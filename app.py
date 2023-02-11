import os
import re

import streamlit as st

from dalle import DALLEGenerator
from generator import generate_from_lyrics
from lyricist import (
    generate_aligned_lyrics_timestamp,
    load_whisper,
    transcribe_audio_segments,
)
from movie import create_video_clip_from_images, merge_audio_and_video
from search import search_youtube
from text_cleaner import get_clean_title
from youtube import YoutubeDownloader

# Variables
REGEX = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
DOWNLOAD_PATH = os.path.join(os.getcwd(), "downloads")
DEFAULT_THUMB = os.path.join(os.getcwd(), "assets", "default-thumb.png")
DEFAULT_GENERATION_TIME = 7
MAX_DURATION = 480
DOWNLOAD_PATH = "songs"
IMAGES_PATH = "generated"
WHISPER_MODEL = "medium.en"
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), ".cache")


@st.cache()
def load_application_model(model_name=WHISPER_MODEL):
    model = load_whisper(model_name, download_root=DOWNLOAD_DIR)
    return model


model = load_application_model()
generator = DALLEGenerator()

st.title("Smart Music Video Creator")
st.header("Create an alternative generated art music video")
st.text("By James Andrew")

st.info("Maximum Song Length is eight minutes.", icon="🤖")
st.warning(
    "I'm using a small server. You may encounter errors as the concurrent users increase. Apologies!",
    icon="🤖",
)

song = st.text_input("Youtube URL / Song Title", "")
artstyle = st.selectbox(
    "Art Style",
    (
        "Impressionist",
        "Photorealistic",
        "Expressionist",
        "Surrealist",
        "Cubist",
        "PopArt",
        "Anime",
        "SciFi",
        "Abstract",
    ),
)


if st.button("Submit"):
    if re.match(REGEX, song):
        youtube_url = song
    else:
        youtube_url = search_youtube(song)

        if not youtube_url:
            st.error("No results found!")
            st.stop()

    if youtube_url and not re.match(REGEX, youtube_url):
        st.error("Invalid URL!")
        st.stop()

    ytd = YoutubeDownloader(youtube_url, DOWNLOAD_PATH)

    if ytd.duration > MAX_DURATION:
        st.error("Song is too long! Please select a song less than 5 minutes.")
        st.stop()

    title = ytd.title
    ecode1, thumbnail = ytd.get_video_thumbnail()
    thumbnail = (
        thumbnail if ecode1 == 0 and os.path.isfile(thumbnail) else DEFAULT_THUMB
    )

    # Display info
    st.header(title)
    st.image(thumbnail, width=480)

    # Create output directory
    hashname = abs(hash(ytd.title)) % (10**8)
    output_dir = os.path.join(IMAGES_PATH, str(hashname))
    os.makedirs(output_dir, exist_ok=True)

    # Dowloading
    with st.spinner("Downloading and converting to audio..."):
        ecode2, audio_path = ytd.download_video_to_mp3()

    if ecode2 != 0:
        st.error(
            "Failed on encoding! Either resumbit or select a different video. Sorry!"
        )
        st.stop()

    # Transcribe
    try:
        with st.spinner("Transcribing and realigning audio..."):
            segmented_transcriptions = transcribe_audio_segments(audio_path, model)
            aligned_lyrics = generate_aligned_lyrics_timestamp(
                segmented_transcriptions,
                ytd.duration,
                clean_title=get_clean_title(title),
            )
    except Exception as e:
        st.error(
            f"Error transcribing audio {str(e)}. This may be due to many concurrent users. Please try again after a minute..."
        )
        st.stop()

    # Generate images
    try:
        with st.spinner(
            f"Generating images. May take approx {int(len(aligned_lyrics)  * DEFAULT_GENERATION_TIME)}s.."
        ):
            aligned_lyrics_with_images = generate_from_lyrics(
                generator, aligned_lyrics, output_dir, artstyle=artstyle
            )
    except Exception as e:
        st.error(
            f"Error generating images: {str(e)}. This may be due to many concurrent users. Please try again after a minute..."
        )
        st.stop()

    # Generate music video
    mp4_path = os.path.join(DOWNLOAD_PATH, f"{ytd.title}.mp4")
    final_video_path = os.path.join(DOWNLOAD_PATH, f"{str(hashname)}.mp4")

    try:
        with st.spinner("Creating art music video"):
            create_video_clip_from_images(
                ytd.duration, aligned_lyrics_with_images, mp4_path
            )
            merge_audio_and_video(mp4_path, audio_path, final_video_path)
    except Exception as e:
        st.error(f"Error creating video {str(e)}")
        st.stop()

    st.text("Art Music Video")
    st.video(final_video_path)
