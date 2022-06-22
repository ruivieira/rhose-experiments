from datetime import datetime
import json
from flask import Flask, request
import os
from flask_apscheduler import APScheduler
import generator
from kafka import KafkaProducer
import logging
log = logging.getLogger("anomaly-generator")


app = Flask(__name__)
scheduler = APScheduler()

time_counter = 0
drift_counter = 0
drifting = False
PERIOD = float(os.environ.get("PERIOD", 10))
AMPLITUDE = float(os.environ.get("AMPLITUDE", 100))
ERROR = float(os.environ.get("ERROR", 2))
MEAN = float(os.environ.get("MEAN", 0))
DRIFT = float(os.environ.get("DRIFT", 0))
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "broker:29092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "data")
ANOMALY_SPIKE=False
ANOMALY_SPIKE_VALUE = 2.0

producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER])


def build_message(value: float, t: datetime) -> str:
    payload = {"y": value, "ds": t.isoformat()}
    return json.dumps(payload)


def emit():
    global time_counter
    global drift_counter
    global drifting
    global producer
    global PERIOD
    global AMPLITUDE
    global ERROR
    global MEAN
    global DRIFT
    global KAFKA_BROKER
    global KAFKA_TOPIC
    global ANOMALY_SPIKE
    global ANOMALY_SPIKE_VALUE
    if not drifting:
        y = generator.generate_step(
            time_counter, PERIOD, AMPLITUDE, error=ERROR, mean=MEAN
        )
    else:
        y = (
            generator.generate_step(
                time_counter, PERIOD, AMPLITUDE, error=ERROR, mean=MEAN
            )
            + drift_counter * DRIFT
        )
        drift_counter += 1
    print(
        f"Currently it is t = {time_counter}, value is {y}" + "(drifting)"
        if drifting
        else ""
    )
    if ANOMALY_SPIKE:
        y *= ANOMALY_SPIKE_VALUE
        ANOMALY_SPIKE = False
    time = datetime.now()
    payload = build_message(y, time)
    log.info(f"Sending {payload}")
    producer.send(KAFKA_TOPIC, value=bytes(payload, "UTF-8"))
    time_counter += 1


@app.route("/update", methods=["GET"])
def update():
    global AMPLITUDE
    global ERROR
    global MEAN
    global DRIFT
    global drifting
    global drift_counter
    global ANOMALY_SPIKE
    global ANOMALY_SPIKE_VALUE
    if request.args.get("amplitude"):
        AMPLITUDE = float(request.args.get("amplitude"))
        print(f"Amplitude set to {AMPLITUDE}")
    if request.args.get("error"):
        ERROR = float(request.args.get("error"))
        print(f"Error set to {ERROR}")
    if request.args.get("mean"):
        MEAN = float(request.args.get("mean"))
        print(f"Mean set to {MEAN}")
    if request.args.get("drift"):
        DRIFT = float(request.args.get("drift"))
        print(f"Drift set to {DRIFT}")
    if request.args.get("drifting"):
        drifting = bool(request.args.get("drifting"))
        drift_counter = 0
        print(f"Started drifting")
    if request.args.get("spike"):
        ANOMALY_SPIKE_VALUE = float(request.args.get("drift"))
        ANOMALY_SPIKE = True
        print(f"Creating an amonaly spike of value {ANOMALY_SPIKE_VALUE}")

    return "Hello, World"


if __name__ == "__main__":
    scheduler.add_job(id="Scheduled Task", func=emit, trigger="interval", seconds=3)
    scheduler.start()
    app.run(host="0.0.0.0")
