import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os

# Database configuration
DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'sf_fire_warehouse',
    'user': 'dbt_user',
    'password': 'dbt_password'
}

def create_db_connection():
    """Create database connection"""
    engine = create_engine(
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
        f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return engine

def generate_district_report():
    """Generate simple district analysis report"""
    engine = create_db_connection()
    
    query = """
    SELECT 
        district,
        SUM(total_incidents) as total_incidents,
        SUM(total_property_loss) as total_loss
    FROM analytics.fire_incidents_by_district
    WHERE month >= CURRENT_DATE - INTERVAL '1 year'
      AND district IS NOT NULL
    GROUP BY district
    ORDER BY total_incidents DESC
    LIMIT 10
    """
    
    df = pd.read_sql(query, engine)
    
    # Create simple bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df['district'], df['total_incidents'])
    ax.set_xlabel('District')
    ax.set_ylabel('Number of Incidents')
    ax.set_title('Fire Incidents by District (Last 12 Months)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reports/district_incidents.png')
    plt.close()
    
    # Property loss chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df['district'], df['total_loss'] / 1000000)  # Convert to millions
    ax.set_xlabel('District')
    ax.set_ylabel('Property Loss ($ Millions)')
    ax.set_title('Property Loss by District (Last 12 Months)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reports/district_property_loss.png')
    plt.close()

def generate_time_report():
    """Generate simple time analysis"""
    engine = create_db_connection()
    
    # Hour pattern
    query = """
    SELECT 
        incident_hour,
        SUM(total_incidents) as total_incidents
    FROM analytics.fire_incidents_by_time
    WHERE incident_date_day >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY incident_hour
    ORDER BY incident_hour
    """
    
    df = pd.read_sql(query, engine)
    
    # Create hour pattern chart
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(df['incident_hour'], df['total_incidents'])
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Number of Incidents')
    ax.set_title('Fire Incidents by Hour of Day (Last 6 Months)')
    ax.set_xticks(range(0, 24))
    plt.tight_layout()
    plt.savefig('reports/incidents_by_hour.png')
    plt.close()
    
    # Day of week pattern
    query_dow = """
    SELECT 
        day_of_week,
        AVG(total_incidents) as avg_incidents
    FROM analytics.fire_incidents_by_time
    WHERE incident_date_day >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY day_of_week
    ORDER BY day_of_week
    """
    
    df_dow = pd.read_sql(query_dow, engine)
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(day_names, df_dow['avg_incidents'])
    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Average Daily Incidents')
    ax.set_title('Average Fire Incidents by Day of Week')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reports/incidents_by_day.png')
    plt.close()

def generate_battalion_report():
    """Generate simple battalion analysis"""
    engine = create_db_connection()
    
    query = """
    SELECT 
        battalion,
        SUM(total_incidents) as total_incidents,
        AVG(avg_suppression_units) as avg_units,
        AVG(avg_suppression_personnel) as avg_personnel
    FROM analytics.fire_incidents_by_battalion
    WHERE month >= CURRENT_DATE - INTERVAL '6 months'
      AND battalion IS NOT NULL
    GROUP BY battalion
    ORDER BY total_incidents DESC
    LIMIT 10
    """
    
    df = pd.read_sql(query, engine)
    
    # Incidents by battalion
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df['battalion'], df['total_incidents'])
    ax.set_xlabel('Battalion')
    ax.set_ylabel('Number of Incidents')
    ax.set_title('Fire Incidents by Battalion (Last 6 Months)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reports/battalion_incidents.png')
    plt.close()
    
    # Resource utilization
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['avg_units'], df['avg_personnel'], s=df['total_incidents'])
    ax.set_xlabel('Average Suppression Units')
    ax.set_ylabel('Average Personnel')
    ax.set_title('Resource Utilization by Battalion\n(Bubble size = Total Incidents)')
    plt.tight_layout()
    plt.savefig('reports/battalion_resources.png')
    plt.close()

def main():
    """Generate all basic reports"""
    print("Generating SF Fire Incidents Reports...")
    
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    try:
        print("1. Generating district reports...")
        generate_district_report()
        
        print("2. Generating time analysis...")
        generate_time_report()
        
        print("3. Generating battalion reports...")
        generate_battalion_report()
        
        print("Reports generated successfully!")
        print("Check the 'reports' directory for PNG files.")
        
    except Exception as e:
        print(f"Error generating reports: {str(e)}")
        raise

if __name__ == "__main__":
    main()