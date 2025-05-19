-- Initialize database schemas and permissions

-- Create airflow database and user for Airflow metadata
CREATE DATABASE airflow;
CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

\c airflow;
GRANT USAGE, CREATE ON SCHEMA public TO airflow;

-- Create schemas in the main warehouse database
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions to dbt_user
GRANT ALL PRIVILEGES ON SCHEMA public TO dbt_user;
GRANT ALL PRIVILEGES ON SCHEMA raw TO dbt_user;
GRANT ALL PRIVILEGES ON SCHEMA staging TO dbt_user;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO dbt_user;

-- Set search_path for dbt_user
ALTER USER dbt_user SET search_path TO analytics,staging,raw,public;