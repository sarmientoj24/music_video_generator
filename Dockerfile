FROM cnstark/pytorch:1.10.1-py3.9.12-cuda11.1.1-devel-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV API_KEY=''
ENV ENGINE=text-davinci-003
ENV TZ=Etc/UTC

# Install installation dependencies
RUN apt-get update -y && \
    apt-get install -y vim wget git zip htop screen build-essential tzdata ffmpeg


RUN git clone https://github.com/sarmientoj24/music_video_generator.git /app/music_video_generator

WORKDIR /app/music_video_generator
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/m-bain/whisperx.git

RUN python setup_whisper.py
RUN python -m spacy download en_core_web_sm
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "app.py"]
