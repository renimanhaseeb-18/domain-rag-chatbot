# Domain-Specific RAG Chatbot for PDF Question Answering

A Retrieval-Augmented Generation (RAG) chatbot built with Streamlit. Upload PDFs (policies, manuals, course notes, legal or training documents), ask questions in natural language, and get answers grounded **only** in the retrieved passages, with the source document and page number shown for every answer.

## Workflow
Upload PDFs -> extract text per page (pypdf) -> split into chunks (LangChain `RecursiveCharacterTextSplitter`, 800 chars, 120 overlap)
-> embed chunks (Sentence Transformers `all-MiniLM-L6-v2`) -> store in FAISS -> user question -> embed question
-> retrieve top-k chunks (cosine similarity) -> send context + question to the LLM (Groq, strict prompt) -> answer + sources.

## Features
- Upload one or more PDFs, file type and size validation (PDF only, max 10 MB, max 5 files), clear documents / clear chat
- Page-level metadata (document name + page number) kept for every chunk
- FAISS vector store with save/load support
- Strict guardrail prompt: answers only from context, fixed fallback message when the answer is missing
- Relevance threshold: refuses without calling the LLM when nothing relevant is found
- Prompt-injection protection: instructions inside documents or questions that try to change the rules are ignored
- Works without an API key (shows the most relevant passage); add a Groq key for generated answers
- Source display below each answer, response time, and a "verify high-stakes information" notice

## Run locally
```
pip install -r requirements.txt
cp .env.example .env        # then put your Groq key in .env (free key: console.groq.com)
streamlit run app.py
```
Click **Use sample PDFs** in the sidebar to try the app with the included `documents/Policy.pdf` and `documents/Handbook.pdf`, or upload your own PDFs and click **Process Documents**.

## Deploy on Streamlit Community Cloud
1. Push this repo to GitHub (never commit `.env`).
2. share.streamlit.io -> New app -> select the repo, main file `app.py`.
3. Advanced settings -> Secrets: `GROQ_API_KEY = "your_key"`.

## Project structure
```
app.py                 Streamlit interface
rag_pipeline.py        Ingest, retrieve, guardrails, answer generation
document_loader.py     PDF reading, validation, chunking
vector_store.py        Embeddings + FAISS (build, search, save, load)
prompt.py              Guardrail prompt and fallback message
create_sample_docs.py  Generates the sample PDFs
documents/             Sample PDFs
tests/test_questions.csv   18-question evaluation set
```

## Testing
`tests/test_questions.csv` has 18 questions: 14 answerable (with expected document and page), 3 not available in the documents, and 1 prompt-injection attempt. The notebook reports retrieval accuracy, answer correctness, refusal quality and response time.

## Responsible AI and security
- API keys are read from environment variables / Streamlit secrets and are never stored in code or GitHub
- Do not upload confidential documents without permission; resumes/documents are processed in memory
- Answers are not guaranteed to be correct: users should verify important information
- Instructions found inside documents are ignored; only PDFs up to 10 MB are accepted

## Limitations
- Scanned (image-only) PDFs are not supported (OCR is a possible extension)
- Chunks are split per page, so an idea that spans two pages can be split
- Answer quality depends on the LLM and on retrieval; a wrong or missing retrieval can lead to a refusal or an incomplete answer
- Free Groq tier has rate limits

## Future work
OCR for scanned PDFs, conversation memory, document filters, FastAPI backend, Docker deployment, feedback buttons.
