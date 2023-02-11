import os

import spacy
from whisperx import _MODELS, _download

DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), ".cache")
_download(_MODELS["medium.en"], DOWNLOAD_DIR, False)
spacy.load("en_core_web_sm")
