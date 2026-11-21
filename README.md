# UOS Library AI — Your Smart Library Assistant

A ChatGPT-style Library Assistant Chatbot built with Python, Streamlit and SQLite.
University student project — demonstration only.

> **Disclaimer:** This is a student project for demonstration purposes. It is not
> officially endorsed by the University of Sargodha and does not access real
> university library records. All book data is sample / demonstration data.

## Features
- ChatGPT-style chat interface, New Chat button, and multiple separate
  conversations in the sidebar (titles from the first question, most
  recently active conversation first, click to reopen and continue).
  Chats are session-only: they are kept while the browser session is
  active and are not saved after the tab is closed.
- Search books by title, author and subject
- Check book availability — **always from SQLite only, never invented by AI**
- Library hours, membership, borrowing, returning and fine information
- English + Roman Urdu understanding; replies try to match the user's language
- Works without an API key (rule-based fallback); Groq free tier is used only
  for general chat when a key is set, never for book availability
- Responsive design for desktop and mobile

## Demo data
80 sample books in SQLite (`library.db`, created by `database.py`):
Computer Science 18, Information Management 12, Library Science 12,
Business 13, Engineering 13, English 12.

## Files
- `app.py` — Streamlit UI + chat logic
- `database.py` — SQLite database + 80 demo books + search functions
- `library.db` — created automatically when the app first runs
- `requirements.txt` — Streamlit + Groq
- `.gitignore` — keeps Python cache, virtual environments and
  `.streamlit/secrets.toml` (API keys) out of GitHub

## Run locally

**Step 1 — Install the required packages (run this only once):**

```bash
pip install -r requirements.txt
```

**Step 2 — Run the app (run this every time you want to start it):**

```bash
streamlit run app.py
```

Then open the local address Streamlit shows in your browser
(usually http://localhost:8501).

## Optional: Groq (free tier)
Set `GROQ_API_KEY` as an environment variable, or in `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your-free-groq-key"
```
Without a key the app still works fully for book search and all library FAQs.

## Deploy (Streamlit Community Cloud, free)
1. Upload these files to the public GitHub repo `uoslibraryai/uos-library-ai`
2. Sign in at share.streamlit.io with GitHub, select that repo, branch `main`, file `app.py`
3. Deploy — you get a public link

## No student login system
By design — no login, no real borrowing transactions, no payments.
