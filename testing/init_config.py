INIT_DOCKER = """version: '3.9'
name: tp2
services:
  <PROCESS_RESTARTER>  

  <PROCESS_STOPPER>

networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

PROCESS_RESTARTER = """
  processes-restarter-{}:
    container_name: processes-restarter-{}
    image: processes_restarter:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=INFO
      - ID_ELECTION={}
      - N_PROCESS_ELECTION={}
      - CONTAINERS_KEEP_ALIVE={}
      - CONTAINER_RESTARTER_NAME=processes-restarter-
      - NETWORK_PROBLEMS={}
      - BASE_IP_ADDRESS={}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      testing_net:
        ipv4_address: {}
"""

PROCESS_STOPPER = """
  processes-stopper:
    container_name: processes-stopper
    image: processes_stopper:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=INFO
      - CONTAINERS_TO_STOP={}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - testing_net
"""