from io import BytesIO
import time
import uuid

from flask import Flask, request, jsonify

from counter import config


def create_app():

    app = Flask(__name__)
    count_action = config.get_count_action()
    object_list_action = config.get_object_list_action()
    monitor = config.get_monitor()

    @app.route('/object-count', methods=['POST'])
    def object_detection():

        request_id = str(uuid.uuid4())
        start_time = time.time()
        threshold = float(request.form.get("threshold", 0.5))
        uploaded_file = request.files["file"]
        image_name = uploaded_file.filename
        image = BytesIO()
        uploaded_file.save(image)

        try:
            count_response = count_action.execute(image,threshold)
            elapsed_ms = int((time.time() - start_time) * 1000)
            detected_classes = ",".join(sorted({item.object_class for item in count_response.current_objects}))

            monitor.log_request(
                request_id=request_id,
                endpoint="/object-count",
                image_name=image_name,
                threshold=threshold,
                response_time_ms=elapsed_ms,
                detected_count=len(count_response.current_objects),
                detected_classes=detected_classes,
                status_code=200,
                success=True)

            return jsonify(count_response)

        except Exception as ex:

            elapsed_ms = int((time.time() - start_time) * 1000)

            monitor.log_request(
                request_id=request_id,
                endpoint="/object-count",
                image_name=image_name,
                threshold=threshold,
                response_time_ms=elapsed_ms,
                detected_count=0,
                detected_classes="",
                status_code=500,
                success=False,
                error_message=str(ex))

            raise

    @app.route('/object-list', methods=['POST'])
    def object_list_detection():

        request_id = str(uuid.uuid4())
        start_time = time.time()
        threshold = float(request.form.get("threshold", 0.5))
        uploaded_file = request.files["file"]
        image_name = uploaded_file.filename
        image = BytesIO()
        uploaded_file.save(image)

        try:
            predictions = object_list_action.execute(image,threshold)
            detected_classes = ",".join(sorted({prediction.class_name for prediction in predictions}))

            for prediction in predictions:
                monitor.log_prediction(
                    request_id=request_id,
                    endpoint="/object-list",
                    image_name=image_name,
                    object_class=prediction.class_name,
                    confidence=prediction.score)

            elapsed_ms = int((time.time() - start_time) * 1000)

            monitor.log_request(
                request_id=request_id,
                endpoint="/object-list",
                image_name=image_name,
                threshold=threshold,
                response_time_ms=elapsed_ms,
                detected_count=len(predictions),
                detected_classes=detected_classes,
                status_code=200,
                success=True)

            return jsonify([
                {
                    "class_name": prediction.class_name,
                    "score": prediction.score,
                    "box": {
                        "xmin": prediction.box.xmin,
                        "ymin": prediction.box.ymin,
                        "xmax": prediction.box.xmax,
                        "ymax": prediction.box.ymax,
                    }
                }
                for prediction in predictions
            ])

        except Exception as ex:

            elapsed_ms = int((time.time() - start_time) * 1000)

            monitor.log_request(
                request_id=request_id,
                endpoint="/object-list",
                image_name=image_name,
                threshold=threshold,
                response_time_ms=elapsed_ms,
                detected_count=0,
                detected_classes="",
                status_code=500,
                success=False,
                error_message=str(ex)
            )

            raise

    return app

if __name__ == "__main__":

    app = create_app()
    app.run(host="0.0.0.0", debug=True)