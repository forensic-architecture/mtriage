#!/usr/bin/env bash

if [ ! "$TRAVIS_PULL_REQUEST_BRANCH" ] && ["$TRAVIS_BRANCH" == "master"]; then
	echo "CI on master branch, pushing to Docker..."
	docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD;
	docker push $DOCKER_USERNAME/mtriage:dev;
else
	echo "Not on master branch, nothing to do."
fi
