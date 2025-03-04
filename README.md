# Yelp Reviews Data Pipeline

![data-pipeline-diagram](https://github.com/user-attachments/assets/3e87ffd3-ac9c-4161-9487-ce5651e7b80d)

## Project Overview
This data engineering project creates an end-to-end pipeline for extracting, transforming, and analyzing Yelp restaurant reviews using modern data infrastructure technologies.

## Technology Stack
- **Airflow**: Orchestration of data pipeline
- **Astronomer**: Workflow management and deployment
- **PostgreSQL**: Data storage and persistence
- **Tableau**: Data visualization and insights generation
- **Poetry**: Dependency management
- **Docker**: Containerization

## Airflow Orchestration:
  - Manages complex workflow dependencies
  - Provides visual representation of pipeline tasks
  - Implements retry mechanisms and error handling
  - Supports automated scheduling and event-driven extraction of data which is essential in automated pipelines
  - Enables monitoring and logging of pipeline execution

The combination of airflow with docker allows for a modular, flexible approach to data pipeline management, where each component of the data workflow can be independently developed, tested, and deployed.

## Data Pipeline Architecture
1. **Data Extraction**: 
   - Uses **SerpAPI** to fetch Yelp reviews
   - Currently implemented to extract historical and live data from a single restaurant

2. **Data Transformation**:
   - Utilizes **Pandas** for data preprocessing
   - Extracts multiple feature dimensions:
     - Temporal features (review hour, day, month, year)
     - Geographic features (city, state, local/non-local reviewers)
     - Engagement metrics (photo count, feedback)
     - Content analysis (review length, owner responses)

3. **Data Loading**:
   - Loads transformed data into **PostgreSQL** database
   - Implements upsert strategy with conflict resolution
   - Stores rich metadata about each review

## Tableau Data Visualization Integration
**Tableau** connects directly to the **PostgreSQL** database using a live connection:

- **Database Driver**: PostgreSQL JDBC Driver
- **Connection Type**: Live Connection
- **Benefits**:
  - Real-time data updates
  - Direct query capabilities
  - Minimal data duplication
  - Performance optimization

## Tableau Visualization Insights
The project generates five key visualizations:

1. **Review Hour vs Review Count**
   - Identifies peak hours for customer reviews
   - Helps understand customer engagement timing

2. **Review Count vs Rating**
   - Analyzes rating distribution
   - Provides insight into overall customer satisfaction

3. **Review Count vs State**
   - Maps geographical review distribution
   - Tracks inter-state customer attraction
   - Identifies primary customer regions

4. **Local Reviewers vs Rating**
   - Compares local resident reviews across different ratings
   - Helps understand local customer perception

5. **User Interaction on Reviews**
   - Tracks feedback and engagement metrics
   - Analyzes response patterns

## Project Setup and Execution

### Prerequisites
- **Docker**
- **Poetry**
- **Astronomer CLI**
- **PostgreSQL** connection
- **SerpAPI** credentials

### Installation Steps
1. Clone the repository
```bash
git clone https://github.com/shahJenil/Automated-Data-Pipeline.git
cd Automated Data Pipeline
```

2. Install dependencies
```bash
poetry add $(cat requirementsyelp.txt)
```

3. Set up environment variables
- Configure **PostgreSQL** connection
- Add **SerpAPI** credentials
- Set up Airflow connections

4. Start local development environment
```bash
poetry shell
astro dev start
```

## Airflow DAG Configuration
- **Schedule**: Hourly runs
- **Catchup**: Disabled
- **Tasks**: 
  1. Extract Yelp data
  2. Transform review data
  3. Load to PostgreSQL

## Monitoring and Logging
- Tracks potential data anomalies
- Logs negative response times
- Provides comprehensive error handling
