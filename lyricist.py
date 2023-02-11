import os
import re

import whisperx

from text_cleaner import BasicLyricsCleaner


def generate_aligned_lyrics_timestamp(timestamps, audio_length, clean_title):
    """
    Generate aligned lyrics timestamp.

    Args:
        timestamps (list): List of timestamps.
        audio_length (float): Length of audio.
        clean_title (str): Cleaned title of song.
    Returns:
        aligned_lyrics (list): List of aligned lyrics.
    """
    lyrics_cleaner = BasicLyricsCleaner()

    all_starts = [0] + [round(segment["start"], 1) for segment in timestamps]

    clean_title = lyrics_cleaner.clean(
        clean_title, convert_verbs=True, replace_pronouns=False, correct_spelling=False
    )

    lyrics = [clean_title]

    for segment in timestamps:
        text = segment["text"]

        # clean text
        text = lyrics_cleaner.clean(text)

        if len(text.split()) < 3:
            text = text + f" {clean_title} "

        lyrics.append(text)

    ends = []
    for i in range(len(all_starts) - 1):
        end = all_starts[i + 1]
        ends.append(end)

    ends.append(round(timestamps[-1]["end"], 1))

    # add ending
    all_starts.append(ends[-1])
    lyrics.append(clean_title)
    ends.append(audio_length)

    timestamps = []
    for i in range(len(all_starts)):
        timestamps.append({"start": all_starts[i], "end": ends[i], "lyrics": lyrics[i]})

    return timestamps


def load_whisper(model="base", device="cuda", download_root=None):
    if download_root is None:
        download_root = os.path.join(os.path.expanduser("~"), ".cache")
    model = whisperx.load_model(model, device, download_root=download_root)
    return model


def transcribe_audio_segments(audio_file, model, device="cuda"):
    result = model.transcribe(audio_file, fp16=True, verbose=False)
    model_a, metadata = whisperx.load_align_model(language_code="en", device=device)
    result_aligned = whisperx.align(
        result["segments"], model_a, metadata, audio_file, device
    )
    return result_aligned["segments"]
