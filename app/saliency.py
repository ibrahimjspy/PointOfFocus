import cv2
import numpy as np
import tempfile
import os
import requests

def load_image_from_url(url: str):
    """Download an image from URL into OpenCV format."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    arr = np.frombuffer(resp.content, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not decode image from URL: {url}")
    return img

def load_image_from_path(path: str):
    """Load an image from local path into OpenCV format."""
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at path: {path}")
    return img

def find_salient_point(img: np.ndarray):
    """
    Compute the centroid of the most salient region in a BGR image.
    Returns ((cx, cy), (width, height))
    """
    h, w = img.shape[:2]
    # downscale for speed
    small = cv2.resize(img, (w // 2, h // 2))
    sal = cv2.saliency.StaticSaliencySpectralResidual_create()
    success, salmap = sal.computeSaliency(small)
    if not success:
        raise RuntimeError("Saliency computation failed")
    salmap = (salmap * 255).astype("uint8")

    _, th = cv2.threshold(salmap, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        raise RuntimeError("No salient regions found")

    c = max(cnts, key=cv2.contourArea)
    M = cv2.moments(c)
    if M["m00"] == 0:
        raise RuntimeError("Zero-area contour encountered")
    # scale back up
    cx = int((M["m10"] / M["m00"]) * 2)
    cy = int((M["m01"] / M["m00"]) * 2)
    return (cx, cy), (w, h)
