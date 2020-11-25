#!/usr/bin/env bash

if [ ! "$TRAVIS_PULL_REQUEST_BRANCH" ] && [ "$TRAVIS_BRANCH" == "main" ]; then
	echo "CI on main branch, pushing to Docker..."
	docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD;
	docker push $DOCKER_USERNAME/mtriage:dev;
	docker push $DOCKER_USERNAME/mtriage:dev-gpu;
else
	echo "Not on main branch, nothing to do."
fi
