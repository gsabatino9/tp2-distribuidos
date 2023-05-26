FROM python:3.9.7-slim
RUN pip install --upgrade pip && pip3 install pika

COPY server/appliers/mean_duration_applier /
COPY server/appliers/common /server/appliers/common
COPY server/common /server/common

ENTRYPOINT ["/bin/sh"]
