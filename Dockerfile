# Dockerfile
# Runs (app.py, extract.py, genre_discogs400.py)
# in a Linux container, since Essentia has no official Windows PyPI wheels.
#
# Build (from PowerShell/cmd, in the project root):
#   docker build -t museko .
#
# Run:
#   docker run -it --rm -p 5000:5000 museko
#
#
# Docker Desktop for Windows with the WSL2 backend enabled
# (Docker Desktop > Settings > General > "Use the WSL 2 based engine").


FROM python:3.14-slim
 
# ffmpeg is needed by yt-dlp's audio postprocessor.
# libsndfile1 backs librosa/soundfile's audio decoding.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*
 
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
 
COPY . .

ENV FLASK_ENV=development

EXPOSE 5000
 
CMD ["flask", "--app", "apps/web/app.py", "run", "--host=0.0.0.0"]