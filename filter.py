def censor(sentence="", hash_table={}):
    """
    Censor sentence based on provided hash table
    """

    new_sentence = ""

    for word in sentence.split():
        if word[0] in hash_table.keys():
            if word in hash_table[word[0]]:
                new_sentence += '*' * len(word) + ' '
            else:
                new_sentence += word + ' '
        else:
            new_sentence += word + ' '

    return new_sentence[:-1]  # [:-1] deletes space at the end
