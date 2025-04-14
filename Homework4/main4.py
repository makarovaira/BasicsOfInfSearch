import os
import math
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import RegexpTokenizer
from pymorphy3 import MorphAnalyzer

# ─── Настройки ───────────────────────────────────────────────
nltk.download('punkt')  # только на всякий случай
morph = MorphAnalyzer()
tokenizer = RegexpTokenizer(r'\b[а-яА-ЯёЁ]{2,}\b')

# Папки
DATA_DIR = "downloaded_pages"
TOKENS_DIR = "tokens"
LEMMAS_DIR = "lemmas"
TFIDF_TERMS_DIR = "tfidf_terms"
TFIDF_LEMMAS_DIR = "tfidf_lemmas"

os.makedirs(TOKENS_DIR, exist_ok=True)
os.makedirs(LEMMAS_DIR, exist_ok=True)
os.makedirs(TFIDF_TERMS_DIR, exist_ok=True)
os.makedirs(TFIDF_LEMMAS_DIR, exist_ok=True)

# Стоп-слова
stop_words = set(["и", "в", "на", "по", "за", "с", "к", "из", "от", "у", "о", "а", "до", "не", "что", "он", "она"])

# ─── Обработка текста ────────────────────────────────────────

def is_valid_token(token):
    return token.isalpha() and token.lower() not in stop_words

def tokenize(text):
    tokens = tokenizer.tokenize(text.lower())
    return [t for t in tokens if is_valid_token(t)]

def lemmatize(tokens):
    lemma_map = defaultdict(list)
    for token in tokens:
        lemma = morph.parse(token)[0].normal_form
        lemma_map[lemma].append(token)
    return lemma_map

def compute_tf(term_counts):
    total_terms = sum(term_counts.values())
    return {term: count / total_terms for term, count in term_counts.items()}

def compute_idf(all_docs_term_counts):
    N = len(all_docs_term_counts)
    df = Counter()
    for term_counts in all_docs_term_counts:
        df.update(set(term_counts))
    return {term: math.log(N / (1 + df[term])) for term in df}

# ─── Обработка всех документов ───────────────────────────────

all_term_counts = []
all_lemma_counts = []
documents = []

file_list = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]

for filename in file_list:
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()

    tokens = tokenize(text)
    term_count = Counter(tokens)
    all_term_counts.append(term_count)
    documents.append(tokens)

    # Сохраняем токены
    with open(f"{TOKENS_DIR}/{filename}", "w", encoding="utf-8") as f:
        for token in sorted(set(tokens)):
            f.write(f"{token}\n")

    # Лемматизация
    lemma_map = lemmatize(tokens)
    lemma_counts = {lemma: len(forms) for lemma, forms in lemma_map.items()}
    all_lemma_counts.append(lemma_counts)

    with open(f"{LEMMAS_DIR}/{filename}", "w", encoding="utf-8") as f:
        for lemma, forms in lemma_map.items():
            f.write(f"{lemma} {' '.join(forms)}\n")

# ─── Расчёт IDF и TF-IDF ─────────────────────────────────────

term_idf = compute_idf(all_term_counts)
lemma_idf = compute_idf(all_lemma_counts)

for i, (term_count, lemma_count) in enumerate(zip(all_term_counts, all_lemma_counts)):
    tf_terms = compute_tf(term_count)
    tf_lemmas = compute_tf(lemma_count)

    filename = file_list[i]

    with open(f"{TFIDF_TERMS_DIR}/{filename}", "w", encoding="utf-8") as f:
        for term, tf in tf_terms.items():
            idf = term_idf.get(term, 0)
            tfidf = tf * idf
            f.write(f"{term} {idf:.6f} {tfidf:.6f}\n")

    with open(f"{TFIDF_LEMMAS_DIR}/{filename}", "w", encoding="utf-8") as f:
        for lemma, tf in tf_lemmas.items():
            idf = lemma_idf.get(lemma, 0)
            tfidf = tf * idf
            f.write(f"{lemma} {idf:.6f} {tfidf:.6f}\n")

print("Обработка завершена.")
