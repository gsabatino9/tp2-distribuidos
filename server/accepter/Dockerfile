FROM python:3.9.7-slim
RUN pip install --upgrade pip && pip3 install pika

COPY server/accepter /
COPY protocol /protocol
COPY server/common /server/common

ENTRYPOINT ["/bin/sh"]
