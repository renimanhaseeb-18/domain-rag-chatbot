import os
import streamlit as st
from document_loader import validate_pdf, MAX_FILES
from rag_pipeline import RAGPipeline, DEFAULT_MODEL

st.set_page_config(page_title="Domain RAG Chatbot", page_icon="📚", layout="wide")
SAMPLE_FILES = ["documents/Policy.pdf", "documents/Handbook.pdf"]

def get_api_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("📄 Documents")
    uploads = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    st.caption(f"Up to {MAX_FILES} PDFs, max 10 MB each.")
    top_k = st.slider("Chunks to retrieve (top-k)", 3, 5, 4)
    min_score = st.slider("Minimum relevance score", 0.0, 0.6, 0.25, 0.01,
                          help="If the best chunk scores below this, the bot refuses instead of guessing.")
    key_input = st.text_input("Groq API key (optional)", type="password",
                              help="Without a key the bot shows the most relevant passage instead of a generated answer.")
    c1, c2 = st.columns(2)
    process = c1.button("Process Documents", type="primary")
    sample = c2.button("Use sample PDFs")
    if st.button("Clear documents"):
        st.session_state.pipeline, st.session_state.messages = None, []
        st.rerun()

    files = None
    if process:
        if not uploads:
            st.warning("Upload at least one PDF first.")
        elif len(uploads) > MAX_FILES:
            st.error(f"Please upload at most {MAX_FILES} files.")
        else:
            bad = [m for u in uploads for ok, m in [validate_pdf(u.name, u.size)] if not ok]
            if bad:
                st.error("\n".join(bad))
            else:
                files = [(u.name, u.getvalue()) for u in uploads]
    if sample:
        files = [(os.path.basename(p), p) for p in SAMPLE_FILES]

    if files:
        with st.spinner("Reading, chunking and embedding documents..."):
            try:
                pipe = RAGPipeline(top_k=top_k, api_key=key_input or get_api_key())
                stats = pipe.ingest(files)
                st.session_state.pipeline, st.session_state.messages = pipe, []
                st.session_state.stats = stats
            except Exception as e:
                st.error(f"Could not process documents: {e}")

    pipe = st.session_state.pipeline
    if pipe:
        pipe.top_k, pipe.min_score = top_k, min_score
        pipe.api_key = key_input or get_api_key()
        s = st.session_state.stats
        st.success(f"{s['documents']} document(s), {s['pages']} pages, {s['chunks']} chunks")
        for name in pipe.documents:
            st.write("• " + name)
        st.caption(f"Embeddings: {'all-MiniLM-L6-v2' if s['backend'] == 'sbert' else 'TF-IDF backup'} | "
                   f"Mode: {'LLM (' + DEFAULT_MODEL + ')' if pipe.api_key else 'No API key: passage only'}")

# ---------------- Main ----------------
st.title("📚 Domain-Specific RAG Chatbot")
st.caption("Ask questions about your uploaded PDFs. Answers come only from the retrieved passages. "
           "AI answers can be wrong: please verify high-stakes information (legal, medical, financial) in the original document. "
           "Instructions hidden inside documents are ignored.")

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            with st.expander("Sources"):
                for s in m["sources"]:
                    st.markdown(f"**{s['source']}, page {s['page']}** (score {s['score']})  \n_{s['snippet']}..._")
        if m.get("meta"):
            st.caption(m["meta"])

question = st.chat_input("Ask a question about your documents...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        if st.session_state.pipeline is None:
            reply = {"answer": "Please upload PDFs and click **Process Documents** (or **Use sample PDFs**) first.",
                     "sources": [], "mode": "", "time": 0}
        else:
            with st.spinner("Searching documents..."):
                reply = st.session_state.pipeline.ask(question)
        st.markdown(reply["answer"])
        if reply["sources"]:
            with st.expander("Sources", expanded=True):
                for s in reply["sources"]:
                    st.markdown(f"**{s['source']}, page {s['page']}** (score {s['score']})  \n_{s['snippet']}..._")
        meta = f"Mode: {reply['mode']} | {reply.get('time', 0)} s" if reply["mode"] else ""
        if meta:
            st.caption(meta)
    st.session_state.messages.append({"role": "assistant", "content": reply["answer"],
                                      "sources": reply["sources"], "meta": meta})
