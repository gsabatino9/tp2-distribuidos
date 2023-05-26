FROM python:3.9.7-slim
RUN pip install --upgrade pip && pip3 install pika

COPY server/groupby/start_date /
COPY protocol /protocol
COPY server/groupby/common /server/groupby/common
COPY server/common /server/common

ENTRYPOINT ["/bin/sh"]
