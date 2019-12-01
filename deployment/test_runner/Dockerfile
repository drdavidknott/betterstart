FROM docker.io/library/python:latest
COPY requirements.txt /
RUN pip install -r requirements.txt
RUN curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64
RUN chmod +x cloud_sql_proxy
