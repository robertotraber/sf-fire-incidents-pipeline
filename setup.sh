#!/bin/bash

echo "Setting up SF Fire Incidents Data Pipeline..."

# Generate Fernet key for Airflow
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "Generated Fernet key: $FERNET_KEY"

# Update docker-compose.yml with the generated key
sed -i.bak "s/your-fernet-key-here/$FERNET_KEY/g" docker-compose.yml

# Create necessary directories
mkdir -p {dags,scripts,reports,docker/postgres,docker/airflow}

# Set permissions
chmod +x setup.sh

echo "Setup complete! You can now run:"
echo "docker-compose up -d"
echo ""
echo "Access points:"
echo "- Airflow UI: http://localhost:8080 (admin/admin)"
echo "- PostgreSQL: localhost:5432 (dbt_user/dbt_password)"