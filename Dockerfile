FROM python:3.9.4-buster

RUN apt-get update && \
    apt-get install -y fonts-symbola fonts-droid-fallback fonts-dejavu

RUN pip install --no-cache-dir tty2img moviepy pyte pillow fclist-cffi freetype-py

COPY asciicast2movie.py tty2img.py /app/
ENTRYPOINT ["python3", "/app/asciicast2movie.py"]

WORKDIR /data/
