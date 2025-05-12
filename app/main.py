from flask import Flask, request, jsonify
from .saliency import (
    load_image_from_url,
    load_image_from_path,
    find_salient_point,
)

app = Flask(__name__)

@app.route("/focus", methods=["GET"])
def focus():
    url = request.args.get("url")
    path = request.args.get("path")
    if not url and not path:
        return jsonify({"error": "provide either 'url' or 'path' parameter"}), 400

    try:
        if url:
            img = load_image_from_url(url)
        else:
            img = load_image_from_path(path)

        (cx, cy), (w, h) = find_salient_point(img)
        return jsonify({
            "focus": {"x": cx, "y": cy},
            "width": w,
            "height": h
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # for local debugging only; in Docker we'll use gunicorn
    app.run(host="0.0.0.0", port=5000, debug=True)
