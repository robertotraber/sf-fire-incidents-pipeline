import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import logging
from datetime import datetime, timedelta
import requests
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_sf_fire_data():
    """
    Extract San Francisco fire incidents data from the open data portal
    """
    # SF Open Data API endpoint for fire incidents
    url = "https://data.sfgov.org/resource/wr8u-xric.json"
    
    # Parameters to get recent data (last 30 days for initial load)
    params = {
        "$where": f"incident_date >= '{(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}'",
        "$limit": 50000,
        "$order": "incident_date DESC"
    }
    
    try:
        logger.info(f"Extracting data from SF Open Data portal: {url}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data)
        
        # Log DataFrame info using a helper to capture print output
        from io import StringIO
        buffer = StringIO()
        df.info(buf=buffer)
        logger.info(f"DataFrame info before type conversion:\n{buffer.getvalue()}")
        
        # Convert 'point' column to JSON string if it exists
        if 'point' in df.columns:
            logger.info("Converting 'point' column to JSON strings.")
            df['point'] = df['point'].apply(lambda x: json.dumps(x) if x is not None and isinstance(x, dict) else x)
        else:
            logger.info("'point' column not found in DataFrame.")
        
        logger.info(f"Extracted {len(df)} records")
        return df
        
    except Exception as e:
        logger.error(f"Error extracting data: {str(e)}")
        raise

def load_to_warehouse(df, table_name="raw_fire_incidents"):
    """
    Load data to PostgreSQL warehouse
    """
    # Database connection parameters
    DB_CONFIG = {
        'host': 'postgres',
        'port': 5432,
        'database': 'sf_fire_warehouse',
        'user': 'dbt_user',
        'password': 'dbt_password'
    }
    
    try:
        # Create SQLAlchemy engine
        engine = create_engine(
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
            f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        
        # Create raw schema if it doesn't exist
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        
        # Load data to warehouse
        df.to_sql(
            table_name,
            engine,
            schema='raw',
            if_exists='replace',  # For full refresh
            index=False,
            method='multi'
        )
        
        logger.info(f"Successfully loaded {len(df)} records to {table_name}")
        
    except Exception as e:
        logger.error(f"Error loading data to warehouse: {str(e)}")
        raise

def main():
    """
    Main ETL function
    """
    logger.info("Starting SF Fire Incidents ETL process")
    
    # Extract
    df = extract_sf_fire_data()
    
    # Load
    load_to_warehouse(df)
    
    logger.info("ETL process completed successfully")

if __name__ == "__main__":
    main()