INIT_DOCKER = """version: '3'
services:
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: rabbitmq
    ports:
      - 15672:15672
      - 5672:5672
    networks:      
      - testing_net
    healthcheck:        
      test: [ "CMD", "nc", "-z", "localhost", "5672" ]
      interval: 10s        
      timeout: 5s        
      retries: 10
    logging:
      driver: none

  <ACCEPTER>

  <PROCESS_RESTARTER>

  <JOINER_STATIONS>
  <JOINER_WEATHER>

  <FILTER_PRETOC>
  <FILTER_YEAR>
  <FILTER_DISTANCE>

  <GROUPBY_QUERY1>
  <GROUPBY_QUERY2>
  <GROUPBY_QUERY3>
  <GROUPBY_QUERY4>

  <APPLIER_QUERY1>
  <APPLIER_QUERY2>
  <APPLIER_QUERY3>
  <APPLIER_QUERY4>

  <RESULTS_VERIFIER>
    
  <EM_JOINERS>
  <EM_FILTERS>
  <EM_GROUPBY>
  <EM_APPLIERS>
  <EM_RESULTS>

  <SESSION_MANAGER>

networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24      
"""

ACCEPTER = """
  accepter_{}:
    container_name: accepter_{}
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=accepter_{}
      - PORT={}
      - NAME_STATIONS_QUEUE={}
      - NAME_WEATHER_QUEUE={}
      - NAME_TRIPS_QUEUES={}
      - NAME_EM_QUEUE={}
      - NAME_STATUS_QUEUE={}
      - NAME_SM_QUEUE={}
      - NAME_RECV_QUEUE={}
      - AMOUNT_QUERIES=3
    image: accepter:latest
    ports:
      - {}:{}
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

JOINER_STATIONS = """
  joiner_stations:
    container_name: joiner_stations
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_TRIPS_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_NEXT_STAGE_QUEUE={}
    image: joiner_stations:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

JOINER_WEATHER = """
  joiner_weather:
    container_name: joiner_weather
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_TRIPS_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_NEXT_STAGE_QUEUE={}
    image: joiner_weather:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

FILTER_PRETOC = """
  filter_pretoc_{}:
    container_name: filter_pretoc_{}
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_EXCHANGE={}
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
      - ID_QUERY=1
    image: filter_pretoc:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

FILTER_YEAR = """
  filter_year_{}:
    container_name: filter_year_{}
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_EXCHANGE={}
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
      - ID_QUERY=2
    image: filter_year:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

FILTER_DISTANCE = """
  filter_distance_{}:
    container_name: filter_distance_{}
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_EXCHANGE={}
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
      - ID_QUERY=3
    image: filter_distance:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

GROUPBY_QUERY1 = """
  groupby_start_date:
    container_name: groupby_start_date
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
      - CHUNK_SIZE=100
    image: groupby_start_date:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

GROUPBY_QUERY2 = """
  groupby_start_station:
    container_name: groupby_start_station
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
      - CHUNK_SIZE=100
    image: groupby_start_station:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

GROUPBY_QUERY3 = """
  groupby_end_station:
    container_name: groupby_end_station
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
      - CHUNK_SIZE=100
    image: groupby_end_station:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

GROUPBY_QUERY4 = """
  groupby_all_elements:
    container_name: groupby_all_elements
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
      - ID_QUERY=4
      - CHUNK_SIZE=100
    image: groupby_all_elements:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

APPLIER_QUERY1 = """
  mean_duration_applier_1_{}:
    container_name: mean_duration_applier_1_{}
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
      - ID_QUERY=1
    image: mean_duration_applier:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

APPLIER_QUERY2 = """
  double_year_applier_{}:
    container_name: double_year_applier_{}
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
    image: double_year_applier:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

APPLIER_QUERY3 = """
  mean_distance_applier_{}:
    container_name: mean_distance_applier_{}
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
    image: mean_distance_applier:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

APPLIER_QUERY4 = """
  mean_duration_applier_4_{}:
    container_name: mean_duration_applier_4_{}
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SEND_QUEUE={}
      - ID_QUERY=4
    image: mean_duration_applier:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

EM_FILTERS = """
  eof_manager_filters:
    container_name: eof_manager_filters
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_FILTERS_QUEUE={}
      - NAME_SEND_QUEUE={}
      - NAME_STATUS_QUEUE={}
      - SIZE_WORKERS={}
    image: eof_manager_filters:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

EM_JOINERS = """
  eof_manager_joiners:
    container_name: eof_manager_joiners
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_SEND_QUEUE={}
      - NAME_STATIONS_QUEUE={}
      - NAME_WEATHER_QUEUE={}
      - NAME_JOIN_STATIONS_QUEUE={}
      - NAME_JOIN_WEATHER_QUEUE={}
      - NAME_STATUS_QUEUE={}
    image: eof_manager_joiners:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

EM_GROUPBY = """
  eof_manager_groupby:
    container_name: eof_manager_groupby
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_GROUPBY_QUEUE={}
      - NAME_SEND_QUEUE={}
      - NAME_STATUS_QUEUE={}
    image: eof_manager_groupby:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

EM_APPLIERS = """
  eof_manager_appliers:
    container_name: eof_manager_appliers
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_APPLIERS_QUEUES={}
      - NAME_SEND_QUEUE={}
      - NAME_STATUS_QUEUE={}
      - SIZE_WORKERS={}
    image: eof_manager_appliers:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

EM_RESULTS = """
  eof_manager_query_results:
    container_name: eof_manager_query_results
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_VERIFIER_QUEUE={}
      - NAME_STATUS_QUEUE={}
      - SIZE_QUERIES=4
    image: eof_manager_query_results:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

RESULTS_VERIFIER = """
  results_verifier:
    container_name: results_verifier
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - NAME_RECV_QUEUE={}
      - NAME_EM_QUEUE={}
      - NAME_SM_QUEUE={}
      - AMOUNT_QUERIES=4
      - HOST=results_verifier
      - PORT=13000
    ports:
      - 13000:13000
    image: results_verifier:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""


SESSION_MANAGER = """
  session_manager:
    container_name: session_manager
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - MAX_CLIENTS={}
      - NAME_RECV_QUEUE={}
      - NAME_SEND_QUEUE={}
      - NAME_END_SESSION_QUEUE={}
    image: session_manager:latest
    networks:      
      - testing_net
    depends_on:
      rabbitmq:
        condition: service_healthy
"""

INIT_CLIENT = """
version: '3'
services:
  <CLIENT>
networks:
    testing_net:
      name: tp2-distribuidos_testing_net
      external: true
"""

CLIENT = """
  client_{}:
    container_name: client_{}
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - ADDRESSES=[('accepter_1', 12345), ('accepter_2', 12346)]
      - HOST_CONSULT=results_verifier
      - PORT_CONSULT=13000
      - CHUNK_SIZE=100
      - MAX_RETRIES=50
      - SUSCRIPTIONS=[1,2,3,4]
      - FILE_PATH=data/
    image: client:latest
    networks:      
      - testing_net
    volumes:
    - ./client/results:/results
    - ./data/client_{}:/data
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
