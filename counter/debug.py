import os
from datetime import datetime

from PIL import ImageDraw, ImageFont


def get_color(score):
    """
    Red    : < 0.40
    Yellow : 0.40 - 0.70
    Green  : > 0.70
    """

    if score < 0.40:
        return "red"

    if score < 0.70:
        return "yellow"

    return "green"


def draw(predictions, image, image_name):

    draw_image = ImageDraw.Draw(image, "RGBA")

    image_width, image_height = image.size

    font = ImageFont.truetype(
        "counter/resources/arial.ttf",
        20
    )

    for prediction in predictions:

        box = prediction.box
        score = prediction.score
        color = get_color(score)

        xmin = box.xmin * image_width
        ymin = box.ymin * image_height
        xmax = box.xmax * image_width
        ymax = box.ymax * image_height

        # Bounding box
        draw_image.rectangle(
            [(xmin, ymin), (xmax, ymax)],
            outline=color,
            width=3
        )

        # Label
        label = f"{prediction.class_name}: {score:.3f}"

        draw_image.text(
            (xmin, max(0, ymin - 25)),
            label,
            font=font,
            fill=color
        )

    # --------------------------------------------------
    # Summary section at bottom of image
    # --------------------------------------------------

    if predictions:

        lowest_score = min(
            prediction.score
            for prediction in predictions
        )

        summary_text = (
            f"Total detections: {len(predictions)} | "
            f"Lowest confidence: {lowest_score:.3f}"
        )

        draw_image.text(
            (10, image_height - 30),
            summary_text,
            font=font,
            fill="blue"
        )

    # --------------------------------------------------
    # Create folder if needed
    # --------------------------------------------------

    os.makedirs("tmp/debug", exist_ok=True)

    # --------------------------------------------------
    # Unique filename
    # --------------------------------------------------

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = os.path.basename(image_name)

    output_file = (f"tmp/debug/{timestamp}_{base_filename}.jpg")

    image.save(output_file, "JPEG")

    print(f"Debug image saved: {output_file}")