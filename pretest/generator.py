import re
import random
import itertools

def word_variances_alg(word):
    
    # changing polish chars
    word = word.replace('ą','a').replace('ę', 'e').replace('ź','z').replace('ż', 'z').replace('ó','o').replace('ł', 'l').replace('ć','c').replace('ń','n').replace('ś','s')
    
    dictionary_no_big_letters = {'o':'0','b':'8','s':'5','e':'3','g':'9','z':'2','a':'4','u':'v','w':'vv','l':'I','I':'l', 'a': '@'}

    word_variances = []
    lista = []
    output= []
    length = 20
    
    for i in range(length):
        lista.append(word)
    for key,value in dictionary_no_big_letters.items(): #loop which creating words with changed letters one by one from the first letter to the last letter
        for j in range(0,10):
             for i in range(0,length):
                    output = re.sub(key, value, lista[i], j)
                    word_variances.append(output)
    for key,value in dictionary_no_big_letters.items(): #loop which creating  words with changed letters one by one from the last letter to the first letter
        for j in range(0,10):
             for i in range(0,length):
                    regex = key + "(?!.*" + key + ")" 
                    output2 = re.sub(regex, value, lista[i], j)
                    word_variances.append(output2)
                       
    full_list = []
    
    test_keys = list(dictionary_no_big_letters)
    test_values = list(dictionary_no_big_letters.values())        
    res = [(x, y) for idx, x in enumerate(test_keys) for y in test_keys[idx + 1: ]]
    res2 = [(x, y) for idx, x in enumerate(test_values) for y in test_values[idx + 1: ]]
    
    for i in range(len(res)): #loop which creates combinations of 2 letters
        list_out = [element.replace(res[i][0],res2[i][0]).replace(res[i][1],res2[i][1]) for element in lista]
        full_list += list_out
    word_variances = word_variances + full_list
    res = [(x, y,z) for idx, x in enumerate(test_keys) for y in test_keys[idx + 1: ] for z in test_keys[idx+2:]]
    res2 = [(x, y,z) for idx, x in enumerate(test_values) for y in test_values[idx + 1: ] for z in test_values[idx+2:]]
    # for i in range(len(res)): #loop which creates combinations of 3 letters
    #     list_out = [element.replace(res[i][0],res2[i][0]).replace(res[i][1],res2[i][1]).replace(res[i][2],res2[i][2]) for element in lista]
    #     full_list += list_out
    #     word_variances = word_variances + full_list

    for i in range(len(word)): #loop which generates words with double letter
        full_list.append(word[0:i]+word[i-1]+word[i:len(word)])
    word_variances = word_variances + full_list

    return list(set(word_variances))

# To regenerate cache, run:
# python generator.py dataset/wulgaryzmy.txt dataset/wulgaryzmy-cache.txt
if __name__ == "__main__":
    from argparse import ArgumentParser
    from pathlib import Path
    import io

    from tqdm import tqdm

    parser = ArgumentParser()
    parser.add_argument("src", type=Path, help="Source file.")
    parser.add_argument("dst", type=Path, help="Destination file.")
    args = parser.parse_args()

    src = args.src
    dst = args.dst

    with io.open(src.as_posix(), mode="r", encoding="utf-8") as f_in,\
         io.open(dst.as_posix(), mode="w", encoding="utf-8") as f_out:
        for word in tqdm(f_in.readlines()):
            if len(word) <= 0:
                continue
            for word_variant in word_variances_alg(word):
                f_out.write(f"{word_variant}")
