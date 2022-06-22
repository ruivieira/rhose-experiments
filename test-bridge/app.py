from kafka import KafkaConsumer
import os
import logging
import json
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

log = logging.getLogger("test-bridge")


# KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "broker:29092")
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "data")

# MODEL_URL = 'http://anomaly-detector:9000/predict'
MODEL_URL = "http://localhost:9000/predict"
GENERATOR_URL = "http://localhost:5000/update"

ALL_DATA = []

consumer = KafkaConsumer(
    KAFKA_TOPIC, bootstrap_servers=[KAFKA_BROKER], enable_auto_commit=True
)


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

DATA = {"y": [], "ds": [], "outlier": [], "mean": []}

def create_anomaly():
    requests.get(f"{GENERATOR_URL}?spike=2.0")

# Control sidebar

with st.sidebar:
    st.number_input('Drift rate')
    st.button("Drift")
    st.number_input('Anomaly size')
    st.button("Create anomaly", on_click=create_anomaly)


# Plot containers

data_holder = st.empty()
mean_holder = st.empty()

for message in consumer:
    data = json.loads(message.value)
    DATA["y"].append(data["y"])
    DATA["ds"].append(pd.Timestamp(data["ds"]).to_pydatetime())
    response = requests.post(MODEL_URL, json=data)
    json_resp = json.loads(response.json())
    DATA["outlier"].append(json_resp["outlier"])
    DATA["mean"].append(sum(DATA["y"])/len(DATA["y"]))

    df = pd.DataFrame(data=DATA)
    df['colour'] = df['outlier'].apply(lambda x: "k" if x==0 else "r")

    with data_holder.container():
        fig, ax = plt.subplots(figsize=(20,4))
        ax.plot(df.ds, df.y, c="k", alpha=0.75)
        ax.scatter(df.ds, df.y, c=df.colour)
        st.pyplot(fig, use_container_width=True)

    with mean_holder.container():
        fig, ax = plt.subplots(figsize=(20,4))
        ax.plot(df.ds, df['mean'], c="k", alpha=0.75)
        st.pyplot(fig, use_container_width=True)


    print(response.json())
    log.info(response.json())
