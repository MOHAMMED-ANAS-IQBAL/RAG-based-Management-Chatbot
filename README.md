# 📊 RAG-based Management Chatbot

An interactive **Management Advisor** built with **Streamlit** that uses **Retrieval-Augmented Generation (RAG)** to answer management questions (leadership, strategy, operations, org dev, etc.).  
Users upload their own management PDF files to create a custom knowledge base, and must enter their own OpenRouter / OpenAI-compatible API key in the app UI — there is **no `.env`** required or stored by default.

---

## 🔎 Key ideas (short)
- **RAG only works when users upload documents.** Uploaded PDFs are extracted, split into chunks, and used to ground answers.
- **API key is entered in the UI.** The app connects to OpenRouter / OpenAI-compatible endpoint (project uses `deepseek/deepseek-chat-v3-0324:free` in code).
- **No central key storage** — keys live in session state only; users must supply their own keys each session.

---

## Features
- Upload PDFs (management books, reports, policies, case studies) to enable RAG mode.
- If no files are uploaded, the app runs in **Standard Mode** using LLM-only responses.
- Simple keyword-based retrieval is used as the RAG retrieval mechanism in the current version (chunks chosen via keyword overlap).
- Streamlit chat UI with session chat history, API key connect/disconnect, and upload status messages.
- Lightweight — easy to run locally or deploy.

---

## Project structure

project/

├─ chat.py                         # Main Streamlit app (provided)

├─ requirements.txt                # (optional)

└─ README.md

---

## 🛠 Prerequisites
- Python 3.8+
- Basic familiarity with running Streamlit apps
- An OpenRouter / OpenAI-compatible API key (users must provide their key in the UI)

---

## ⚙️ Installation
### 1. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
### 2. Install dependencies (example)
pip install -r requirements.txt

---

## ▶️ Run the app
### From the project folder:
streamlit run chat.py

---

## 🧭 How to use (UI steps)
1. Open the app in the browser (Streamlit will open it).
2. Enter your OpenRouter / OpenAI-compatible API key in the top field and click Connect.
3. (Optional but required for RAG) Upload one or more PDF documents in the Document Upload area.
4. Type your management question into the chat input and press Enter.
5. If documents are uploaded, the app will retrieve relevant text chunks and include them as context in the prompt to the LLM — giving RAG-enhanced answers.

---

## 🔍 How RAG works in this app (plain English)
1. The app extracts text from uploaded PDFs using PyPDF2.
2. Text is split into chunks with RecursiveCharacterTextSplitter.
3. A simple keyword-overlap search selects the top relevant chunks for a question.
4. Those chunks are included as context and sent with the user question to the LLM (via the user’s API key).
5. The LLM returns an answer that is (ideally) grounded in the uploaded documents.

---

## ⚠️ Important notes & best practices
1. You must upload your PDFs for the chatbot to produce document-grounded answers. Without uploads, the chatbot answers from the model alone.
2. Do not upload sensitive/confidential files unless you trust the deployment environment. For shared or public deployments, add auth and encryption.
3. Scanned PDFs may not extract text — use OCR (Tesseract or similar) before uploading.
4. Large documents may cause token-limit issues — chunking helps, but consider semantic retrieval (embeddings + vector DB) for better scale.
5. LLM hallucinations are still possible. Consider showing retrieved snippets or filenames with the answer to improve trust.

---

## ✅ Suggested next steps / improvements
1. Replace the keyword retrieval with semantic embeddings + Chroma/FAISS for better matches.
2. Persist a vector store to disk for faster repeated queries.
3. Add source citations: show which PDF/chunk the answer used.
4. Integrate OCR for scanned PDFs.
5. Add authentication and HTTPS for secure multi-user use.
6. Add document management (delete/update) and basic analytics (common queries).

---

## 🐞 Troubleshooting
- "API Key Missing" / connection errors: Make sure the key is valid and you’ve clicked Connect. If rate-limited, check provider dashboard.
- "No text extracted": PDF may be scanned images — run OCR first.
- Slow responses: API latency or large prompt context. Reduce k (number of chunks retrieved) or chunk size.
- Chat empty / no replies: Ensure the API key is connected and not expired.

---

✉️ Contact[
https://www.linkedin.com/in/mohammedanasiqbal/](https://www.linkedin.com/in/mohammedanasiqbal/)
