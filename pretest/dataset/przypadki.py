from pathlib import Path

def generate_alterations(dictionary: Path, curse_words: Path, output: str = 'wulgaryzmy.txt'):
    """Generate text file with altered base words. 
    Alterations are based on the dictionary.
    
    Parameters
    ----------

    dictionary [Path] - path to text file with dictionary content.
    The file can be downloaded from here: https://sjp.pl/sl/odmiany/

    curse_words [Path] - path to file with curse words collected from Wikipedia

    output [str] - name of the file in which altered dictionary will be saved
    """

    if not dictionary.is_file():
        raise ValueError("Specified dictionary path is not a file!")

    # Load curse words
    with open(curse_words, 'r') as f:
        wulgar = f.readlines()

    new_wulg = []
    for wulg in wulgar:
        new_wulg.append(wulg.strip(' \n'))

    with open(dictionary, 'r') as file, open(output, 'w') as out:
        for line in file.readlines():
            # Remove spaces and newlines from dictionary and split it
            words = line.replace(" ", "").replace('\n', "").split(',')

            # Find curses for which there are alterations in the dictionary
            for wulg in wulgar:
                if wulg.strip(' \n') == words[0]:
                    print(f"Extending curses for word: {words[0]}")
                    new_wulg.extend(words[1:])
                    break
            # Save alterations to file    
            for wulg in new_wulg:
                out.write(wulg + '\n')

            new_wulg = []

if __name__ == "__main__":

    # Specify path to the dictionary file
    dictionary = Path("")
    curse_words = Path("./data")
    generate_alterations(dictionary, curse_words)