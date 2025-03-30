import os
import re
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import nltk
from pymorphy3  import MorphAnalyzer

# Папка с сохраненными страницами
input_folder = "downloaded_pages"

# Файлы для сохранения результатов
tokens_file = "tokens.txt"
lemmas_file = "lemmas.txt"

# Инициализация лемматизатора и стоп-слов
morph = MorphAnalyzer()
nltk.download('stopwords')
stop_words = set(stopwords.words("russian"))  # Для русского языка

# Регулярное выражение для поиска слов
word_pattern = re.compile(r"\b[а-яА-ЯёЁ]+\b")

# Множества для хранения токенов и лемм
tokens = set()
lemmas_dict = {}

# Функция для очистки текста от HTML-разметки
def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

# Функция для токенизации и очистки текста
def tokenize_and_clean(text):
    words = word_pattern.findall(text.lower())  # Ищем слова и приводим к нижнему регистру
    cleaned_words = [
        word for word in words
        if word not in stop_words  # Убираем стоп-слова
        and not any(char.isdigit() for char in word)  # Убираем слова с цифрами
    ]
    return cleaned_words

# Основной код
if __name__ == "__main__":
    # Очищаем файлы перед началом
    with open(tokens_file, "w", encoding="utf-8") as f:
        f.write("")
    with open(lemmas_file, "w", encoding="utf-8") as f:
        f.write("")

    # Обрабатываем каждый файл в папке
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        # Извлекаем текст из HTML
        text = extract_text_from_html(html_content)

        # Токенизируем и очищаем текст
        words = tokenize_and_clean(text)

        # Добавляем токены в множество
        tokens.update(words)

        # Лемматизируем токены
        for word in words:
            lemma = morph.parse(word)[0].normal_form
            if lemma not in lemmas_dict:
                lemmas_dict[lemma] = set()
            if word != lemma:
                lemmas_dict[lemma].add(word)

    # Сохраняем токены в файл
    with open(tokens_file, "w", encoding="utf-8") as f:
        for token in sorted(tokens):
            f.write(f"{token}\n")

    # Сохраняем леммы в файл
    with open(lemmas_file, "w", encoding="utf-8") as f:
        for lemma, words in sorted(lemmas_dict.items()):
            f.write(f"{lemma} {' '.join(sorted(words))}\n")

    print("Обработка завершена. Результаты сохранены в tokens.txt и lemmas.txt.")