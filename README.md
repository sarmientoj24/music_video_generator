# Music Video Generator with DALLE2 and WhisperX

## Overview
This Python application generates a music video from a song by extracting audio from a YouTube video, transcribing the lyrics using OpenAI's WhisperX, and generating images for each lyrics using DALLE2. The user can choose the style for the images, and the application is built with a Streamlit user interface for easy use.

## Features
- Allows Youtube URL or Song Title
- Up to Eight Minutes Song Duration
- Transcribes the lyrics using OpenAI's WhisperX and aligns the words with the timestamps of the lyrics
- Generates an image for each lyrics using DALLE2, with user-selectable styles such as impressionist, anime, abstract, and more
- Built with a Streamlit user interface for an easy and intuitive experience

## Requirements
- Python 3.x
- Streamlit
- FFmpeg
- OpenAI's WhisperX
- DALLE2

## Requirements
- Python 3.9+
- Streamlit
- See `requirements.txt`

## Usage (Local)
- Clone the repository
- Install the required packages by running `pip install -r requirements.txt`
- Set Open API key
    ```
        export API_KEY=YOUR_KEYS_HERE
    ```
- Start the application
    ```
        streamlit run app.py
    ```
- Go to localhost:8501 on your browser

## Deploy using Docker
- Build docker `docker build -t music_video:latest`
- Run via
    ```
        docker run -it --gpus=all -e "API_KEY=YOUR_API_KEY" -p 8501:8501 music_video:latest
    ```
- Go to `http://localhost:8501/` in your browser
- Input the YouTube URL or the song title, choose the image style, and enjoy the generated music video!

## Conclusion
This Music Video Generator is a unique and innovative application that combines the power of OpenAI's WhisperX, DALLE2, and Streamlit to generate a music video from a song. With its user-friendly interface, anyone can quickly and easily generate a music video with custom images to match the lyrics. Try it out today and bring your favorite songs to life!
