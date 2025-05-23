# San Francisco Fire Incidents Data Pipeline

## Project Description

This project implements a containerized ELT (Extract, Load, Transform) data pipeline for San Francisco Fire Incidents. It automates the process of:

1.  **Extracting** recent fire incident data daily from the public SF OpenData API.
2.  **Loading** this raw data into a PostgreSQL data warehouse.
3.  **Transforming** the data using dbt (Data Build Tool) into cleaned, structured, and analytics-ready models. These models support common business intelligence queries, focusing on aggregations by time periods, geographic districts, and fire battalions.

The entire pipeline is orchestrated by Apache Airflow, running within Docker containers managed by Docker Compose. This ensures a reproducible and isolated environment for development and execution. The solution also includes initial data quality tests via dbt and a basic Python script to generate example reports from the transformed data. The `README.md` provides comprehensive setup and operational instructions.

## Key Assumptions for this Project

1.  **Data Source Reliability**: The SF OpenData API is assumed to be consistently available and its schema for fire incidents data to be relatively stable.
2.  **Daily Data Granularity**: The pipeline is designed for daily batch processing, assuming that daily updates are sufficient for the analytical needs.
3.  **Local Development Focus**: The current setup (PostgreSQL as a data warehouse, default credentials) is optimized for a local Dockerized development environment. For production, components like the data warehouse and credential management would need to be scaled and secured appropriately.
4.  **Defined Analytical Scope**: The primary analytical focus is on incidents aggregated by time, district, and battalion, as reflected in the dbt models.
5.  **Sufficient Local Resources**: The user's machine running Docker is assumed to have adequate resources (RAM, CPU) to run the PostgreSQL and Airflow containers.
6.  **Full Refresh of Recent Data**: The extraction process performs a full refresh of the last 30 days of data (for the initial load example), which is assumed manageable for this data source.
7.  **User Responsibility for Security Keys**: It's assumed the user will generate and use their own unique Airflow Fernet key for security, as detailed in the setup instructions.
8.  **Basic Reporting Needs**: The included report generation script serves as a basic example and is not intended as a full-fledged BI reporting solution.

## Architecture

- **Data Source**: San Francisco Open Data Portal (SF OpenData API)
- **Orchestration**: Apache Airflow
- **Data Warehouse**: PostgreSQL (containerized)
- **Transformation**: DBT (Data Build Tool)
- **Containerization**: Docker & Docker Compose

## Key Features

1. **Automated Daily Data Ingestion**: Extracts the latest fire incidents data from SF Open Data API
2. **Optimized Data Models**: DBT models designed for efficient querying by time, district, and battalion
3. **Comprehensive Transformations**: Standardized data with proper typing and cleaning
4. **Automated Pipeline**: Airflow DAG orchestrates the entire ELT process
5. **Data Quality**: DBT tests ensure data integrity
6. **Analytics-Ready**: Pre-built aggregation tables for common business queries

## Setup and Run Instructions

Follow these steps to get the San Francisco Fire Incidents Data Pipeline running on your local machine.

### Prerequisites

*   **Git**: For cloning the repository.
*   **Docker**: Ensure Docker Desktop (or Docker Engine + Docker Compose CLI plugin) is installed and running. Docker will manage the containerized services (PostgreSQL, Airflow).
*   **Sufficient System Resources**: Allocate at least 4GB of RAM to Docker, as Airflow and PostgreSQL can be resource-intensive.

### 1. Clone the Repository

Open your terminal and run the following commands:

```bash
git clone <your-repository-url> # Replace <your-repository-url> with the actual URL of your GitHub repo
cd sf-fire-incidents-pipeline
```

### 2. Configure Environment (Important!)

The project uses an Airflow Fernet key for encrypting connections and variables. The `docker-compose.yml` file contains a placeholder. **You should generate your own unique Fernet key.**

*   **Generate Fernet Key**:
    Run the following Python command in your terminal:
    ```bash
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ```
*   **Update `docker-compose.yml`**:
    Copy the key generated by the command above. Open the `docker-compose.yml` file in the project root, find the `AIRFLOW__CORE__FERNET_KEY` environment variable for the `airflow` service, and replace the placeholder value with your newly generated key.

    Example:
    ```yaml
    # ...
    environment:
      # ...
      AIRFLOW__CORE__FERNET_KEY: 'YOUR_GENERATED_FERNET_KEY_HERE' # Paste your key
      # ...
    ```

### 3. Build and Start Services

This project uses Docker Compose to manage the Airflow and PostgreSQL services.

*   **Build and Run**:
    In your terminal, from the project's root directory (`sf-fire-incidents-pipeline`), run:
    ```bash
    docker-compose up -d --build
    ```
    *   `--build`: This flag ensures that Docker images are built (or rebuilt if they already exist) according to the Dockerfiles, incorporating any changes.
    *   `-d`: Runs the containers in detached mode (in the background).

    This command will:
    1.  Build the custom Airflow image (installing Python dependencies, dbt, etc.).
    2.  Pull the official PostgreSQL image.
    3.  Create and start containers for Airflow (webserver, scheduler) and PostgreSQL.
    4.  The PostgreSQL container will run an initialization script (`docker/postgres/init.sql`) to create the necessary databases (`sf_fire_warehouse`, `airflow`) and users (`dbt_user`, `airflow`).
    5.  The Airflow container will initialize its metadata database and create a default admin user.

*   **Verify Services**:
    After a few minutes (Airflow initialization can take some time), check if the containers are running:
    ```bash
    docker ps
    ```
    You should see `sf_fire_airflow` and `sf_fire_postgres` listed with an "Up" status.

    You can also check the logs to ensure everything started correctly:
    ```bash
    docker-compose logs -f airflow
    ```
    Look for messages indicating the webserver and scheduler have started, and the database initialization is complete. Press `Ctrl+C` to stop following the logs.

### 4. Access Airflow UI

Once the services are running:

*   Open your web browser and navigate to: `http://localhost:8080`
*   Log in with the default Airflow credentials:
    *   **Username**: `admin`
    *   **Password**: `admin`

### 5. Run the ELT Pipeline

The main data pipeline is defined in an Airflow DAG.

1.  In the Airflow UI, find the DAG named `sf_fire_incidents_pipeline`.
2.  If it's paused (default behavior set in `docker-compose.yml`), unpause it by clicking the toggle switch.
3.  Trigger the DAG manually by clicking the "Play" button next to its name.
4.  You can monitor the DAG run's progress in the "Grid" or "Graph" views. Click on individual tasks to see their logs.

The DAG will perform the following main steps:
*   **`extract_and_load_raw_data`**: Extracts data from the SF OpenData API and loads it into the `raw.raw_fire_incidents` table in PostgreSQL.
*   **`run_dbt_models`**: Executes dbt to transform the raw data and create staging views and analytics tables in the `analytics` schema.
*   **`dbt_test`**: Runs dbt tests to ensure data quality.

### 6. Generate Analytics Reports (Optional Manual Step)

The project includes a Python script to generate example reports from the analytics tables. To run this script:

1.  Ensure the ELT pipeline (Step 5) has completed successfully at least once, so the analytics tables exist.
2.  Open a new terminal and run:
    ```bash
    docker exec -it sf_fire_airflow python /opt/airflow/reports/generate_reports.py
    ```
    This command executes the `generate_reports.py` script inside the running `sf_fire_airflow` container.
    *(Note: The output/location of these reports will depend on how `generate_reports.py` is implemented, e.g., printing to console, saving to a file inside the container's `/opt/airflow/reports` directory which is mounted to your local `./reports` directory).*

### 7. Accessing the Data Warehouse (PostgreSQL)

You can connect to the PostgreSQL database directly if needed:

*   **Host**: `localhost`
*   **Port**: `5432`
*   **Database**: `sf_fire_warehouse`
*   **User**: `dbt_user`
*   **Password**: `dbt_password`

Use any SQL client (e.g., DBeaver, pgAdmin, `psql`) with these credentials. The transformed data will be in the `analytics` schema.

You can also use `docker exec` for `psql`:
```bash
docker exec -it sf_fire_postgres psql -U dbt_user -d sf_fire_warehouse
```

## Data Model

### Raw Layer (`raw` schema)
- `raw_fire_incidents`: Raw data from SF Open Data API

### Staging Layer (`staging` models)
- `stg_fire_incidents`: Cleaned and typed fire incidents data

### Mart Layer (`analytics` schema)
- `fire_incidents_by_time`: Aggregated by hour, day, month, year
- `fire_incidents_by_district`: Aggregated by geographic district
- `fire_incidents_by_battalion`: Aggregated by fire battalion

## Sample Queries

### 1. Monthly Incidents by District
```sql
SELECT 
    district,
    month,
    total_incidents,
    total_property_loss
FROM analytics.fire_incidents_by_district
WHERE month >= CURRENT_DATE - INTERVAL '6 months'
ORDER BY district, month;
```

### 2. Peak Hours Analysis
```sql
SELECT 
    incident_hour,
    SUM(total_incidents) as total_incidents
FROM analytics.fire_incidents_by_time
GROUP BY incident_hour
ORDER BY total_incidents DESC;
```

### 3. Battalion Performance
```sql
SELECT 
    battalion,
    AVG(avg_suppression_units) as avg_units,
    SUM(total_incidents) as incidents
FROM analytics.fire_incidents_by_battalion
WHERE month >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY battalion
ORDER BY incidents DESC;
```

## Reports

The project includes automated report generation:

```bash
# Generate analytics reports
docker exec sf_fire_airflow python /opt/airflow/reports/generate_reports.py
```

Generated reports include:
- District analysis charts
- Time-based heatmaps
- Seasonal trend analysis
- Battalion performance comparisons

## Monitoring and Maintenance

### Daily Operations
- Monitor Airflow DAG execution
- Check for data quality issues in DBT logs
- Review error logs if pipeline fails

### Data Quality Checks
DBT includes several tests:
- Not null checks for critical fields
- Referential integrity tests
- Custom business logic validation

### Scaling Considerations
- For production: Replace PostgreSQL with Snowflake/BigQuery
- Add data lineage tracking
- Implement incremental loading for large datasets
- Add monitoring and alerting

## Technical Assumptions

1. **Data Freshness**: Source data is updated daily
2. **Data Volume**: Approximately 50,000 records per month
3. **Business Requirements**: Primary aggregations by time, district, and battalion
4. **Data Retention**: No explicit requirement specified
5. **Performance**: Sub-second query response for aggregated data

## Development Workflow

### Adding New Models

1. Create SQL model in appropriate directory:
   - Staging: `dbt_project/models/staging/`
   - Marts: `dbt_project/models/marts/`

2. Add tests in YAML files
3. Run DBT commands:
```bash
docker exec sf_fire_airflow bash -c "cd /opt/airflow/dbt_project && dbt run --select new_model"
```

### Modifying the Pipeline

1. Update Python scripts in `scripts/`
2. Modify Airflow DAG in `dags/`
3. Restart Airflow:
```bash
docker-compose restart airflow
```

## Troubleshooting

### Common Issues

*   **Container Startup Failures**: Check logs carefully with `docker-compose logs airflow` or `docker-compose logs postgres`.
*   **`pg_config` error during `docker-compose up --build`**: Ensure `libpq-dev` and `git` are in the `apt-get install` line in `docker/airflow/Dockerfile`.
*   **Airflow "permission denied for schema public"**: Ensure the `init.sql` for PostgreSQL correctly grants permissions to the `airflow` user on the `airflow` database and its `public` schema.
*   **DBT Connection Errors**:
    *   Verify `sf_fire_postgres` container is running (`docker ps`).
    *   Check credentials in `dbt_project/profiles.yml` (target `dev`) match those in `docker-compose.yml` for `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and the `postgres` service host.
*   **Module Not Found (e.g., `matplotlib`, `seaborn`)**: Add the missing Python package to `docker/airflow/requirements.txt` and rebuild the image with `docker-compose up -d --build`.
*   **"File not found" for scripts (e.g., `generate_reports.py`)**: Ensure the relevant local directory (e.g., `./reports`) is correctly mounted as a volume in `docker-compose.yml` for the `airflow` service.

### Useful Commands

```bash
# View logs
docker-compose logs -f airflow
docker-compose logs -f postgres

# Connect to PostgreSQL
docker exec -it sf_fire_postgres psql -U dbt_user -d sf_fire_warehouse

# Run DBT manually
docker exec sf_fire_airflow bash -c "cd /opt/airflow/dbt_project && dbt run"

# Reset environment
docker-compose down -v
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test locally
4. Submit a pull request with detailed description

## License

This project is for educational/demonstration purposes.