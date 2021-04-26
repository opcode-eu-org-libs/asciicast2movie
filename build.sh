#!/usr/bin/env bash

TAG=${1:-test}

docker build -t asciicast2movie:${TAG} -f Dockerfile .
