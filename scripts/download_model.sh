#!/bin/bash

set -e

MODEL_FILE="tmp/model/ssd_mobilenet_v2/1/saved_model.pb"

# Skip download if model already exists
if [ -f "$MODEL_FILE" ]; then
    echo "TensorFlow model already exists. Skipping download."
    exit 0
fi

echo "Downloading TensorFlow model..."

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

echo "TensorFlow model download complete."