# NIQ Innovation Enablement - Object Counter Challenge

## Overview

The goal of this repository is to demonstrate how to apply **Hexagonal Architecture (Ports & Adapters)** in a Machine Learning based system.

This application exposes a Flask API that receives:

* An image
* A confidence threshold

and returns:

* Objects detected in the current image
* Running totals of all detected objects persisted in the database

The object detection model is served through TensorFlow Serving using the SSD MobileNet V2 model trained on the COCO dataset.

---

## Architecture

The application follows a Hexagonal Architecture pattern and is composed of three main layers:

### EntryPoints

Responsible for:

* Exposing REST APIs
* Receiving requests
* Validating inputs
* Returning responses

### Domain

Responsible for:

* Business logic
* Object counting rules
* Orchestrating interactions between adapters
* Applying domain-specific validations

### Adapters

Responsible for:

* Communicating with external services
* Translating domain models into external representations
* Translating external responses into domain objects

Examples include:

* TensorFlow Serving adapter
* Database adapters (MongoDB / MySQL)

---

## Features

### Object Detection

Detects objects in uploaded images using SSD MobileNet V2.

### Threshold Filtering

Allows users to specify a confidence threshold for filtering predictions.

### Persistent Object Counts

Stores cumulative object counts across requests.

### Object Listing
Provides a dedicated endpoint to return the list of detected objects above the specified confidence threshold without updating or returning persisted counts.

### Database Support

Supports:
* MongoDB
* MySQL
Database selection is configurable through environment variables.

### Automated Testing

Includes:
* Unit Tests
* Integration Tests
* End-to-End (E2E) Tests

E2E tests validate:

* Object class detection
* Persistence behavior
* Aggregate object counts

---

# Setup TensorFlow Model

## Unix / macOS

```bash
mkdir -p tmp/model/ssd_mobilenet_v2/1

curl -L -o tmp/model.tar.gz \
http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz

tar -xzvf tmp/model.tar.gz -C tmp/model

mv \
tmp/model/ssd_mobilenet_v2_coco_2018_03_29/saved_model/saved_model.pb \
tmp/model/ssd_mobilenet_v2/1

chmod -R 777 tmp/model

rm tmp/model.tar.gz
rm -rf tmp/model/ssd_mobilenet_v2_coco_2018_03_29
```

Expected directory structure:

```text
tmp/
└── model/
    └── ssd_mobilenet_v2/
        └── 1/
            └── saved_model.pb
```

---

# Run TensorFlow Serving

## Unix / macOS

```bash
num_physical_cores=$(sysctl -n hw.physicalcpu)

docker run --rm -d \
    --name=tfserving \
    -p 8501:8501 \
    --mount type=bind,source=$(pwd)/tmp/model,target=/models \
    -e OMP_NUM_THREADS=$num_physical_cores \
    -e TENSORFLOW_INTRA_OP_PARALLELISM=$num_physical_cores \
    -e MODEL_NAME=ssd_mobilenet_v2 \
    tensorflow/serving
```

## Linux

```bash
num_physical_cores=$(lscpu --all --parse=SOCKET,CORE | grep -v '^#' | uniq | wc -l)

docker run --rm -d \
    --name=tfserving \
    -p 8501:8501 \
    --mount type=bind,source=$(pwd)/tmp/model,target=/models \
    -e OMP_NUM_THREADS=$num_physical_cores \
    -e TENSORFLOW_INTRA_OP_PARALLELISM=$num_physical_cores \
    -e MODEL_NAME=ssd_mobilenet_v2 \
    tensorflow/serving
```

## Windows (PowerShell)

```powershell
$num_physical_cores=(Get-WmiObject Win32_Processor | Select-Object NumberOfCores).NumberOfCores

docker run --rm -d `
    --name=tfserving `
    -p 8501:8501 `
    -v "$pwd\tmp\model:/models" `
    -e OMP_NUM_THREADS=$num_physical_cores `
    -e TENSORFLOW_INTRA_OP_PARALLELISM=$num_physical_cores `
    -e MODEL_NAME=ssd_mobilenet_v2 `
    tensorflow/serving
```

---

# Database Setup

## MongoDB

```bash
docker run --rm \
  --name test-mongo \
  -p 27017:27017 \
  -d mongo:latest
```

## MySQL

```bash
docker run --rm \
  --name test-mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=counter \
  -p 3306:3306 \
  -d mysql:8
```

After startup:

```sql
CREATE DATABASE IF NOT EXISTS counter; -- Docker should create this already

USE counter;

--- You need to create a table manually in your MYSQL for it to persist data
CREATE TABLE IF NOT EXISTS object_counts ( 
    object_class VARCHAR(255) PRIMARY KEY,
    count INT NOT NULL
);
```

---

# Environment Configuration

Create a `.env` file in the project root.

Example:

```env
ENV=prod

--- here you can change to mongodb if that is your preferred DB
DB_TYPE=mysql

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DB=counter

MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=counter

TFS_URL=http://localhost:8501/v1/models/ssd_mobilenet_v2:predict
```

---

# Python Environment Setup

Python 3.10+ recommended.

## Unix / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

export PYTHONPATH=.
```

## Windows PowerShell

```powershell
python3 -m venv .venv

.venv\Scripts\Activate.ps1

pip install -r requirements.txt

$Env:PYTHONPATH="."
```

---

# Run the Application

## Using Fake Services

```bash
python -m counter.entrypoints.webapp
```

## Using Real Services

```bash
ENV=prod python -m counter.entrypoints.webapp
```

or

```bash
python -m counter.entrypoints.webapp
```

when using a configured `.env` file.

Application runs on:

```text
http://localhost:5000
```

---
# API Endpoints

## POST /object-count

Detects objects in an image and updates persistent object counts.

### Request

- file: image file
- threshold: confidence threshold

### Response

Returns:

- current_objects: objects detected in the current image
- total_objects: cumulative object counts stored in the database

## POST /object-list

Detects objects in an image and returns all objects whose confidence score exceeds the provided threshold.

### Request

- file: image file
- threshold: confidence threshold

### Response

Returns a list of detected objects, including:

- object_class
- confidence score
- bounding box coordinates (if available)

### Example Use Cases

- Validate model predictions
- Inspect detections without affecting persisted counts
- Experiment with different confidence thresholds
- Troubleshoot object-count discrepancies

# Call the service
 curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://localhost:5000/object-count
 curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://localhost:5000/object-list


# Running Tests

Run all tests:

```bash
pytest
```

Run Integration tests:

```bash
pytest tests/integration -v
```

Run E2E tests:

```bash
pytest tests/e2e -v
```

Run a specific E2E test:

```bash
pytest tests/e2e/test_object_class.py -v
```

Shorter failure trace:

```bash
pytest tests/e2e -v --tb=short
```

---

# Notes

* TensorFlow Serving must be running before executing production mode tests.
* MySQL or MongoDB must be running when using `ENV=prod`.
* Object counts persist across requests when using a real database.