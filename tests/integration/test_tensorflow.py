from pathlib import Path
from counter.adapters.object_detector import TFSObjectDetector

class TestTensorFlowServing:

    def test_predict_returns_detections(self):
        detector = TFSObjectDetector(host="localhost",port=8501,model="ssd_mobilenet_v2")

        image_path = (Path(__file__).parent.parent.parent/ "resources"/ "images"/ "cat.jpg")

        with open(image_path, "rb") as image:
            predictions = detector.predict(image)

        assert len(predictions) > 0

        assert all(prediction.class_name is not None for prediction in predictions)