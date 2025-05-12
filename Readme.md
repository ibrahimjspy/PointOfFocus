
# Flask Saliency Focus

A lightweight Flask service that computes the most salient (attention-grabbing) point in an image using OpenCV’s Spectral Residual Saliency, and returns JSON:

```json
{
  "focus": { "x": 1432, "y": 514 },
  "width": 1920,
  "height": 1080
}
````

It supports both remote images (via URL) and local files (via filesystem path), and ships with a Dockerfile for easy containerized deployment.

---

## Table of Contents

* [Features](#features)
* [Prerequisites](#prerequisites)
* [Local Installation & Running](#local-installation--running)

  * [1. Clone the Repo](#1-clone-the-repo)
  * [2. Create & Activate a Virtualenv](#2-create--activate-a-virtualenv)
  * [3. Install Dependencies](#3-install-dependencies)
  * [4. Run the App](#4-run-the-app)
* [Docker Deployment](#docker-deployment)

  * [Build the Image](#build-the-image)
  * [Run the Container](#run-the-container)
* [API Usage](#api-usage)

  * [Endpoint](#endpoint)
  * [Parameters](#parameters)
  * [Examples](#examples)
* [Project Structure](#project-structure)
* [Troubleshooting](#troubleshooting)
* [License](#license)

---

## Features

* **Saliency-based focus detection** using OpenCV contrib module
* Supports **remote URLs** or **local paths**
* Returns focus point and image dimensions as JSON
* **Docker-ready** for easy deployment
* Simple, zero-configuration HTTP API

---

## Prerequisites

* **Python 3.8+** (tested on 3.12)
* **Git** (for cloning the repo)
* **Docker** (optional, for containerized deployment)

---

## Local Installation & Running

### 1. Clone the Repo

```bash
git clone https://your.git.host/flask-saliency-focus.git
cd flask-saliency-focus
```

### 2. Create & Activate a Virtualenv

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:

* `Flask`
* `opencv-contrib-python==4.5.5.64` (with saliency API)
* `numpy<2.0`
* `requests`

### 4. Run the App

```bash
export FLASK_APP=app.main
export FLASK_ENV=development        # enables debug mode (auto-reload, stack traces)
flask run --host=0.0.0.0 --port=5000
```

You should see:

```
 * Serving Flask app "app.main"
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

---

## Docker Deployment

If you prefer containerization, the included `Dockerfile` builds a minimal image with Gunicorn.

### Build the Image

```bash
docker build -t saliency-focus .
```

### Run the Container

```bash
docker run --rm -p 5000:5000 saliency-focus
```

Now the service is available at `http://localhost:5000`.

To test with a local file, bind your images directory:

```bash
docker run --rm -v $(pwd)/images:/data -p 5000:5000 saliency-focus
```

Then request:

```bash
curl "http://localhost:5000/focus?path=/data/image1.jpg"
```

---

## API Usage

### Endpoint

```
GET /focus
```

### Parameters

| Name | Type   | Required?             | Description                       |
| ---- | ------ | --------------------- | --------------------------------- |
| url  | string | either this or `path` | HTTP URL of an image to analyze.  |
| path | string | either this or `url`  | Filesystem path to a local image. |

### Examples

* **Remote image**

  ```bash
  curl "http://localhost:5000/focus?url=https://example.com/pic.jpg"
  ```
* **Local file**

  ```bash
  curl "http://localhost:5000/focus?path=image1.jpg
  ```

**Success response** (HTTP 200):

```json
{
  "focus": { "x": 1432, "y": 514 },
  "width": 1920,
  "height": 1080
}
```

**Error response** (HTTP 4xx/5xx):

```json
{ "error": "Could not load image at path: /invalid.jpg" }
```

---

## Project Structure

```
flask-saliency-focus/
├── Dockerfile
├── requirements.txt
└── app
    ├── __init__.py           # makes `app` a Python package
    ├── main.py               # Flask app & routes
    └── saliency.py           # image loading & saliency logic
```

---

## Troubleshooting

* **`ImportError: cv2 has no attribute saliency`**
  Make sure you installed `opencv-contrib-python`, not just `opencv-python`, and that it’s pinned to a compatible version:

  ```bash
  pip uninstall opencv-python opencv-contrib-python
  pip install "numpy<2.0" opencv-contrib-python==4.5.5.64
  ```

* **`_ARRAY_API not found` or NumPy ABI errors**
  Pin NumPy to `<2.0` and reinstall OpenCV:

  ```bash
  pip install --upgrade "numpy<2.0"
  pip install --upgrade opencv-contrib-python==4.5.5.64
  ```

* **Timeout downloading remote images**
  Check that the URL is reachable and serving an image. Default timeout is 10 seconds.

