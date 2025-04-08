from os import listdir, path
from bs4 import BeautifulSoup


STORAGE_PATH = 'D:/учеба/ОИП/Homework1/downloaded_pages'
LEMMAS_PATH = 'D:/учеба/ОИП/Homework1/lemmas'
INVERTED_INDEX_PATH = 'D:/учеба/ОИП/Homework1/inverted_index.txt'

def get_texts():
    texts = dict()
    for file_name in listdir(STORAGE_PATH):
        with open(path.join(STORAGE_PATH, file_name), 'r', encoding='utf-8') as f:
            text = BeautifulSoup(f, features='html.parser').get_text().lower()
            f.close()
            texts[file_name] = text
    return texts


def get_lemmas():
    lemmas = dict()
    for file_name in listdir(LEMMAS_PATH):
        with open(path.join(LEMMAS_PATH,file_name), 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.read().splitlines()
            for l in lines:
                splitted = l.split(" ")
                lemmas[splitted[0]] = splitted[1:]
    return lemmas

def build_index():
    inverted_index = dict()
    lemmas = get_lemmas()
    texts = get_texts()

    for key, lemmas in lemmas.items():
        for file_name, text in texts.items():
            if any([l in text for l in lemmas]):
                if key not in inverted_index:
                    inverted_index[key] = set()
                inverted_index[key].add(file_name)

    for key in inverted_index.keys():
        inverted_index[key] = list(inverted_index[key])

    with open(INVERTED_INDEX_PATH, 'w+', encoding='utf-8') as index:
        for key, files in inverted_index.items():
            index.write(key + ' ' + str(files) + '\n')


if __name__ == "__main__":
    build_index()