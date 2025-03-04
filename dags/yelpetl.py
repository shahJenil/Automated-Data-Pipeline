from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from airflow.utils.dates import days_ago
import pandas as pd
import numpy as np
from datetime import datetime
import json

POSTGRES_CONN_ID = "postgres-default"
API_CONN_ID = "serpapi-yelp"

default_args = {"owner": "airflow", "start_date": days_ago(1)}

with DAG(
    dag_id="yelp_weather_api",
    default_args=default_args,
    schedule_interval="@hourly",
    catchup=False,
) as dag:

    @task()
    def extract_yelp_data():
        http_hook = HttpHook(http_conn_id=API_CONN_ID, method="GET")

        endpoint = f"/search.json?engine=yelp_reviews&place_id=-4ofMtrD7pSpZIX5pnDkig&hl=en&api_key=613c857ef6a6138c3a573b9a0e7e0f7b6a13a0a7ea08c16036fd458b6b21e2fe&num=49"

        response = http_hook.run(endpoint=endpoint)
        return response.json()

    @task()
    def transform_review_data(raw_data):
        data = raw_data.get("reviews", [])
        df = pd.json_normalize(data, sep="_")

        # Temporal Transformations
        def transform_temporal(df):
            df["review_datetime"] = pd.to_datetime(
                df["date"], format="%Y-%m-%dT%H:%M:%SZ", utc=True
            )
            df["review_hour"] = df["review_datetime"].dt.hour
            df["review_day"] = df["review_datetime"].dt.day_name()
            df["review_month"] = df["review_datetime"].dt.month
            df["review_year"] = df["review_datetime"].dt.year

            # Handle owner replies safely
            def get_reply_date(replies):
                if isinstance(replies, list) and replies:
                    return replies[0].get("date")
                return None

            df["owner_replies_date"] = df["owner_replies"].apply(get_reply_date)
            df["owner_response_datetime"] = pd.to_datetime(
                df["owner_replies_date"],
                format="%Y-%m-%dT%H:%M:%SZ",
                utc=True,
                errors="coerce",
            )

            df["response_time_days"] = np.where(
                df["owner_response_datetime"].notna(),
                (
                    df["owner_response_datetime"] - df["review_datetime"]
                ).dt.total_seconds()
                / (24 * 3600),
                None,
            )

            negative_responses = df[df["response_time_days"] < 0]
            if len(negative_responses) > 0:
                print("Found negative response times:")
                for _, row in negative_responses.iterrows():
                    print(f"Review ID: {row.name}")
                    print(f"Review datetime: {row['review_datetime']}")
                    print(f"Response datetime: {row['owner_response_datetime']}")
                    print(f"Response time (days): {row['response_time_days']}")
                    print("---")

            return df

        # Geographic Transformations
        def transform_geographic(df):
            location_parts = df["user_address"].str.extract(
                r"(?:.*, )?(?P<city>[^,]+),\s*(?P<state>[A-Z]{2})$"
            )

            df = pd.concat([df, location_parts], axis=1)
            df["is_local"] = df["city"].str.contains("Austin", case=False, na=False)

            return df

        # Engagement Transformations
        def transform_engagement(df):
            df["has_photos"] = df["photos"].notna()
            df["photo_count"] = df["photos"].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            )
            df["total_feedback"] = (
                df["feedback_useful"].fillna(0)
                + df["feedback_funny"].fillna(0)
                + df["feedback_cool"].fillna(0)
            )

            return df

        # Content Transformations
        def transform_content(df):
            df["review_length"] = df["comment_text"].str.len()
            df["has_owner_response"] = df["owner_replies"].notna()

            def get_reply_comment(replies):
                if isinstance(replies, list) and replies:
                    return replies[0].get("comment", "")
                return None

            df["owner_replies_comment"] = df["owner_replies"].apply(get_reply_comment)
            df["owner_response_length"] = df["owner_replies_comment"].str.len()

            return df

        # Apply all transformations
        df = transform_temporal(df)
        df = transform_geographic(df)
        df = transform_engagement(df)
        df = transform_content(df)

        # Convert to list of dictionaries for easy database insertion
        records = []
        for idx, row in df.iterrows():
            record = {
                "review_id": int(idx),
                "review_datetime": row["review_datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                "review_hour": int(row["review_hour"]),
                "review_day": str(row["review_day"]),
                "review_month": int(row["review_month"]),
                "review_year": int(row["review_year"]),
                "owner_response_datetime": row["owner_response_datetime"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if pd.notna(row["owner_response_datetime"])
                else None,
                "response_time_days": float(row["response_time_days"])
                if pd.notna(row["response_time_days"])
                else None,
                "city": str(row["city"]) if pd.notna(row["city"]) else None,
                "state": str(row["state"]) if pd.notna(row["state"]) else None,
                "is_local": bool(row["is_local"]),
                "has_photos": bool(row["has_photos"]),
                "photo_count": int(row["photo_count"]),
                "total_feedback": int(row["total_feedback"]),
                "rating": int(row["rating"]),
                "review_text": str(row["comment_text"]),
                "review_length": int(row["review_length"]),
                "has_owner_response": bool(row["has_owner_response"]),
                "owner_response": str(row["owner_replies_comment"])
                if pd.notna(row["owner_replies_comment"])
                else None,
                "owner_response_length": int(row["owner_response_length"])
                if pd.notna(row["owner_response_length"])
                else 0,
            }
            records.append(record)

        return records

    @task()
    def load_review_data(transformed_data):
        if not transformed_data:
            return

        pg_hook = PostgresHook(POSTGRES_CONN_ID)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews(
                review_id INTEGER PRIMARY KEY,
                review_datetime TIMESTAMP WITHOUT TIME ZONE,
                review_hour SMALLINT,
                review_day VARCHAR(10),
                review_month SMALLINT, 
                review_year SMALLINT,
                owner_response_datetime TIMESTAMP WITHOUT TIME ZONE,
                response_time_days FLOAT,
                city VARCHAR(50),
                state VARCHAR(2),
                is_local BOOLEAN,
                has_photos BOOLEAN,
                photo_count SMALLINT,
                total_feedback INTEGER,
                rating SMALLINT,
                review_text TEXT,
                review_length INTEGER,
                has_owner_response BOOLEAN,
                owner_response TEXT,
                owner_response_length INTEGER,
                timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """
        )

        # Insert each record
        insert_query = """
            INSERT INTO reviews (
                review_id, review_datetime, review_hour, review_day, review_month,
                review_year, owner_response_datetime, response_time_days, city,
                state, is_local, has_photos, photo_count, total_feedback,
                rating, review_text, review_length, has_owner_response,
                owner_response, owner_response_length
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (review_id) DO UPDATE SET
                timestamp = CURRENT_TIMESTAMP;
        """

        for record in transformed_data:
            cursor.execute(
                insert_query,
                (
                    record["review_id"],
                    record["review_datetime"],
                    record["review_hour"],
                    record["review_day"],
                    record["review_month"],
                    record["review_year"],
                    record["owner_response_datetime"],
                    record["response_time_days"],
                    record["city"],
                    record["state"],
                    record["is_local"],
                    record["has_photos"],
                    record["photo_count"],
                    record["total_feedback"],
                    record["rating"],
                    record["review_text"],
                    record["review_length"],
                    record["has_owner_response"],
                    record["owner_response"],
                    record["owner_response_length"],
                ),
            )

        conn.commit()
        cursor.close()
        conn.close()

    # Define the DAG structure
    review_data = extract_yelp_data()
    transformed_data = transform_review_data(review_data)
    load_review_data(transformed_data)
