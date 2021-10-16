FROM docker.io/library/python:3.7
COPY requirements.txt /
RUN pip install -r requirements.txt
RUN curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64
RUN chmod +x cloud_sql_proxy
