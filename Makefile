APP_NAME = solana-bot
ENV_FILE = .env

build:
	docker build -t $(APP_NAME) .

run:
	docker run --cpus=1.0 --rm -it --env-file $(ENV_FILE) --name $(APP_NAME) $(APP_NAME)

start:
	docker build -t $(APP_NAME) .
	docker run --cpus=1.0 -d --env-file $(ENV_FILE) --name $(APP_NAME) $(APP_NAME)

stop:
	docker stop $(APP_NAME) || true

logs:
	docker logs -f $(APP_NAME)

clean:
	docker rm -f $(APP_NAME) || true
	docker rmi $(APP_NAME) || true

exec:
	docker exec -it $(APP_NAME) /bin/bash