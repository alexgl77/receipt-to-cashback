# Dockerfile for Hugging Face Spaces (Docker SDK).
# HF Spaces removed the Streamlit SDK in 2025; Streamlit apps now ship
# inside a Docker container. The Space's runtime expects the process
# to listen on port 7860, which is what `streamlit run` is told below.

FROM python:3.13-slim

# System libs:
#   libgl1 + libglib2.0-0 : opencv (used by easyocr)
#   libsm6 libxext6       : extra X libs some easyocr wheels need
#   git                   : a few pip installs need it
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        git \
    && rm -rf /var/lib/apt/lists/*

# Run as a non-root user — HF Spaces best practice.
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# Install Python deps first so layer caches when only source changes.
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the repo (respects .dockerignore if present).
COPY --chown=user:user . .

USER user

# HF Spaces convention: listen on 0.0.0.0:7860.
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=7860 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false \
    STREAMLIT_SERVER_FILEWATCHERTYPE=none \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1

EXPOSE 7860

CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=7860", "--server.address=0.0.0.0"]
