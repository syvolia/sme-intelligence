FROM apache/spark:3.5.1-python3

USER root

RUN curl -fsSL -o /opt/spark/jars/postgresql-42.7.3.jar \
    https://jdbc.postgresql.org/download/postgresql-42.7.3.jar

USER spark