from PIL import Image

from counter.debug import draw
from counter.domain.models import CountResponse
from counter.domain.ports import ObjectDetector, ObjectCountRepo
from counter.domain.predictions import over_threshold, count


class PredictionService:

    def __init__(self, object_detector: ObjectDetector):
        self._object_detector = object_detector

    def get_valid_predictions(self, image, threshold):
        predictions = self._object_detector.predict(image)
        self._debug_image(image,predictions,"all_predictions")
        valid_predictions = list(over_threshold(predictions,threshold=threshold))
        self._debug_image(image,valid_predictions,f"valid_predictions_threshold_{threshold}")
        return valid_predictions

    @staticmethod
    def _debug_image(image, predictions, image_name):
        if __debug__ and image is not None:
            image = Image.open(image)
            draw(predictions,image,image_name)


class CountDetectedObjects:

    def __init__(self,object_detector: ObjectDetector,object_count_repo: ObjectCountRepo):
        self.__prediction_service = PredictionService(object_detector)
        self.__object_count_repo = object_count_repo

    def execute(self,image,threshold) -> CountResponse:
        predictions = self.__prediction_service.get_valid_predictions(image,threshold)
        object_counts = count(predictions)
        self.__object_count_repo.update_values(object_counts)
        total_objects = self.__object_count_repo.read_values()
        return CountResponse(current_objects=object_counts,total_objects=total_objects)

class ListDetectedObjects:

    def __init__(self,object_detector: ObjectDetector):
        self.__prediction_service = PredictionService(object_detector)

    def execute(self,image,threshold):
        return self.__prediction_service.get_valid_predictions(image,threshold)