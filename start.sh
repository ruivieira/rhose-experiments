#!/usr/bin/env sh

echo Starting zookeeper, broker, anomaly-detector, Kafdrop
docker-compose up zookeeper broker anomaly-detector kafdrop --build -d

sleep 10

echo Starting data generator
docker-compose up generator --build -d

sleep 5

echo Starting test bridge
docker-compose up test-bridge --build -d