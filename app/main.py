"""
Saliency Detection Flask API
=============================

This Flask app exposes an API to detect the most salient (visually important) point in an image.
You can supply either a URL or a local file path to an image. The API will return the image dimensions
and the coordinates of the computed focus point.

Endpoints:
---------
- GET /focus?url=...         → Process image from URL
- GET /focus?path=...        → Process image from local path

Returns:
--------
- JSON response with focus coordinates and image dimensions.
- On error, a JSON error message with appropriate status code.

Author: [Your Name]
Date: 2025-05-19
"""

from flask import Flask, request, jsonify
from .saliency import (
    load_image_from_url,
    load_image_from_path,
    find_salient_point,
)
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


@app.route("/focus", methods=["GET"])
def focus():
    """
    Endpoint to compute the salient point of an image.

    Query Parameters:
    -----------------
    - url (str): URL to the image.
    - path (str): Local file path to the image.

    Returns:
    --------
    JSON object:
    {
        "focus": {"x": <int>, "y": <int>},
        "width": <int>,
        "height": <int>
    }

    Errors:
    -------
    - 400: Missing required query parameter
    - 500: Internal server error
    """
    url = request.args.get("url")
    path = request.args.get("path")

    if not url and not path:
        logging.warning("Missing 'url' or 'path' parameter in request")
        return jsonify({"error": "Provide either 'url' or 'path' parameter"}), 400

    try:
        if url:
            logging.info(f"Received image URL: {url}")
            img = load_image_from_url(url)
        else:
            logging.info(f"Received local path: {path}")
            img = load_image_from_path(path)

        (cx, cy), (w, h) = find_salient_point(img)

        logging.info(f"Salient point computed: ({cx}, {cy}) in image of size ({w}x{h})")
        return jsonify({
            "focus": {"x": cx, "y": cy},
            "width": w,
            "height": h
        })

    except Exception as e:
        logging.exception("Error processing request")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Local development server only
    app.run(host="0.0.0.0", port=5000, debug=True)
