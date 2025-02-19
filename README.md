<h1 align="center">
    Hi there, We're neuro App!
    <img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" height="32"/>
</h1>

## This is a repository dedicated to the Python module of the "Neuro App" project

### Look what we have!

- [Installing](#installing)

## Installing 

To run fastapi on a local machine you need:

- install project locally:
	- git init
	- git clone https://github.com/finesko1/neuro-app-fastapi.git
- run docker desktop and then:
	- docker-compose -p neuro-fastapi build *(to display the process use --progress=plain)*
	- for work into container:
        - docker exec -it -p neuro-fastapi /bin/sh *(for windows system)*
- you can work with project outer folder using a file global_makefile (create Makefile by copying this file outer folder)
	- to build this project: make build-fastapi
	- to up this project: make up-fastapi
	- to down thiw project: make down-fastapi

The container with the application is running on port 8000!
