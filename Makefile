# Подключение окружения проекта
# include .path.to.your.file.if.exists
INDEX ?= neuro-fastapi

# Создание образов, контейнеров и их запуск
install:
	@$(MAKE) -s down
	@$(MAKE) -s docker-build
	@$(MAKE) -s up

# Сборка контейнеров
build: docker-build
# Перезапуск контейнеров
restart: down up
# Запуск контейнеров
up: docker-up
# Удаление контейнеров
down: docker-down

# Просмотр запущенных контейнеров
ps:
	@docker ps
	
# Запуск контейнеров
docker-up:
	@docker-compose -p ${INDEX} up -d
# Удаление контейнеров
docker-down:
	@docker-compose -p ${INDEX} down --remove-orphans
# Создание образов для контейнеров
docker-build: \
	docker-build-fastapi
	
# Образ для fastapi
docker-build-fastapi:
	@docker-compose -p ${INDEX} build python
	
# Работа с python контейнером
python:
	@docker exec -it python /bin/sh