"""
Image Saliency Analysis Tool
=============================

This module provides utilities to:
- Load images from URLs or local file paths
- Compute and find the most salient point in an image using OpenCV's saliency detection

It utilizes OpenCV's `StaticSaliencyFineGrained` for visual attention modeling and determines
the most relevant region of an image based on visual contrast.

Dependencies:
- OpenCV (`cv2`)
- NumPy
- Requests
- Logging

Author: M Ibrahim
Date: 2025-05-19
"""

import cv2
import numpy as np
import tempfile
import os
import requests
import logging
import sys

# Configure logging for debug output
logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def load_image_from_url(url: str) -> np.ndarray:
    """
    Download and decode an image from a URL into OpenCV (BGR) format.

    Args:
        url (str): Direct link to an image file.

    Returns:
        np.ndarray: Image loaded in BGR format.

    Raises:
        requests.RequestException: If the image could not be downloaded.
        ValueError: If the image could not be decoded.
    """
    logging.info(f"Loading image from URL: {url}")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    arr = np.frombuffer(resp.content, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not decode image from URL: {url}")
    logging.debug(f"Image loaded with shape: {img.shape}")
    return img


def load_image_from_path(path: str) -> np.ndarray:
    """
    Load an image from a local file path into OpenCV (BGR) format.

    Args:
        path (str): Local filesystem path to the image.

    Returns:
        np.ndarray: Image loaded in BGR format.

    Raises:
        FileNotFoundError: If the image cannot be loaded.
    """
    logging.info(f"Loading image from path: {path}")
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at path: {path}")
    logging.debug(f"Image loaded with shape: {img.shape}")
    return img


def find_salient_point(img: np.ndarray):
    """
    Find the most salient point (centroid of high-attention area) in an image.

    Uses OpenCV's StaticSaliencyFineGrained algorithm to calculate the saliency map,
    smooths the result, thresholds it using Otsu's method, and then finds the centroid
    of the most significant contour.

    Args:
        img (np.ndarray): Input image in BGR format.

    Returns:
        Tuple[Tuple[int, int], Tuple[int, int]]:
            - (cx, cy): Coordinates of the most salient point.
            - (width, height): Size of the original image.

    Raises:
        RuntimeError: If saliency map computation fails.
    """
    logging.info("Starting salient point detection")
    logging.debug(f"Input image shape = {img.shape}")
    h, w = img.shape[:2]

    # Step 1: Downscale image for faster saliency computation
    small = cv2.resize(img, (w // 2, h // 2))
    sal = cv2.saliency.StaticSaliencyFineGrained_create()
    try:
        ok, salmap = sal.computeSaliency(small)
    except ValueError:
        salmap = sal.computeSaliency(small)
        ok = True
    if not ok:
        raise RuntimeError("Saliency computation failed")
    salmap = (salmap * 255).astype("uint8")
    logging.debug("Saliency map successfully computed")

    # Step 2: Apply Gaussian blur to reduce noise
    salmap = cv2.GaussianBlur(salmap, (7, 7), 0)

    # Step 3: Resize saliency map to original image size and normalize
    salmap = cv2.resize(salmap, (w, h), interpolation=cv2.INTER_LINEAR)
    salmap = cv2.normalize(salmap, None, 0, 255, cv2.NORM_MINMAX)

    # Step 4: Binarize using Otsu’s thresholding and remove noise
    _, th = cv2.threshold(salmap, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=2)

    # Step 5: Find external contours
    cnts_ret = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts_ret) == 3:
        _, cnts, _ = cnts_ret
    else:
        cnts, _ = cnts_ret
    logging.debug(f"Found {len(cnts)} external contours")

    # Step 6: Determine centroid of largest contour
    if cnts:
        c = max(cnts, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            logging.info(f"Salient point located at centroid: ({cx}, {cy})")
            return (cx, cy), (w, h)

    # Step 7: Fallback to most intense point in saliency map
    _, max_val, _, max_loc = cv2.minMaxLoc(salmap)
    logging.warning(
        f"No valid contour found. Falling back to max saliency location: {max_loc} (val={max_val})"
    )
    return max_loc, (w, h)
