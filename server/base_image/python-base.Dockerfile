FROM python:3.9.7-slim
RUN pip install --upgrade pip && pip3 install pika
COPY server/common /server/common
COPY protocol /protocol