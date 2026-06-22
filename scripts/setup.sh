#!/bin/bash

set -euo pipefail

# Create .env if missing

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env created from .env.example"
fi

echo "Reading .env..."

set -a
source .env
set +a

# Create virtual environment if needed

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

# Download TensorFlow model

chmod +x ./scripts/download_model.sh
./scripts/download_model.sh

# Start TensorFlow Serving

if docker ps --format '{{.Names}}' | grep -q '^tfserving$'; then
    echo "TensorFlow Serving already running."
else
    echo "Starting TensorFlow Serving..."

    docker rm -f tfserving 2>/dev/null || true

    docker run -d \
        --name=tfserving \
        -p 8501:8501 \
        --mount type=bind,source=$(pwd)/tmp/model,target=/models \
        -e MODEL_NAME=ssd_mobilenet_v2 \
        tensorflow/serving
fi

echo "Waiting for TensorFlow model to become AVAILABLE..."

until curl -s http://localhost:8501/v1/models/ssd_mobilenet_v2 | grep -q "AVAILABLE"
do
    sleep 2
done

echo "TensorFlow model is ready."

# MySQL Setup

if [ "$DB_TYPE" = "mysql" ]; then

    echo "Checking MySQL port..."

    if lsof -i :"$MYSQL_PORT" >/dev/null 2>&1; then

        if ! docker ps --format '{{.Names}}' | grep -q '^test-mysql$'; then
            echo ""
            echo "ERROR: Port $MYSQL_PORT is already in use."
            echo "Please stop the service using that port or update MYSQL_PORT in .env."
            echo ""
            exit 1
        fi
    fi

    if docker ps --format '{{.Names}}' | grep -q '^test-mysql$'; then

        echo "MySQL container already running."

    else

        echo "Starting MySQL..."

        docker rm -f test-mysql 2>/dev/null || true

        docker run -d \
            --name=test-mysql \
            -e MYSQL_ROOT_PASSWORD="$MYSQL_PASSWORD" \
            -e MYSQL_DATABASE="$MYSQL_DB" \
            -p "$MYSQL_PORT":3306 \
            mysql:8

    fi

    echo "Waiting for MySQL initialization..."

    until docker logs test-mysql 2>&1 | grep -q "ready for connections"
    do
        sleep 2
    done

    echo "Initializing MySQL database..."

    .venv/bin/python scripts/setup_mysql.py

    echo "MySQL ready."

fi

# MongoDB Setup

if [ "$DB_TYPE" = "mongodb" ]; then

    if docker ps --format '{{.Names}}' | grep -q '^test-mongo$'; then

        echo "MongoDB container already running."

    else

        echo "Starting MongoDB..."

        docker rm -f test-mongo 2>/dev/null || true

        docker run -d \
            --name=test-mongo \
            -p "$MONGO_PORT":27017 \
            mongo:latest

    fi

    echo "MongoDB ready."

fi

echo ""
echo "========================================"
echo "Setup complete."
echo "Run application using:"
echo "make start"
echo "========================================"