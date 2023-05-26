FROM python:3.9.7-slim
RUN pip install --upgrade pip && pip3 install pika

COPY server/filters/filter_pretoc /
COPY server/filters/common /server/filters/common
COPY protocol /protocol
COPY server/common /server/common

ENTRYPOINT ["/bin/sh"]
