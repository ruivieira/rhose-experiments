#!/usr/bin/env sh

echo Starting zookeeper, broker, anomaly-detector, drift-detector, Kafdrop
docker-compose up zookeeper broker anomaly-detector drift-detector kafdrop --build -d

sleep 10

echo Starting data generator
docker-compose up generator --build -d

sleep 5

echo Starting test bridge
docker-compose up test-bridge --build -d

echo Following services are available:
echo - Test bridge: http://127.0.0.1:8502
echo - Kafdrop: http://127.0.0.1:8888