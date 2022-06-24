# rhose-experiments

![](docs/architecture.svg)

## Starting

### Kafka and detectors

Start by using

```shell
docker-compose up zookeeper broker anomaly-detector --build -d
```

### Generator

```shell
docker-compose up generator --build -d
```

## Anomaly detection

```
curl -X POST  http://localhost:9000/predict \
   -H 'Content-Type: application/json' \
   -d '{"y": 210}'
```