import os, re, time
from document_loader import load_pdf, chunk_pages
from vector_store import VectorStore
from prompt import build_messages, FALLBACK_MESSAGE

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
MIN_SCORE = {"sbert": 0.25, "tfidf": 0.18}          # below this similarity the chatbot refuses
INJECTION = re.compile(r"(ignore|forget|disregard).{0,30}(previous|above|prior|all).{0,20}(instruction|rule|prompt)|"
                       r"system prompt|reveal your (prompt|instructions)|you are now|act as (?!per)", re.I)

def call_llm(messages, api_key, model=DEFAULT_MODEL):
    from groq import Groq
    client = Groq(api_key=api_key)
    last = None
    for attempt in range(3):
        try:
            r = client.chat.completions.create(model=model, messages=messages, temperature=0, max_tokens=450)
            return r.choices[0].message.content.strip()
        except Exception as e:
            last = e
            if "429" in str(e) or "rate" in str(e).lower():
                time.sleep(6 * (attempt + 1)); continue
            raise
    raise last

class RAGPipeline:
    def __init__(self, chunk_size=800, chunk_overlap=120, top_k=4, min_score=None, api_key=None, model=DEFAULT_MODEL):
        self.chunk_size, self.chunk_overlap, self.top_k = chunk_size, chunk_overlap, top_k
        self.min_score, self.model = min_score, model
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.store, self.chunks, self.documents = None, [], []

    def ingest(self, files):
        # files: list of (filename, path_or_bytes). Returns a small stats dict.
        pages = []
        for name, src in files:
            p = load_pdf(src, name)
            pages.extend(p)
            self.documents.append(name)
        self.chunks = chunk_pages(pages, self.chunk_size, self.chunk_overlap)
        self.store = VectorStore()
        shape = self.store.build(self.chunks)
        return {"documents": len(files), "pages": len(pages), "chunks": len(self.chunks),
                "embedding_dim": shape[1], "backend": self.store.embedder.name}

    def threshold(self):
        return self.min_score if self.min_score is not None else MIN_SCORE.get(self.store.embedder.name, 0.2)

    def ask(self, question, doc_filter=None):
        t0 = time.time()
        res = {"question": question, "answer": FALLBACK_MESSAGE, "sources": [], "retrieved": [], "mode": "refused"}
        if self.store is None:
            res["answer"] = "Please upload and process documents first."
            return res
        if INJECTION.search(question):
            res["mode"] = "blocked-injection"
            res["time"] = round(time.time() - t0, 2)
            return res
        retrieved = self.store.search(question, k=self.top_k, doc_filter=doc_filter)
        res["retrieved"] = retrieved
        good = [c for c in retrieved if c["score"] >= self.threshold()]
        if not good:
            res["mode"] = "refused-low-relevance"
        elif self.api_key:
            try:
                res["answer"] = call_llm(build_messages(question, good), self.api_key, self.model)
                res["mode"] = "llm"
            except Exception as e:
                res["mode"] = "extractive (LLM error)"
                res["error"] = str(e)[:200]
        else:
            res["mode"] = "extractive (no API key)"
        if res["mode"].startswith("extractive"):
            top = good[0]
            res["answer"] = f"Most relevant passage ({top['source']}, page {top['page']}):\n{top['text'][:700]}"
        if FALLBACK_MESSAGE.lower() not in res["answer"].lower():
            seen, srcs = set(), []
            for c in good:
                key = (c["source"], c["page"])
                if key not in seen:
                    seen.add(key)
                    srcs.append({"source": c["source"], "page": c["page"], "score": round(c["score"], 3),
                                 "snippet": c["text"][:220].replace("\n", " ")})
            res["sources"] = srcs
        res["time"] = round(time.time() - t0, 2)
        return res
