FROM python:3.9.7-slim
RUN pip install docker

COPY server/processes_restarter /
COPY server/common /common


ENTRYPOINT ["/bin/sh"]
