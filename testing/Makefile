docker-image:
	docker build -f ../server/processes-restarter/Dockerfile -t "processes-restarter:latest" .
# 	docker build -f ../server/keep-alive/Dockerfile -t "keep-alive:latest" .
	# Execute this command from time to time to clean up intermediate stages generated 
	# during client build (your hard drive will like this :) ). Don't left uncommented if you 
	# want to avoid rebuilding client image every time the docker-compose-up command 
	# is executed, even when client code has not changed
	# docker rmi `docker images --filter label=intermediateStageToBeDeleted=true -q`
.PHONY: docker-image

docker-compose-up: docker-image
	docker compose -f docker-compose-testing-restarters.yaml up -d --build
.PHONY: docker-compose-up-2

docker-compose-down:
	docker compose -f docker-compose-testing-restarters.yaml stop -t 1
	docker compose -f docker-compose-testing-restarters.yaml down
.PHONY: docker-compose-down-2

docker-compose-logs:
	docker compose -f docker-compose-testing-restarters.yaml logs -f
.PHONY: docker-compose-logs-2
