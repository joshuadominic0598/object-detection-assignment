# Object Counter Challenge
The goal of this repository is to demonstrate how to apply **Hexagonal Architecture (Ports & Adapters)** in a Machine Learning based system.

# Architecture
The application follows a Hexagonal Architecture pattern and is composed of three main layers:
Entrypoints, Domain and Adapters

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
# Make Commands

The project provides several Make targets to simplify common workflows.

## Start Application

Starts the complete application stack:

```bash
make start
```

This will:

* Create the Python virtual environment if required
* Install dependencies
* Download the TensorFlow model
* Start TensorFlow Serving
* Start MySQL or MongoDB
* Initialize database objects
* Launch the Flask application

---

## Stop Services
Stops all Docker services:

```bash
make stop
```
---

## Run Unit Tests
Runs all unit tests:

```bash
make test
```
---

## Run Integration Tests
Runs integration tests against external dependencies such as:
* TensorFlow Serving
* MySQL
* MongoDB

```bash
make integration
```
---

## Run End-to-End Tests
Runs complete application validation tests:

```bash
make e2e
```
These tests exercise the full stack including:
* Flask APIs
* TensorFlow Serving
* Database persistence
* Domain logic

---

## Generate Monitoring Dashboard
Creates an interactive HTML dashboard from monitoring data:

```bash
make dashboard
```
The dashboard is automatically opened in your browser after generation.

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

## Run E2E Tests - Uses test cases as ground truth and test images as data
- test end to end working of the app, set your own test cases and get feedback on performance

```bash
pytest tests/e2e -v
```

## Run Specific E2E Test

```bash
pytest tests/e2e/test_object_class.py -v
pytest tests/e2e/test_object_persistance.py -v
```
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
# API Monitoring & Dashboard

The application includes built-in monitoring capabilities to track API behavior, model predictions, and operational metrics.

All monitoring information is persisted to MySQL and can be visualized through an automatically generated HTML dashboard.

## Request Monitoring

Every API request is logged to the `api_request_log` table.

Captured fields include:

* Request timestamp
* Endpoint
* Uploaded image name
* Confidence threshold
* Response time (milliseconds)
* Number of detected objects
* Unique detected classes
* HTTP status code
* Success / failure status
* Error message (if applicable)

Example:

| endpoint      | image_name | detected_classes | response_time_ms |
| ------------- | ---------- | ---------------- | ---------------- |
| /object-count | cat.jpg    | cat              | 982              |
| /object-list  | people.jpg | person,dog       | 1145             |

---

## Prediction Monitoring

Every detected prediction is logged to the `prediction_log` table.

Captured fields include:

* Request timestamp
* Endpoint
* Image name
* Object class
* Confidence score

Example:

| endpoint      | object_class | confidence |
| ------------- | ------------ | ---------- |
| /object-list  | person       | 0.994      |
| /object-list  | dog          | 0.912      |
| /object-count | cat          | 0.997      |

This allows detailed analysis of model behavior over time.

---

## Dashboard Generation

Generate a monitoring dashboard using:

```bash
make dashboard
```

The dashboard is generated from monitoring tables and automatically opened in your browser.

---

## Dashboard Contents

* The dashboard includes:
* Dashboard Features
* Total requests breakdown (Success vs Failure)
* Requests by endpoint (/object-count vs /object-list)
* Response time distribution histogram
* Top 20 detected object classes by frequency
* Prediction confidence score distribution
* Detection failure rate (% of requests with no objects detected)
* Current cumulative object counts from database
* Latest 20 API request records
* Latest 20 prediction records
* Request auditing (image name, threshold, response time, status)

# Notes
* The first startup may take several minutes because the TensorFlow model is downloaded automatically.
* Subsequent startups reuse the downloaded model.
* Object counts persist across requests when using a real database - Otherwise need to set up .env file connected to your MYSQL instance - then requests modify only your table.