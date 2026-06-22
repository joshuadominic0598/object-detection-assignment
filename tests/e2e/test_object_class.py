import io
import json
import os

from pathlib import Path

from counter.entrypoints.webapp import create_app
from tests.e2e.test_cases import OBJECT_COUNT_TEST_CASES


class TestObjectCountE2E:

    def test_object_count_persists_counts_across_requests(self):

        os.environ["ENV"] = "prod"
        os.environ["DB_TYPE"] = "mysql"

        app = create_app()
        app.config["TESTING"] = True

        image_root = (
            Path(__file__).parent.parent.parent
            / "resources"
            / "images"
            / "test_images"
        )

        with app.test_client() as client:

            previous_totals = {}
            class_failures = []

            for test_case in OBJECT_COUNT_TEST_CASES:

                image_name = test_case["image_name"]
                expected_classes = test_case["expected_classes"]

                image_path = image_root / image_name

                # Object Count Endpoint
                with open(image_path, "rb") as f:

                    response = client.post(
                        "/object-count",
                        data={
                            "threshold": "0.5",
                            "file": (
                                io.BytesIO(f.read()),
                                image_name
                            )
                        },
                        content_type="multipart/form-data"
                    )

                assert response.status_code == 200

                body = json.loads(response.data)

                assert "current_objects" in body
                assert "total_objects" in body

                current_classes = {
                    obj["object_class"]
                    for obj in body["current_objects"]
                }

                # Object List Endpoint
=                with open(image_path, "rb") as f:

                    object_list_response = client.post(
                        "/object-list",
                        data={
                            "threshold": "0.5",
                            "file": (
                                io.BytesIO(f.read()),
                                image_name
                            )
                        },
                        content_type="multipart/form-data"
                    )

                assert object_list_response.status_code == 200

                prediction_body = json.loads(
                    object_list_response.data
                )

                all_predictions = {
                    obj["class_name"]: obj["score"]
                    for obj in prediction_body
                }
=
                if not expected_classes.issubset(current_classes):

                    above_threshold = []
                    below_threshold = []
                    not_detected = []

                    for expected_class in sorted(expected_classes):

                        if expected_class in current_classes:

                            above_threshold.append(
                                f"{expected_class} "
                                f"({all_predictions.get(expected_class, 0):.3f})"
                            )

                        elif expected_class in all_predictions:

                            below_threshold.append(
                                f"{expected_class} "
                                f"({all_predictions.get(expected_class):.3f})"
                            )

                        else:

                            not_detected.append(expected_class)

                    class_failures.append(
                        {
                            "image": image_name,
                            "expected": sorted(expected_classes),
                            "detected": sorted(current_classes),
                            "above_threshold": above_threshold,
                            "below_threshold": below_threshold,
                            "not_detected": not_detected,
                            "all_predictions": sorted(
                                [
                                    f"{cls} ({score:.3f})"
                                    for cls, score
                                    in all_predictions.items()
                                ]
                            )
                        }
                    )

                totals = {
                    obj["object_class"]: obj["count"]
                    for obj in body["total_objects"]
                }

                for object_class in expected_classes:

                    if object_class in previous_totals:

                        assert (
                            totals[object_class]
                            > previous_totals[object_class]
                        )

                    previous_totals[object_class] = (
                        totals[object_class]
                    )
                    
            if class_failures:

                error_message = (
                    "\n\nCLASS DETECTION FAILURES\n"
                )

                error_message += "=" * 60 + "\n"

                for failure in class_failures:

                    error_message += (
                        f"\nImage: {failure['image']}"
                        f"\nExpected Classes:"
                        f"\n{failure['expected']}"
                        f"\n"
                        f"\nPassed Threshold:"
                        f"\n{failure['above_threshold']}"
                        f"\n"
                        f"\nDetected But Below Threshold:"
                        f"\n{failure['below_threshold']}"
                        f"\n"
                        f"\nNot Detected:"
                        f"\n{failure['not_detected']}"
                        f"\n"
                        f"\nAll Predictions:"
                        f"\n{failure['all_predictions']}"
                        f"\n{'-' * 60}"
                    )

                assert False, error_message