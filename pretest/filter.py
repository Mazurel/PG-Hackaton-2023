from unicodedata import normalize

from typing import TextIO
from generator import word_variances_alg

def _append_word_to_hash(word: str, hash: dict):
    key = word[0]
    words = hash.get(key, []) + [word]
    hash[key] = words

def create_profanty_table(file: TextIO, generate_variations=False) -> dict:
    """
    Create hash table required, for profanity lookups.
    """
    data = file.read()
    data = data.split('\n')
    data = map(lambda word: word.strip(), data)
    data = filter(lambda word: len(word) > 0, data)
    profanity_hash = {}
    for word in data:
        if generate_variations:
            append_curse(word, profanity_hash)
        else:
            _append_word_to_hash(word, profanity_hash)
    return profanity_hash


def unpolish_word(word: str) -> str:
    return normalize("NFKD", word).encode("ascii", "ignore").decode("ASCII")


def censor(sentence="", hash_table={}):
    """
    Censor sentence based on provided hash table
    """

    new_sentence = ""

    for word in sentence.split():
        lowered_word = unpolish_word(word.lower())
        first_letter = lowered_word[0]
        if first_letter in hash_table.keys():
            if lowered_word in hash_table[first_letter]:
                new_sentence += '*' * len(word) + ' '
            else:
                new_sentence += word + ' '
        else:
            new_sentence += word + ' '

    return new_sentence[:-1]  # [:-1] deletes space at the end


def append_curse(word: str, profanity_hash: dict) -> dict:
    """
    Append new curs word to provided profanity_hash
    """
    word = word.lower().strip()
    similar_words = word_variances_alg(word)
    for word in similar_words:
        _append_word_to_hash(word, profanity_hash)
    return profanity_hash
