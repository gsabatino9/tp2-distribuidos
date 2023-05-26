FROM python:3.9.7-slim
RUN pip install --upgrade pip && pip3 install pika

COPY server/joiners/joiner_weather /
COPY protocol /protocol
COPY server/common /server/common
COPY server/joiners/common /server/joiners/common

ENTRYPOINT ["/bin/sh"]
