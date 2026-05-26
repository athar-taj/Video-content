# Use official lightweight Python parent image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffer outputs for real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install only essential runtime system packages (no build/dev dependencies for local testing)
# - ffmpeg: media compositor runtime binary (required for rendering)
# - espeak-ng: runtime binary for text phonemization (required for local Kokoro TTS)
# - libsndfile1: C-library required for Python soundfile package
# - libgl1: required for opencv-python frame processing
#
# REMOVED FOR LOCAL TESTING (reasons):
# - build-essential: Unnecessary; C-extensions are installed from precompiled wheels.
# - git: Unnecessary; codebase is copied directly or mounted, no remote cloning needed.
# - pkg-config, libav*-dev: Unnecessary; PyAV (av>=13) uses precompiled wheels with statically linked FFmpeg.
# - libespeak-ng-dev: Unnecessary; phonemizer only requires the espeak-ng binary at runtime, not build headers.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    espeak-ng \
    libsndfile1 \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy dependency specifications
COPY requirements.txt .

# Install Python packages
# Install torch CPU-only first to avoid pulling the multi-GB CUDA wheel
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.2.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source files
COPY . .

# Ensure all default asset directories exist inside the container
RUN mkdir -p \
    assets/fonts \
    assets/videos/gameplay \
    assets/audio/raw \
    assets/audio/processed \
    assets/audio/temp \
    assets/videos/temp \
    assets/output \
    assets/subtitles \
    assets/ass \
    assets/overlays \
    logs

# Configure PYTHONPATH to import project modules
ENV PYTHONPATH=/app

# Default entry point
CMD ["python", "scripts/run_pipeline.py"]
