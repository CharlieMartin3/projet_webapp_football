FROM apache/airflow:2.6.3

USER root

# Installer les bibliothèques système nécessaires (pour psycopg2 notamment)
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    apt-get clean

USER airflow

# Installer les bibliothèques Python nécessaires
RUN pip install --no-cache-dir \
    pandas \
    sqlalchemy \
    psycopg2-binary