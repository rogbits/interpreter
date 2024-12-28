#!/usr/bin/env bash

docker container inspect interpreter &> /dev/null
container_exists=$(test $? == 0 && echo "true" || echo "false")
if $container_exists; then
  docker start interpreter
  docker exec -it interpreter bash
else
  docker run -it --name interpreter --mount=type=bind,src="$HOME"/code/interpreter,target=/app ubuntu
fi
