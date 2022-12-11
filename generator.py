import re
import random
import itertools


def word_variances_alg(word):
    # changing polish chars
    word = word.replace('ą', 'a').replace('ę', 'e').replace('ź', 'z').replace('ż', 'z').replace('ó', 'o').replace('ł',
                                                                                                                  'l').replace \
        ('ć', 'c').replace('ń', 'n').replace('ś', 's')

    dictionary_no_big_letters = {'o': '0', 'b': '8', 's': '5', 'e': '3', 'g': '9', 'z': '2', 'a': '4', 'u': 'v'
        , 'w': 'vv', 'l': 'I', 'I': 'l'}
    dictionary = {'o': '0', 'O': '0', 'b': '8', 'B': '8', 's': '5', 'S': '5', 'e': '3', 'E': '3', 'G': '6', 'g': '9'
        , 'z': '2', 'Z': '2', 'a': '@', 'A': '4', 'T': '7', 'u': 'v', 'w': 'vv', 'l': 'I', 'I': 'l'}

    list_keys = list(dictionary_no_big_letters.keys())
    list_values = list(dictionary_no_big_letters.values())
    word_variances = []
    lista = []
    output = []
    length = 20
    for i in range(length):
        lista.append(word)
    for key, value in dictionary_no_big_letters.items():  # loop which creating words with changed letters one by one from the first letter to the last letter
        for j in range(0, 10):
            for i in range(0, length):
                output = re.sub(key, value, lista[i], j)
                word_variances.append(output)
    for key, value in dictionary_no_big_letters.items():  # loop which creating  words with changed letters one by one from the last letter to the first letter
        for j in range(0, 10):
            for i in range(0, length):
                regex = key + "(?!.*" + key + ")"
                output2 = re.sub(regex, value, lista[i], j)
                word_variances.append(output2)

    full_list = []
    mapIndexPosition = list(zip(list_keys, list_values))
    random.shuffle(mapIndexPosition)
    list_keys_1, list_values_1 = zip \
        (*mapIndexPosition)  # shuffeling of lists of keys and values(with no missing indexes) to make combination of two letters

    mapIndexPosition2 = list(zip(list_keys, list_values))
    random.shuffle(mapIndexPosition2)
    list_keys_2, list_values_2 = zip(*mapIndexPosition2)

    for elem in range(len(list_keys)):
        list_out = \
            [element.replace(list_keys[elem], list_values[elem]).replace(list_keys_1[elem],
                                                                         list_values_1[elem]).replace(
                list_keys_2[elem], list_values_2[elem]) for element in lista]
        full_list += list_out

    word_variances = word_variances + full_list  # filling a list with variances

    for elem in range(len(list_keys_1)):
        list_out = [
            element.replace(list_keys_1[elem], list_values_1[elem]).replace(list_keys_2[elem], list_values_2[elem]) for
            element in lista]
        full_list += list_out

    word_variances = word_variances + full_list

    mapIndexPosition = list(zip(list_keys, list_values))
    random.shuffle(mapIndexPosition)
    list_keys_1, list_values_1 = zip(*mapIndexPosition)

    mapIndexPosition2 = list(zip(list_keys, list_values))
    random.shuffle(mapIndexPosition2)
    list_keys_2, list_values_2 = zip(*mapIndexPosition2)

    for elem in range(len(list_keys_1)):
        list_out = [
            element.replace(list_keys_1[elem], list_values_1[elem]).replace(list_keys_2[elem], list_values_2[elem]) for
            element in lista]
        full_list += list_out

    word_variances = word_variances + full_list

    for elem in range(len(list_keys)):  # filling variances with
        list_out = [element.replace(list_keys[0], list_values[0]).replace(list_keys[1], list_values[1]) for element in
                    lista]
        full_list += list_out
    word_variances = word_variances + full_list

    for elem in range(len(list_keys)):
        list_out = [element.replace(list_keys[0], list_values[0]).replace(list_keys[6], list_values[6]) for element in
                    lista]
        full_list += list_out
    word_variances = word_variances + full_list

    for elem in range(len(list_keys)):
        list_out = [element.replace(list_keys[3], list_values[3]).replace(list_keys[6], list_values[6]) for element in
                    lista]
        full_list += list_out
    word_variances = word_variances + full_list

    for elem in range(len(list_keys)):
        list_out = [
            element.replace(list_keys[3], list_values[3]).replace(list_keys[6], list_values[6]).replace(list_keys[0],
                                                                                                        list_values[0])
            for element in lista]
        full_list += list_out
    word_variances = word_variances + full_list

    for i in range(len(word)):  # loop which generates words with space gaps every letter
        full_list.append(word[0:i] + " " + word[i:len(word)])
    word_variances = word_variances + full_list
    for i in range(len(word)):  # loop which generates words with double letter
        full_list.append(word[0:i] + word[i - 1] + word[i:len(word)])
    word_variances = word_variances + full_list

    return list(set(word_variances))
