# Object Counter Challenge

## Overview
The goal of this repository is to demonstrate how to apply **Hexagonal Architecture (Ports & Adapters)** in a Machine Learning based system.

This application exposes two Flask APIs that both receive:

* An image
* A confidence threshold

and returns:

1. Count of objects detected in the current image, along with total cummulative counts of all detected objects previously
2. List of objects returned for a particular threshold

The object detection model is served through TensorFlow Serving using the SSD MobileNet V2 model trained on the COCO dataset.

---

# Architecture

The application follows a Hexagonal Architecture pattern and is composed of three main layers:

## EntryPoints

Responsible for:

* Exposing REST APIs
* Receiving requests
* Validating inputs
* Returning responses

## Domain

Responsible for:

* Business logic
* Object counting rules
* Orchestrating interactions between adapters
* Applying domain-specific validations

## Adapters

Responsible for:

* Communicating with external services
* Translating domain models into external representations
* Translating external responses into domain objects

Examples include:

* TensorFlow Serving adapter
* Database adapters (MongoDB / MySQL)

---

# Features

## Object Detection

Detects objects in uploaded images using SSD MobileNet V2.

## Threshold Filtering

Allows users to specify a confidence threshold for filtering predictions.

## Persistent Object Counts

Stores cumulative object counts across requests.

## Object Listing

Provides a dedicated endpoint to return detected objects above the specified confidence threshold without updating persisted counts.

## Database Support

Supports:

* MySQL
* MongoDB

Database selection is configurable through environment variables.

## Automated Testing

Includes:

* Unit Tests
* Integration Tests
* End-to-End (E2E) Tests

---

# Quick Start

## Prerequisites

The following software must be installed:

* Python 3.10+
* Docker

Verify installation:

```bash
python3 --version
docker --version
```

## Clone Repository

```bash
git clone https://github.com/joshuadominic0598/object-detection-assignment
cd object-detection-assignment
```

## Start Application

```bash
make start
```

The setup process is fully automated.

The startup script will automatically:

* Create a Python virtual environment
* Install Python dependencies
* Create a default `.env` file if one does not exist
* Download the TensorFlow model
* Start TensorFlow Serving
* Start the configured database (MySQL or MongoDB)
* Create required database objects
* Launch the Flask application

Application URL:

```text
http://localhost:5000
```

Please Note: No manual TensorFlow, database, or environment setup is required.
- By default, the setup script will automatically provision a Dockerized MySQL instance (or MongoDB, depending on `DB_TYPE`) and create all required database objects.
- If you prefer to use your own MySQL instance, update the database connection settings in the `.env` file (`MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DB`) before running `make start`.
- The application will then connect to your existing database instead of the automatically provisioned container.
---

# API Endpoints

## POST /object-count

Detects objects in an image and updates persistent object counts.

### Request

* file: image file
* threshold: confidence threshold

### Response

Returns:

* current_objects
* total_objects

Example:

```bash
curl -F "threshold=0.9" \
     -F "file=@resources/images/boy.jpg" \
     http://localhost:5000/object-count
```

---

## POST /object-list

Detects objects in an image and returns all objects whose confidence score exceeds the specified threshold.

### Request

* file: image file
* threshold: confidence threshold

### Response

Returns:

* object class
* confidence score
* bounding box coordinates

Example:

```bash
curl -F "threshold=0.9" \
     -F "file=@resources/images/boy.jpg" \
     http://localhost:5000/object-list
```

---

# Running Tests

## Run All Tests

```bash
pytest
```

## Run Integration Tests
- test mongodb, tensorflow or mysql connections

```bash
pytest tests/integration -v
```

## Run E2E Tests
- test end to end working of the app, set your own test cases and get feedback on performance

```bash
pytest tests/e2e -v
```

## Run Specific E2E Test

```bash
pytest tests/e2e/test_object_class.py -v
pytest tests/e2e/test_object_persistance.py -v

```
We can establish what classes we hope to detect from an image as well as, what total counts we expect if the model runs through the list of images. This directly helps tune the thresholding required for a particular use case.
---

### Object Detection Validation

Verifies expected object classes are detected from sample images.

Example image:

```text
boy_bowl_cup.jpg
```

Expected classes:

```python
['bowl', 'cup', 'dining table', 'person']
```

Example model output:

```text
Passed Threshold:
['person (0.999)', 'dining table (0.922)']

Detected But Below Threshold:
['cup (0.418)']

Not Detected:
['bowl']

All Predictions:
[
 'person (0.999)',
 'dining table (0.922)',
 'cup (0.418)',
 'orange (0.317)'
]
```

### Threshold Filtering Validation

Ensures only predictions above the specified threshold are returned.

### Database Persistence Validation

Ensures counts accumulate across requests.

Example:

Request 1:

```text
person = 1
```

Request 2:

```text
person = 2
```

This validates:

* Database connectivity
* Repository implementation
* Aggregate counting logic
* Persistence behavior

### Object Count Endpoint Validation

Ensures:

* current_objects reflects only the current request
* total_objects reflects cumulative persisted counts

---

# Notes

* The first startup may take several minutes because the TensorFlow model is downloaded automatically.
* Subsequent startups reuse the downloaded model.
* Object counts persist across requests when using a real database - Otherwise need to set up .env file connected to your MYSQL instance - then requests modify only your table.