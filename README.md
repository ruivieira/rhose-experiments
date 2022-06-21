# Starting

Start by using

```shell
docker-compose up docker-compose up --build -d
```

# Kafka topic

Build the Kafka topic with:

```shell
docker exec broker \
kafka-topics --bootstrap-server broker:9092 \
             --create \
             --topic quickstart
```