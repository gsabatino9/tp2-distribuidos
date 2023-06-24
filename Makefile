SHELL := /bin/bash
PWD := $(shell pwd)

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init

default: build

all:

client-image:
	docker build -f ./client/Dockerfile -t "client:latest" .
.PHONY: client-image

testing-image:
	docker build -f ./server/processes_restarter/Dockerfile -t "processes_restarter:latest" .
	docker build -f ./testing/processes_stopper/Dockerfile -t "processes_stopper:latest" .
.PHONY: testing-image

server-image:
	docker build -f ./server/base_image/python-base.Dockerfile -t "rabbitmq-python-server-base:latest" .

	docker build -f ./server/processes_restarter/Dockerfile -t "processes_restarter:latest" .
	docker build -f ./server/receiver/Dockerfile -t "receiver:latest" .
	docker build -f ./server/session_manager/Dockerfile -t "session_manager:latest" .
	
	docker build -f ./server/joiners/joiner_stations/Dockerfile -t "joiner_stations:latest" .
	docker build -f ./server/joiners/joiner_weather/Dockerfile -t "joiner_weather:latest" .
	
	docker build -f ./server/filters/filter_pretoc/Dockerfile -t "filter_pretoc:latest" .
	docker build -f ./server/filters/filter_year/Dockerfile -t "filter_year:latest" .
	docker build -f ./server/filters/filter_distance/Dockerfile -t "filter_distance:latest" .
	
	docker build -f ./server/groupby/start_date/Dockerfile -t "groupby_start_date:latest" .
	docker build -f ./server/groupby/start_station/Dockerfile -t "groupby_start_station:latest" .
	docker build -f ./server/groupby/end_station/Dockerfile -t "groupby_end_station:latest" .
	docker build -f ./server/groupby/all_elements/Dockerfile -t "groupby_all_elements:latest" .
	
	docker build -f ./server/appliers/mean_duration_applier/Dockerfile -t "mean_duration_applier:latest" .
	docker build -f ./server/appliers/double_year_applier/Dockerfile -t "double_year_applier:latest" .
	docker build -f ./server/appliers/mean_distance_applier/Dockerfile -t "mean_distance_applier:latest" .
	
	docker build -f ./server/results_verifier/Dockerfile -t "results_verifier:latest" .
	
	docker build -f ./server/eof_manager/joiners/Dockerfile -t "eof_manager_joiners:latest" .
	docker build -f ./server/eof_manager/filters/Dockerfile -t "eof_manager_filters:latest" .
	docker build -f ./server/eof_manager/groupby/Dockerfile -t "eof_manager_groupby:latest" .
	docker build -f ./server/eof_manager/appliers/Dockerfile -t "eof_manager_appliers:latest" .
	docker build -f ./server/eof_manager/results_verifier/Dockerfile -t "eof_manager_query_results:latest" .

.PHONY: server-image

server-up: server-image
	docker compose -f docker-compose-server.yaml up -d --build
.PHONY: server-up

server-down:
	docker compose -f docker-compose-server.yaml stop -t 1
	docker compose -f docker-compose-server.yaml down
.PHONY: server-down

server-logs:
	docker compose -f docker-compose-server.yaml logs -f
.PHONY: server-logs

server-run: server-image
	python3 create_docker_compose.py
	docker compose -f docker-compose-server.yaml up -d --build
	docker compose -f docker-compose-server.yaml logs -f
.PHONY: server-run

client-run: client-image
	docker compose -f docker-compose-client.yaml up -d --build
	docker compose -f docker-compose-client.yaml logs -f
.PHONY: client-run

client-down:
	docker compose -f docker-compose-client.yaml stop -t 1
	docker compose -f docker-compose-client.yaml down
.PHONY: client-down


testing-run: testing-image
	python3 testing/create_docker_compose.py
	docker compose -f ./testing/docker-compose-testing-restarters.yaml up -d --build
	docker compose -f ./testing/docker-compose-testing-restarters.yaml logs -f
.PHONY: testing-run

testing-down:
	docker compose -f ./testing/docker-compose-testing-restarters.yaml stop -t 15
	docker compose -f ./testing/docker-compose-testing-restarters.yaml down
.PHONY: testing-down
