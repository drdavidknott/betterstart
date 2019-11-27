FROM docker.io/library/python:latest
COPY requirements.txt /
RUN pip install -r requirements.txt
