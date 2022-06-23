from confluent_kafka import Consumer, KafkaError
from confluent_kafka.error import KafkaException, KafkaError
import os
import logging
import json
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

log = logging.getLogger("test-bridge")


KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "broker:29092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "data")

KAFKA_CONFIG = {'bootstrap.servers': KAFKA_BROKER,
        'group.id': "rhose-experiments",
        'enable.auto.commit': False,
        'auto.offset.reset': 'earliest'}


MODEL_ANOMALY_URL = os.environ.get("MODEL_ANOMALY_URL", "http://anomaly-detector:9000/predict")
MODEL_DRIFT_URL = os.environ.get("MODEL_DRIFT_URL", "http://drift-detector:9000/predict")
GENERATOR_URL = os.environ.get("GENERATOR_URL", "http://generator:5000/update")

ALL_DATA = []



@st.experimental_memo
def get_data():
    return ALL_DATA


st.set_page_config(
    page_title="Anonaly / Drift detection",
    page_icon="🌹",
    layout="wide",
)

# dashboard title
st.title("Real-Time anomaly / drift detection")

DATA = {"y": [], "ds": [], "outlier": [], "mean": [], "drift": []}

def create_anomaly():
    requests.get(f"{GENERATOR_URL}?spike=2.0")


# Control sidebar

with st.sidebar:
    st.number_input("Drift rate")
    st.button("Drift")
    st.number_input("Anomaly size")
    st.button("Create anomaly", on_click=create_anomaly)


# Plot containers

data_holder = st.empty()

consumer = Consumer(KAFKA_CONFIG)
try:
    consumer.subscribe(['data'])
    while True:
        message = consumer.poll(timeout=1.0)
        if message is None: continue

        if message.error():
            if message.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print('Reached end at offset')
            elif message.error():
                raise KafkaException(message.error())
        else:
            data = json.loads(message.value())
            DATA["y"].append(data["y"])
            DATA["ds"].append(pd.Timestamp(data["ds"]).to_pydatetime())
            # Get anomaly prediction
            response = requests.post(MODEL_ANOMALY_URL, json=data)
            json_resp = json.loads(response.json())
            DATA["outlier"].append(json_resp["outlier"])
            DATA["mean"].append(sum(DATA["y"]) / len(DATA["y"]))

            # Get drift prediction
            response = requests.post(MODEL_DRIFT_URL, json={"y": data["y"]})
            json_resp = json.loads(response.json())
            DATA["drift"].append(json_resp["drift"])

            df = pd.DataFrame(data=DATA)
            df["c_outlier"] = df["outlier"].apply(lambda x: "k" if x == 0 else "r")
            df["c_drift"] = df["drift"].apply(lambda x: "k" if x == 0 else "r")

            with data_holder.container():
                fig, ax = plt.subplots(figsize=(20, 4))
                ax.plot(df.ds, df.y, c="k", alpha=0.75)
                ax.scatter(df.ds, df.y, c=df.c_outlier)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

                mean_col, drift_col = st.columns(2)

                with mean_col:
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.plot(df.ds, df["mean"], c="k", alpha=0.75)
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)

                with drift_col:
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.scatter(df.ds, df.drift, c=df.c_drift, alpha=0.75)
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)
        
finally:
    # Close down consumer to commit final offsets.
    consumer.close()




        

print("Something went wrong, because I left the Kafka loop.")
