FROM python:3.8-slim
WORKDIR /app

# Install python packages
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get -y --no-install-recommends install libgl1 libglib2.0-0 build-essential
RUN pip install -r requirements.txt
RUN pip install seldon-core

# Copy source code
COPY . .

# Port for GRPC
EXPOSE 5000
# Port for REST
EXPOSE 9000

# Define environment variables
ENV MODEL_NAME DriftDetector
ENV SERVICE_TYPE MODEL

# Changing folder to default user
RUN chown -R 8888 /app

CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE