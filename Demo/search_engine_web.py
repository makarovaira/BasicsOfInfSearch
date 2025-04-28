from flask import Flask, request, render_template
import os
import numpy as np
from collections import Counter
from nltk.tokenize import RegexpTokenizer
from pymorphy3 import MorphAnalyzer

# Создаём экземпляр веб-приложения Flask
app = Flask(__name__)

# Пути к данным
TFIDF_DIR = "tfidf_lemmas"
INDEX_FILE = "index.txt"

# Инициализация токенизатора и морфоанализатора
tokenizer = RegexpTokenizer(r'\b[а-яА-ЯёЁ]{2,}\b')
morph = MorphAnalyzer()

# Стоп-слова (которые не учитываются в запросах)
stop_words = set(["и", "в", "на", "по", "за", "с", "к", "из", "от", "у", "о", "а", "до", "не", "что", "он", "она"])

# Загрузка index.txt
def load_index():
    index_map = {}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                number, url = line.strip().split(":", 1)
                index_map[f"page_{number.strip()}.txt"] = url.strip()
    return index_map

# Загрузка всех tf-idf файлов
def load_documents():
    docs = {}
    for filename in os.listdir(TFIDF_DIR):
        tfidf = {}
        with open(os.path.join(TFIDF_DIR, filename), "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3:
                    term, _, tfidf_val = parts
                    tfidf[term] = float(tfidf_val)
        docs[filename] = tfidf
    return docs

# Восстановление idf по документам
def extract_idf(all_docs):
    idf_dict = {}
    for tfidf_dict in all_docs.values():
        for term, tfidf_val in tfidf_dict.items():
            if term not in idf_dict:
                tf = tfidf_val  # tfidf = tf * idf
                if tf > 0:
                    idf_dict[term] = tfidf_val / tf
    return idf_dict

# Токенизация запроса
def tokenize(text):
    tokens = tokenizer.tokenize(text.lower())
    return [t for t in tokens if t not in stop_words]


# Лемматизация токенов
def lemmatize(tokens):
    return [morph.parse(token)[0].normal_form for token in tokens]

# Обработка запроса: подсчёт tf-idf запроса
def process_query(query, idf_dict):
    tokens = tokenize(query)
    lemmas = lemmatize(tokens)
    lemma_counts = Counter(lemmas)
    total = sum(lemma_counts.values())
    tf = {lemma: count / total for lemma, count in lemma_counts.items()}
    return {lemma: tf[lemma] * idf_dict.get(lemma, 0.0) for lemma in tf}

# Построение общего словаря всех терминов
def build_vocab(docs):
    vocab = set()
    for tfidf_dict in docs.values():
        vocab.update(tfidf_dict)
    return sorted(vocab)


# Векторизация одного документа или запроса
def vectorize(tfidf_dict, vocab):
    return np.array([tfidf_dict.get(term, 0.0) for term in vocab])


# Вычисление косинусного сходства двух векторов
def cosine_similarity(vec1, vec2):
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Основной маршрут сайта: страница поиска
@app.route("/", methods=["GET", "POST"])
def search():
    results = [] # Список найденных документов
    query = "" # Строка запроса
    if request.method == "POST":
        query = request.form["query"]

        # Загрузка всех данных
        all_docs = load_documents()
        idf_dict = extract_idf(all_docs)
        vocab = build_vocab(all_docs)
        query_vec = vectorize(process_query(query, idf_dict), vocab)
        index_map = load_index()

        # Для каждого документа считаем его "похожесть" на запрос
        for filename, tfidf_dict in all_docs.items():
            doc_vec = vectorize(tfidf_dict, vocab)
            score = cosine_similarity(query_vec, doc_vec)
            results.append({
                "filename": filename,
                "score": round(score, 4),
                "url": index_map.get(filename, "ссылка не найдена")
            })

        # Ранжируем по убыванию оценки и берём топ-10 документов
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:10]

    # Отрисовка HTML страницы с результатами
    return render_template("search.html", results=results, query=query)

# Запуск сервера Flask
if __name__ == "__main__":
    app.run(debug=True)
