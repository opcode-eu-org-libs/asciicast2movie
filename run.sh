#!/usr/bin/env bash

TAG=${TAG:-test}

docker run -t --rm -v ${PWD}:/data -u $(id -u):$(id -g) asciicast2movie:${TAG} $*
