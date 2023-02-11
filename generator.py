import os

from dalle import DALLEGenerator


def generate_from_lyrics(
    generator: DALLEGenerator, aligned_lyrics, out_dir, artstyle="impressionist"
):
    """
    Generate images from lyrics.

    Args:
        generator (DALLEGenerator): DALLE generator.
        aligned_lyrics (list): List of aligned lyrics.
        out_dir (str): Output directory.
        artstyle (str): Artstyle to use for generation.
    Returns:
        aligned_lyrics (list): List of aligned lyrics with image filenames.
    """

    artstyle = artstyle.lower()

    for i, ap in enumerate(aligned_lyrics):
        filename = os.path.join(out_dir, str(i).zfill(6) + ".jpg")
        aligned_lyrics[i]["filename"] = filename
        lyric = ap["lyrics"]
        image = generator.generate_image(lyric, style=artstyle)
        image.save(filename)
    return aligned_lyrics
