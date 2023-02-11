import re

import pkg_resources
import spacy
from lemminflect import getInflection, getLemma
from symspellpy import SymSpell, Verbosity
from youtube_title_parse import get_artist_title

BASE_PRONOUNS_MAPPING = {
    "i": "person",
    "im": "person",
    "me": "person",
    "my": "person's",
    "mine": "someone's",
    "we": "people",
    "us": "people",
    "our": "people's",
    "ours": "people's",
    "you": "person",
    "your": "person's",
    "yours": "person's",
    "he": "someone",
    "him": "someone's",
    "his": "someone's",
    "himself": "someone",
    "she": "someone",
    "her": "someone's",
    "hers": "someone's",
    "herself": "someone",
    "they": "those people",
    "them": "those people",
    "their": "those people's",
    "theirs": "those people's",
}

STOPWORDS = ("am", "an", "re")


def get_clean_title(title):
    """
    Get the artist and title of a song.

    Args:
        title (str): Title of song.
    Returns:
    """
    try:
        artist, title = get_artist_title(title)
        return f"{title} {artist}".lower()
    except Exception:
        title = title.lower()
        # Remove special characters except space, apostrophe from title
        title = re.sub(r"[^a-zA-Z0-9\s']", "", title)
        # Remove lyrics, official video, etc. from title
        title = re.sub(r"lyrics|official video|official|video|lyric", "", title)
        return title


def get_inflection(word):
    """
    Get the inflection of a word.

    Args:
        word (str): Word to get inflection of.
    Returns:
        inflection (str): Inflection of word.
    """
    lemma = getLemma(word, upos="VERB")[0]
    inflection = getInflection(lemma, tag="VBG")[0]
    return inflection


class BasicLyricsCleaner:
    def __init__(self):
        print("Building cleaner...")
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

        dictionary_path = pkg_resources.resource_filename(
            "symspellpy", "frequency_dictionary_en_82_765.txt"
        )
        self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
        self.nlp = spacy.load("en_core_web_sm")

    def __convert_verbs_to_gerund(self, lyrics: str):
        """
        1. Parse string to get POS tags.
        2. For each instance of a verb, convert it to its gerund form using LemmInflect.
        3. Rewrite the string with the new verbs.

        e.g. "I love you" -> "I loving you"

        Args:
            lyrics (str): Song lyrics.
        Returns:
            lyrics (str): Song lyrics with verbs converted to gerund form.
        """
        doc = self.nlp(lyrics)
        new_lyrics = []
        for token in doc:
            if token.pos_ == "VERB":
                new_lyrics.append(get_inflection(token.text))
            else:
                new_lyrics.append(token.text)
        return " ".join(new_lyrics)

    def __remove_punctuation(self, lyrics: str):
        """
        Remove punctuation from lyrics.

        Args:
            lyrics (str): Song lyrics.
        Returns:
            lyrics (str): Song lyrics with punctuation removed.
        """
        return (
            lyrics.replace(",", " ")
            .replace(".", "")
            .replace("!", " ")
            .replace("?", " ")
        )

    def __convert_pronouns_to_person(self, lyric):
        """
        1. Parse string to get POS tags.
        2. For each instance of a pronoun,
            If pronoun is singular, convert to "person"
                e.g. "I" -> "person", "you" -> "person", "he" -> "person", "she" -> "person"
            If pronoun is it, do nothing.
            If pronoun is plural, convert to "people"
                e.g. "we" -> "people", "they" -> "people"
        3. Rewrite the string with the new pronouns.
        """
        doc = self.nlp(lyric)
        new_lyrics = []
        for token in doc:
            if token.pos_ == "PRON":
                if token.text in BASE_PRONOUNS_MAPPING:
                    new_lyrics.append(BASE_PRONOUNS_MAPPING[token.text])
                else:
                    new_lyrics.append(token.text)
            else:
                new_lyrics.append(token.text)
        return " ".join(new_lyrics)

    def __correct_spelling(self, lyrics: str):
        """
        Correct spelling for each word in lyrics using SymSpell.

        Args:
            lyrics (str): Song lyrics.
        Returns:
            lyrics (str): Song lyrics with spelling corrected.
        """

        # Split lyrics into words
        words = lyrics.split()

        # Correct spelling for each word
        new_words = []
        for word in words:
            new_words.append(
                self.sym_spell.lookup(
                    word, Verbosity.CLOSEST, max_edit_distance=2, include_unknown=True
                )[0].term
            )
        return " ".join(new_words)

    def __remove_filler_words(self, lyrics: str):
        """
        Remove filler words from lyrics.

        Args:
            lyrics (str): Song lyrics.
        Returns:
            lyrics (str): Song lyrics with filler words removed.
        """
        filler_words = [
            "yea",
            "yeah",
            "oh",
            "cmon",
            "ooh",
            "woah",
            "hmm",
            "mmmm",
            "ohh",
        ]
        lyrics = lyrics.split()
        new_lyrics = []
        for word in lyrics:
            if word not in filler_words:
                new_lyrics.append(word)
        return " ".join(new_lyrics)

    def __decontracted(self, phrase):
        """
        Decontracted words.

        Args:
            phrase (str): Phrase to decontract.
        Returns:
        """
        # specific
        phrase = re.sub(r"won\'t", "will not", phrase)
        phrase = re.sub(r"can\'t", "can not", phrase)

        # general
        phrase = re.sub(r"n\'t", " not", phrase)
        phrase = re.sub(r"\'re", " are", phrase)
        phrase = re.sub(r"\'s", " is", phrase)
        phrase = re.sub(r"\'d", " would", phrase)
        phrase = re.sub(r"\'ll", " will", phrase)
        phrase = re.sub(r"\'t", " not", phrase)
        phrase = re.sub(r"\'ve", " have", phrase)
        phrase = re.sub(r"\'m", " am", phrase)
        return phrase

    def __remove_stopwords(self, lyrics: str):
        """
        Remove stopwords from lyrics.

        Args:
            lyrics (str): Song lyrics.
        Returns:
            lyrics (str): Song lyrics with stopwords removed.
        """
        lyrics = lyrics.split()
        new_lyrics = []
        for word in lyrics:
            if word not in STOPWORDS and len(word) > 1:
                new_lyrics.append(word)
        return " ".join(new_lyrics)

    def clean(
        self,
        lyrics: str,
        convert_verbs=True,
        replace_pronouns=True,
        correct_spelling=True,
    ):
        """
        Clean lyrics.

        Args:
            lyrics (str): Song lyrics.
            convert_verbs (bool): Whether to convert verbs to gerund form.
            replace_pronouns (bool): Whether to replace pronouns with "person" or "people".
            correct_spelling (bool): Whether to correct spelling.
        Returns:
            lyrics (str): Cleaned song lyrics.
        """
        lyrics = lyrics.lower()
        lyrics = self.__remove_punctuation(lyrics)

        lyrics = self.__decontracted(lyrics)
        lyrics = self.__remove_filler_words(lyrics)

        if correct_spelling:
            lyrics = self.__correct_spelling(lyrics)

        if convert_verbs:
            lyrics = self.__convert_verbs_to_gerund(lyrics)

        if replace_pronouns:
            lyrics = self.__convert_pronouns_to_person(lyrics)

        lyrics = self.__remove_stopwords(lyrics)

        lyrics = lyrics.strip()

        return lyrics
