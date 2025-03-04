![data-pipeline-diagram](https://github.com/user-attachments/assets/41fbb7ea-771b-4aef-b5f8-5901ca7ec112)# Yelp Reviews Data Pipeline

![Uploading<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500">
  <!-- Background -->
  <rect width="100%" height="100%" fill="#f0f0f0"/>
  
  <!-- Title -->
  <text x="400" y="40" text-anchor="middle" font-size="20" font-weight="bold" fill="#333">
    Yelp Reviews Data Pipeline Architecture
  </text>
  
  <!-- Components -->
  <!-- SerpAPI -->
  <rect x="50" y="100" width="150" height="80" fill="#4CAF50" rx="10" ry="10"/>
  <text x="125" y="140" text-anchor="middle" fill="white" font-weight="bold">SerpAPI</text>
  <text x="125" y="160" text-anchor="middle" fill="white" font-size="10">Data Extraction</text>
  
  <!-- Airflow -->
  <rect x="300" y="100" width="200" height="80" fill="#2196F3" rx="10" ry="10"/>
  <text x="400" y="140" text-anchor="middle" fill="white" font-weight="bold">Apache Airflow</text>
  <text x="400" y="160" text-anchor="middle" fill="white" font-size="10">Workflow Orchestration</text>
  
  <!-- Pandas -->
  <rect x="300" y="250" width="200" height="80" fill="#FF9800" rx="10" ry="10"/>
  <text x="400" y="290" text-anchor="middle" fill="white" font-weight="bold">Pandas</text>
  <text x="400" y="310" text-anchor="middle" fill="white" font-size="10">Data Transformation</text>
  
  <!-- PostgreSQL -->
  <rect x="600" y="250" width="150" height="80" fill="#9C27B0" rx="10" ry="10"/>
  <text x="675" y="290" text-anchor="middle" fill="white" font-weight="bold">PostgreSQL</text>
  <text x="675" y="310" text-anchor="middle" fill="white" font-size="10">Data Storage</text>
  
  <!-- Tableau -->
  <rect x="600" y="400" width="150" height="80" fill="#673AB7" rx="10" ry="10"/>
  <text x="675" y="440" text-anchor="middle" fill="white" font-weight="bold">Tableau</text>
  <text x="675" y="460" text-anchor="middle" fill="white" font-size="10">Data Visualization</text>
  
  <!-- Docker -->
  <rect x="50" y="250" width="150" height="80" fill="#795548" rx="10" ry="10"/>
  <text x="125" y="290" text-anchor="middle" fill="white" font-weight="bold">Docker</text>
  <text x="125" y="310" text-anchor="middle" fill="white" font-size="10">Containerization</text>
  
  <!-- Arrows -->
  <!-- SerpAPI to Airflow -->
  <line x1="200" y1="140" x2="300" y2="140" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <!-- Airflow to Pandas -->
  <line x1="400" y1="180" x2="400" y2="250" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <!-- Pandas to PostgreSQL -->
  <line x1="500" y1="290" x2="600" y2="290" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <!-- PostgreSQL to Tableau -->
  <line x1="675" y1="330" x2="675" y2="400" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <!-- Docker surrounding other components -->
  <rect x="30" y="80" width="740" height="420" fill="none" stroke="#795548" stroke-dasharray="5,5" rx="15" ry="15"/>
  <text x="400" y="480" text-anchor="middle" fill="#795548" font-size="12">Docker Containerization Environment</text>
  
  <!-- Arrowhead marker definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>
    </marker>
  </defs>
</svg>
 data-pipeline-diagram.svg…]()


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
