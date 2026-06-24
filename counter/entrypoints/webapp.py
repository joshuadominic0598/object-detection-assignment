from io import BytesIO
import time
import uuid

from flask import Flask, request, jsonify

from counter import config

def get_request_data():
    request_id = str(uuid.uuid4())
    start_time = time.time()
    threshold = float(request.form.get("threshold", 0.5))
    uploaded_file = request.files["file"]
    image_name = uploaded_file.filename
    image = BytesIO()
    uploaded_file.save(image)
    return request_id, start_time, threshold, image_name, image

def get_elapsed_ms(start_time):
    return int((time.time() - start_time) * 1000)

def log_request(monitor,request_id,endpoint,image_name,threshold,start_time,success,detected_count=0,detected_classes="",error_message=None):
    monitor.log_request(request_id=request_id,endpoint=endpoint,image_name=image_name,threshold=threshold,response_time_ms=get_elapsed_ms(start_time),detected_count=detected_count,detected_classes=detected_classes,
        status_code=200 if success else 500,
        success=success,
        error_message=error_message
    )

def create_app():

    app = Flask(__name__)

    count_action = config.get_count_action()
    object_list_action = config.get_object_list_action()
    monitor = config.get_monitor()

    @app.route("/object-count", methods=["POST"])
    def object_detection():
        request_id, start_time, threshold, image_name, image = get_request_data()
        try:
            count_response = count_action.execute(image,threshold)
            detected_classes = ",".join(sorted({item.object_class for item in count_response.current_objects}))
            log_request(monitor,request_id,"/object-count",image_name,threshold,start_time,True,len(count_response.current_objects),detected_classes) 
            return jsonify(count_response)
        except Exception as ex:
            log_request(monitor,request_id,"/object-count",image_name,threshold,start_time,False,ex)
            raise

    @app.route("/object-list", methods=["POST"])
    def object_list_detection():
        request_id, start_time, threshold, image_name, image = get_request_data()
        try:
            predictions = object_list_action.execute(image,threshold)
            detected_classes = ",".join(sorted({item.object_class for item in count_response.current_objects}))
            for prediction in predictions:
                monitor.log_prediction(request_id,"/object-list",image_name,prediction.class_name,prediction.score)
            log_request(monitor,request_id,"/object-list",image_name,threshold,start_time,True,len(count_response.current_objects),detected_classes) 
            return jsonify(
                [
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
                ]
            )
        except Exception as ex:
            log_request(monitor,request_id,"/object-list",image_name,threshold,start_time,False,ex)
            raise

    return app


if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', debug=True)
