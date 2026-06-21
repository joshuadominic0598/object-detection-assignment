import io
import json
import os
from pathlib import Path
import mysql.connector
from counter.entrypoints.webapp import create_app
from tests.e2e.test_cases import OBJECT_COUNT_TEST_CASES, EXPECTED_MIN_TOTALS

class TestObjectCountPersistenceE2E:

    @staticmethod
    def clear_mysql_table():

        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", 3306)),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DB", "counter"))

        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE object_counts")
        connection.commit()
        cursor.close()
        connection.close()

    def test_object_count_persists_expected_totals(self):

        os.environ["ENV"] = "prod"
        os.environ["DB_TYPE"] = "mysql"

        self.clear_mysql_table()

        app = create_app()
        app.config["TESTING"] = True

        image_root = (Path(__file__).parent.parent.parent
            / "resources"
            / "images"
            / "test_images")

        final_response_body = None

        with app.test_client() as client:

            for test_case in OBJECT_COUNT_TEST_CASES:

                image_name = test_case["image_name"]

                image_path = image_root / image_name

                with open(image_path, "rb") as f:

                    response = client.post("/object-count",
                        data={"threshold": "0.5", "file": (io.BytesIO(f.read()), image_name)},
                        content_type="multipart/form-data")

                assert response.status_code == 200

                final_response_body = json.loads(response.data)

        assert final_response_body is not None

        total_objects = {obj["object_class"]: obj["count"] for obj in final_response_body["total_objects"]}
        
        print("\nFINAL TOTALS")
        print("=" * 50)

        for object_class, count in sorted(total_objects.items()):
            print(f"{object_class}: {count}")

        print("=" * 50)

        failures = []

        for object_class, expected_count in EXPECTED_MIN_TOTALS.items():

            actual_count = total_objects.get(object_class, 0)

            if actual_count < expected_count:
                failures.append(
                    f"{object_class}: expected >= {expected_count}, actual = {actual_count}"
                )

        if failures:
            error_message = (
                "\n\nTOTAL COUNT FAILURES\n"
                + "=" * 60
                + "\n\n"
                + "\n".join(failures))
                
            assert False, error_message