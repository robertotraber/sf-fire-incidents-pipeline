FROM apache/airflow:2.7.1-python3.9

USER root
RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install required Python packages
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Install dbt
RUN pip install dbt-postgres dbt-core==1.5.4