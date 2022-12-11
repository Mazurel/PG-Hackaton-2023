from unicodedata import normalize

from typing import TextIO
from generator import word_variances_alg

def create_profanty_table(file: TextIO) -> dict:
    """
    Create hash table required, for profanity lookups.
    """
    data = file.read()
    data = data.split('\n')
    profanity_hash = {}
    for word in data[:-1]:
        key = word[0]
        if key in profanity_hash.keys():
            profanity_hash[key].append(word)
        else:
            profanity_hash[key] = [word]
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


def add_words(word: str, profanity_hash: dict) -> dict:
    """
    Append new curs words to provided profanity_hash
    """
    word = word.lower()
    similar_words = word_variances_alg(word)
    for word in similar_words:
        key = word[0]
        if key in profanity_hash.keys():
            if word not in profanity_hash[key]:
                profanity_hash[key].append(word)
        else:
            profanity_hash[key] = [word]

    return profanity_hash
