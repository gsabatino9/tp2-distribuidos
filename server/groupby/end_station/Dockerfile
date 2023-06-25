FROM rabbitmq-python-server-base:latest
RUN pip install haversine

COPY server/groupby/end_station /
COPY server/groupby/common /server/groupby/common

ENTRYPOINT ["/bin/sh"]
