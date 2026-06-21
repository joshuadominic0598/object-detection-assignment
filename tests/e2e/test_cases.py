OBJECT_COUNT_TEST_CASES = [
    {
        "image_name": "boy_and_cat.jpeg",
        "expected_classes": {"person", "cat"}
    },
    {
        "image_name": "boy_bowl_cup.jpg",
        "expected_classes": {"person", "dining table", "cup", "bowl"}
    },
    {
        "image_name": "cat_bowl.jpg",
        "expected_classes": {"cat", "bowl"}
    },
    {
        "image_name": "four_boys.jpg",
        "expected_classes": {"person"}
    },
    {
        "image_name": "two_cats.jpeg",
        "expected_classes": {"cat"}
    },
    {
        "image_name": "bowl_dining_table_cup.jpg",
        "expected_classes": {"bowl", "dining table","cup"}
    }
]

EXPECTED_MIN_TOTALS = {
    "person": 6,
    "cat": 4,
    "bowl": 3,
    "cup": 2,
    "dining table": 2
}