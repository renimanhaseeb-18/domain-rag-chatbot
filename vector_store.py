import os, json, pickle, warnings
from functools import lru_cache
import numpy as np
import faiss

MODEL_NAME = "all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def _load_sbert(name=MODEL_NAME):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(name)

class SBertEmbedder:
    # Main embedder: Sentence Transformers all-MiniLM-L6-v2 (384 dimensions, normalised)
    name = "sbert"
    def __init__(self, model_name=MODEL_NAME):
        self.model = _load_sbert(model_name)
    def encode(self, texts):
        return np.asarray(self.model.encode(list(texts), normalize_embeddings=True, show_progress_bar=False), dtype="float32")
    def fit_encode(self, texts):
        return self.encode(texts)
    def encode_query(self, q):
        return self.encode([q])

class TfidfEmbedder:
    # Backup only, used when the Sentence Transformers model cannot be downloaded
    name = "tfidf"
    def __init__(self):
        self.vec = None
    def fit_encode(self, texts):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True, max_features=5000)
        return self.vec.fit_transform(list(texts)).toarray().astype("float32")
    def encode_query(self, q):
        return self.vec.transform([q]).toarray().astype("float32")

def make_embedder(backend="auto"):
    if backend in ("auto", "sbert"):
        try:
            return SBertEmbedder()
        except Exception as e:
            if backend == "sbert":
                raise
            warnings.warn(f"Sentence Transformers model unavailable ({e}). Using TF-IDF backup embeddings.")
    return TfidfEmbedder()

class VectorStore:
    def __init__(self, backend="auto"):
        self.backend, self.embedder, self.index, self.chunks = backend, None, None, []

    def build(self, chunks):
        if not chunks:
            raise ValueError("No text chunks to index.")
        self.embedder = make_embedder(self.backend)
        vecs = self.embedder.fit_encode([c["text"] for c in chunks])
        self.index = faiss.IndexFlatIP(vecs.shape[1])      # inner product of normalised vectors = cosine similarity
        self.index.add(vecs)
        self.chunks = chunks
        return vecs.shape

    def search(self, query, k=4, doc_filter=None):
        qv = self.embedder.encode_query(query)
        n = self.index.ntotal
        scores, ids = self.index.search(qv, n if doc_filter else min(k, n))
        out = []
        for s, i in zip(scores[0], ids[0]):
            if i < 0:
                continue
            c = self.chunks[i]
            if doc_filter and c["source"] not in doc_filter:
                continue
            out.append({**c, "score": float(s)})
            if len(out) == k:
                break
        return out

    def save(self, folder):
        os.makedirs(folder, exist_ok=True)
        faiss.write_index(self.index, os.path.join(folder, "index.faiss"))
        json.dump(self.chunks, open(os.path.join(folder, "chunks.json"), "w"))
        json.dump({"backend": self.embedder.name}, open(os.path.join(folder, "meta.json"), "w"))
        if self.embedder.name == "tfidf":
            pickle.dump(self.embedder.vec, open(os.path.join(folder, "tfidf.pkl"), "wb"))

    @classmethod
    def load(cls, folder):
        vs = cls()
        meta = json.load(open(os.path.join(folder, "meta.json")))
        vs.index = faiss.read_index(os.path.join(folder, "index.faiss"))
        vs.chunks = json.load(open(os.path.join(folder, "chunks.json")))
        if meta["backend"] == "sbert":
            vs.embedder = SBertEmbedder()
        else:
            vs.embedder = TfidfEmbedder()
            vs.embedder.vec = pickle.load(open(os.path.join(folder, "tfidf.pkl"), "rb"))
        return vs
