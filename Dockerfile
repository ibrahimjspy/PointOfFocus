# Use a slim Python base
FROM python:3.12-slim

# Install system deps for OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /usr/src/app

# Copy and install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Expose port
EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.main:app"]
