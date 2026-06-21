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

        image_root = (Path(__file__).parent.parent.parent
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

                with open(image_path, "rb") as f:

                    response = client.post("/object-count",
                        data={"threshold": "0.5",
                            "file": (io.BytesIO(f.read()), image_name)},
                        content_type="multipart/form-data")

                assert response.status_code == 200

                body = json.loads(response.data)

                assert "current_objects" in body
                assert "total_objects" in body

                current_classes = {obj["object_class"]for obj in body["current_objects"]}

                missing_classes = expected_classes - current_classes

                # Collect failures instead of stopping immediately
                if not expected_classes.issubset(current_classes):
                    class_failures.append(
                        {
                            "image": image_name,
                            "expected": sorted(expected_classes),
                            "detected": sorted(current_classes),
                            "missing": sorted(missing_classes)
                        }
                    )

                totals = {obj["object_class"]: obj["count"] for obj in body["total_objects"]}

                for object_class in expected_classes:

                    if object_class in previous_totals:

                        assert (totals[object_class] > previous_totals[object_class])

                    previous_totals[object_class] = totals[object_class]

            # Report all class failures at the end
            if class_failures:

                error_message = "\n\nCLASS DETECTION FAILURES\n"
                error_message += "=" * 60 + "\n"

                for failure in class_failures:
                    error_message += (
                        f"\nImage: {failure['image']}"
                        f"\nExpected: {failure['expected']}"
                        f"\nDetected: {failure['detected']}"
                        f"\nMissing: {failure['missing']}"
                        f"\n{'-' * 60}"
                    )

                assert False, error_message