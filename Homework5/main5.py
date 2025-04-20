import os
import numpy as np
from collections import defaultdict, Counter
from nltk.tokenize import RegexpTokenizer
from pymorphy3 import MorphAnalyzer

# ─── Настройки ─────────────────────────────────────────────
TFIDF_DIR = "tfidf_lemmas"
INDEX_FILE = "index.txt"    # формат: page1.txt https://...

tokenizer = RegexpTokenizer(r'\b[а-яА-ЯёЁ]{2,}\b')
morph = MorphAnalyzer()

stop_words = set(["и", "в", "на", "по", "за", "с", "к", "из", "от", "у", "о", "а", "до", "не", "что", "он", "она"])

# ─── Обработка запроса ─────────────────────────────────────

def tokenize(text):
    tokens = tokenizer.tokenize(text.lower())
    return [t for t in tokens if t not in stop_words]

def lemmatize(tokens):
    return [morph.parse(token)[0].normal_form for token in tokens]

# ─── Загрузка index.txt и возвращение словаря { 'page_1.txt': 'https://example.com', ... }

def load_index():
    index_map = {}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            try:
                number, url = line.split(":", 1)
                number = number.strip()
                url = url.strip()
                filename = f"page_{number}.txt"
                index_map[filename] = url
            except ValueError:
                continue
    return index_map


def load_documents():
    docs = {}
    for filename in os.listdir(TFIDF_DIR):
        filepath = os.path.join(TFIDF_DIR, filename)
        tfidf = {}
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3:
                    term, idf, tfidf_val = parts
                    tfidf[term] = float(tfidf_val)
        docs[filename] = tfidf
    return docs

def extract_idf(all_docs):
    idf_dict = {}
    for tfidf_dict in all_docs.values():
        for term, tfidf_val in tfidf_dict.items():
            if term not in idf_dict:
                tf = tfidf_val  # tf * idf = tfidf → idf = tfidf / tf
                if tf > 0:
                    idf_dict[term] = tfidf_val / tf
    return idf_dict

# ─── Построение векторов и поиск ───────────────────────────

def build_vocab(docs):
    vocab = set()
    for tfidf_dict in docs.values():
        vocab.update(tfidf_dict)
    return sorted(vocab)

def vectorize(tfidf_dict, vocab):
    return np.array([tfidf_dict.get(term, 0.0) for term in vocab])

def cosine_similarity(vec1, vec2):
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def process_query(query, idf_dict):
    tokens = tokenize(query)
    lemmas = lemmatize(tokens)
    lemma_counts = Counter(lemmas)
    total = sum(lemma_counts.values())
    tf = {lemma: count / total for lemma, count in lemma_counts.items()}
    tfidf_query = {lemma: tf[lemma] * idf_dict.get(lemma, 0.0) for lemma in tf}
    return tfidf_query

# ─── Поиск ──────────────────────────────────────────────────

def search(query, top_k=5):
    doc_index = load_index()
    all_docs = load_documents()
    vocab = build_vocab(all_docs)
    idf_dict = extract_idf(all_docs)

    query_vector = vectorize(process_query(query, idf_dict), vocab)

    results = []
    for doc_name, tfidf_dict in all_docs.items():
        doc_vector = vectorize(tfidf_dict, vocab)
        score = cosine_similarity(query_vector, doc_vector)
        results.append((doc_name, score))

    results.sort(key=lambda x: x[1], reverse=True)

    print(f"\n🔍 Результаты по запросу: «{query}»\n")
    for doc_name, score in results[:top_k]:
        link = doc_index.get(doc_name, "ссылка не найдена")
        print(f"{doc_name:25} | score: {score:.4f} | {link}")

# ─── Точка входа ────────────────────────────────────────────

if __name__ == "__main__":
    print("🔎 Поисковик запущен (используется TF-IDF из папки tfidf_lemmas)\n")
    while True:
        query = input("Введите запрос (или 'exit'): ").strip()
        if query.lower() == "exit":
            break
        search(query)
