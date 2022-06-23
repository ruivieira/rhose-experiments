
FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8501

COPY . .

CMD [ "streamlit", "run", "app.py"]