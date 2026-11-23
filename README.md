# UOS Library AI — Your Smart Library Assistant

A ChatGPT-style Library Assistant Chatbot built with Python, Streamlit and SQLite.
University student project — demonstration only.

> **Disclaimer:** This is a student project for demonstration purposes. It is not
> officially endorsed by the University of Sargodha and does not access real
> university library records. All book data is sample / demonstration data.

## Three kinds of information — kept strictly separate

| Area | What it is | Source |
| --- | --- | --- |
| **Official UOS Library information** | Verified public facts about Wazir Agha Library: opening hours, contact details, collection figures, facilities, seminar libraries, services, Turnitin process, e-books and HEC Digital Library links. Stored in `library_info.py`; every answer shows its official source link. | Official University of Sargodha / library pages (listed below), checked 21 November 2026 |
| **Demo book catalogue** | 80 sample books in SQLite. Search and availability come from this database only. These are **demonstration data, not verified UOS holdings**. | `database.py` / `library.db` (project sample data) |
| **Demo policies** | Sample membership, borrowing, renewal, return and fine rules invented for this student project. They are **NOT official UOS policies**. They are shown only when a user explicitly asks about the demo project's sample rules, and always begin with a "DEMO ONLY" label. | Project sample data in `app.py` |

**Not published officially:** the library's public pages checked do not publish
borrowing limits, loan periods, fines, fees, or a membership/library-card
process. For those questions the chatbot says so honestly and gives the
library's contact details (library@uos.edu.pk, 048-9230587) instead of
inventing an answer. Break/lunch timings and holiday closures are also not
published; Sunday hours are not listed on the library website.

**Catalogue links:** the real Wazir Agha Library catalogue is linked, not
copied — PakCat (PASTIC): https://pakcat.pastic.gov.pk/library/45/university-of-sargodha
A catalogue record does not confirm that a copy is available for borrowing.
The library website's own Koha catalogue was unreachable when checked on
21 November 2026. No catalogue records were scraped or imported.

## Official sources used
- Wazir Agha Library website: https://library.su.edu.pk/ (hours, contact, services, Turnitin, facilities)
- Library on the main UOS site: https://www.su.edu.pk/wazir_agha_library (collection figures, photocopying)
- About / spaces pages: https://library.su.edu.pk/about and https://library.su.edu.pk/libraryspaces (history, seminar libraries, facilities, seating capacity)
- UOS E-Books portal: https://ebooks.su.edu.pk/
- HEC Digital Library (UOS page): https://www.digitallibrary.edu.pk/sargodhauni.html
- PakCat union catalogue (link only): https://pakcat.pastic.gov.pk/library/45/university-of-sargodha

## Features
- ChatGPT-style chat interface, New Chat button, and multiple separate
  conversations in the sidebar (titles from the first question, most
  recently active conversation first, click to reopen and continue).
  Chats are session-only: they are kept while the browser session is
  active and are not saved after the tab is closed.
- Search books by title, author and subject
- Check book availability — **always from SQLite only, never invented by AI**
- Official Wazir Agha Library information with source links: hours, contact,
  collection, facilities, services, Turnitin, e-books, HEC Digital Library,
  and a link to the real PakCat catalogue
- Honest answers for unpublished policies (fines, limits, membership):
  "not published" + library contact — never invented
- English + Roman Urdu understanding; replies try to match the user's language
- Works without an API key (rule-based fallback); Groq free tier is used only
  for general chat when a key is set, never for book availability
- Responsive design for desktop and mobile

## Demo data
80 sample books in SQLite (`library.db`, created by `database.py`):
Computer Science 18, Information Management 12, Library Science 12,
Business 13, Engineering 13, English 12.

## Files
- `app.py` — Streamlit UI + chat logic (routing, demo-policy safeguards)
- `library_info.py` — verified official library facts, sources and caveats
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
Without a key the app still works fully for book search and all library information.

## Deploy (Streamlit Community Cloud, free)
1. Upload these files to the public GitHub repo `uoslibraryai/uos-library-ai`
2. Sign in at share.streamlit.io with GitHub, select that repo, branch `main`, file `app.py`
3. Deploy — you get a public link

## No student login system
By design — no login, no real borrowing transactions, no payments.
