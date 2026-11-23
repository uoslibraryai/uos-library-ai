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
| **Official Rules & Regulations FAQs** | 100 FAQs on entry, behaviour, food/bags/phones, book handling, borrowing process, reservations/renewals, lost-book payments, spaces, Digital Commons and penalties. Stored in `library_faq.py`; every answer shows its official source link. | Official Code of Conduct (VC-approved, 04-09-2024), official Book Price Payment form, Information Services page (details below) |

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

## Rules & Regulations FAQs (100)

`library_faq.py` contains exactly 100 question-answer entries about the
library's rules, in 10 categories: entry & ID card (10), behaviour (15),
food / bags / phones / belongings (10), book handling (10), borrowing &
receipts (10), reservations & renewals (10), lost & damaged books and
payments (10), discussion rooms & spaces (10), Digital Commons & IT (10),
and emergency exits, violations & penalties (5). Every FAQ has an English
and a Roman Urdu question and answer, and shows its official source:

- **Wazir Agha Library Code of Conduct** — approved by the Vice Chancellor
  (University of Sargodha Registrar notification dated 04-09-2024):
  https://www.scribd.com/document/767759639/Code-of-Conduct-Wazir-Agha-Library-UOS
- **Official Book Price Payment form** (lost-book price multipliers:
  up to 5 years old 2×, up to 10 years 3×, up to 13 years 4×, 20 years
  and above 5× the printed price — the form does not specify a
  multiplier for 13–20 years, and the chatbot says so):
  https://library.su.edu.pk/files/Books%20Price%20speicemen%20Performa.pdf
- **Information Services page** (portal renewal/reservation, book-search
  assistance, circulation & clearance): https://library.su.edu.pk/information

Matching is deliberately strict — a question must contain a distinctive
phrase from an FAQ, and ties return no match — so unrelated questions
never receive a wrong rules answer. The FAQs never invent unpublished
policy: exact per-violation fine amounts (the Code of Conduct's fine
table could not be read reliably; it states fines up to Rs. 5,000),
borrowing limits, loan periods and membership fees/process are still
answered with "not published" + library contact, exactly as before.
The chatbot itself cannot reserve, renew, borrow or take payments —
the FAQs only explain the library's own process.

## Facilities & Services FAQs (60)

`library_services_faq.py` contains exactly 60 question-answer entries
about the library's facilities and services, in 8 categories: reading
areas & spaces (10), discussion rooms & facilities (8), reference &
information services (8), Research Support Lab (12), Digital Commons &
Wi-Fi (6), printing & multimedia (5), Turnitin & plagiarism services
(5), and document delivery & inter-library loan (6). Every FAQ has an
English and a Roman Urdu question and answer, an official source link,
and a source status (officially verified / general guidance /
not published). Sources:

- **Library Spaces page** (Learning Zone 150 seats, Faculty Lounge 60,
  Research Commons 75, Digital Commons 40, Reference Hall ~100, and
  **8 discussion rooms of 8 users each** — an older About page says 5;
  the FAQs use the current Spaces page figure and explain this):
  https://library.su.edu.pk/libraryspaces
- **Information Services page** (reference desks, orientation &
  information-literacy training, book-searching assistance, SDI,
  Wi-Fi on all floors, Turnitin process, document delivery & ILL):
  https://library.su.edu.pk/information
- **Research Support Lab page** (paid trainings: literature searching,
  EndNote, Mendeley, APA/Harvard referencing, plagiarism avoidance,
  proposal writing, literature review, systematic reviews,
  meta-analysis, scientometrics, research methodology, SPSS,
  SmartPLS, NVivo, MaxQDA, academic & thesis writing — exact fees are
  **not published** and the chatbot says so):
  https://library.su.edu.pk/supportlab

Not published, and never invented: Wi-Fi login credentials/procedure,
photocopy/printing charges, Research Support Lab fees, Turnitin
thresholds/charges/turnaround, and live room availability. The chatbot
cannot itself book rooms, print, issue books, run Turnitin checks or
process inter-library loans — these FAQs only explain the services.

## Academic & Research Assistance FAQs (80)

`library_academic_faq.py` contains exactly 80 question-answer entries
of study and research help, in 8 categories of 10: assignment
assistance, research topic selection, literature review, research
methodology, referencing & citation, research tools & software,
thesis & academic writing, and plagiarism & research ethics. Every
FAQ has an English and a Roman Urdu question and answer, and a
source status that keeps two kinds of content clearly separate:

- **official UOS information** — a service the Wazir Agha Library
  actually offers (for example Research Support Lab trainings in
  literature searching, EndNote/Mendeley, APA/Harvard referencing,
  SPSS/SmartPLS/NVivo/MaxQDA, proposal, academic and thesis writing,
  and plagiarism avoidance; literature-search assistance; HEC
  Digital Library access), taken from the official Information
  Services and Research Support Lab pages.
- **general academic guidance** — ordinary research-methods guidance
  taught everywhere. It is *not* a UOS service, policy or rule, and
  the answers are worded that way.

Accuracy rules: no invented papers, citations, references,
statistics or Turnitin results; referencing formats are shown as
templates with placeholders; no universal numbers are invented —
source counts, sample sizes, thesis length and "acceptable"
similarity percentages depend on the department/supervisor, and the
UOS Turnitin threshold is **not published** in the sources checked.
The library will help students find and use information, but it will
not write their assignments or theses.

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
- 100 Rules & Regulations FAQs from the official Code of Conduct, the
  official Book Price Payment form and the Information Services page —
  in English and Roman Urdu, each with its source link
- 60 Facilities & Services FAQs from the official Library Spaces,
  Information Services and Research Support Lab pages — capacities,
  services and trainings, in English and Roman Urdu, with source links
- 80 Academic & Research Assistance FAQs — assignments, topics,
  literature reviews, methodology, referencing, tools, thesis writing
  and ethics; general guidance clearly separated from official UOS
  services, in English and Roman Urdu
- Honest answers for unpublished policies (fines, limits, membership):
  "not published" + library contact — never invented
- English + Roman Urdu understanding; replies try to match the user's language
- Works without an API key (rule-based fallback); Groq free tier is used only
  for general chat when a key is set, never for book availability
- Responsive design for desktop and mobile

## Interface (redesigned dashboard)
- Dark navy sidebar (#0B2345) with the project branding (book icon —
  no official university seal is reproduced, as no authorized logo
  asset is part of this project), navigation (Home, New Chat, Chat
  History, expandable Library Categories with eight working category
  shortcuts), Quick Access shortcuts, demo catalogue subjects and
  official links.
- Welcome dashboard: banner with the project name and tagline,
  "How can I help you today?", four category cards (Book Search,
  Research Help, Digital Resources, Library Services) that submit
  real questions to the chatbot, and suggested-question chips.
- Top-right About and Help dialogs, and Clear Chat with a
  confirmation that clears only the current conversation.
- English / Roman Urdu interface selector (changes the interface
  text and built-in example prompts; typed questions keep automatic
  language detection) and a Light / Dark theme selector that restyles
  the whole workspace for the session.
- After the first question the dashboard is replaced by the clean
  conversation view; the large rounded chat input stays at the
  bottom. No attachment or microphone controls are shown, because
  the app has no such features.

## Demo data
80 sample books in SQLite (`library.db`, created by `database.py`):
Computer Science 18, Information Management 12, Library Science 12,
Business 13, Engineering 13, English 12.

## Files
- `app.py` — Streamlit UI + chat logic (routing, demo-policy safeguards)
- `library_info.py` — verified official library facts, sources and caveats
- `library_faq.py` — 100 Rules & Regulations FAQs (Code of Conduct, Book
  Price Payment form, Information Services) with strict phrase matching
- `library_services_faq.py` — 60 Facilities & Services FAQs (Library
  Spaces, Information Services, Research Support Lab) with the same
  strict matching; checked after the rules FAQs
- `library_academic_faq.py` — 80 Academic & Research Assistance FAQs
  (assignments, topics, literature review, methodology, referencing,
  tools, thesis writing, ethics) with the same strict matching;
  checked after the services FAQs
- `library_digital_faq.py` — Digital Library & Online Resources FAQs
  (COMPLETE: DL001–DL500, 25 categories × 20 — e-books portal, HEC
  Digital Library, academic databases, Google Scholar, open
  access, paper/PDF finding, academic search engines, e-books &
  e-journals, Zotero, Mendeley & EndNote, AI research assistants,
  advanced searching, keywords & Boolean operators, journal
  quality & indexing, DOI & citation tracking, research data &
  statistics, digital access & troubleshooting, online learning
  platforms, copyright & OA ethics, digital literacy & online
  safety, thesis & dissertation databases, systematic reviews &
  meta-analysis, research collaboration & academic profiles,
  research visualization & data tools, subject-specific digital
  resources) with the same strict matching; checked after the
  academic FAQs

## Digital Library & Online Resources FAQs (COMPLETE: 500 FAQs)

`library_digital_faq.py` was built in 10 approved batches of 50 and
is now **complete: 500 FAQs (25 categories × 20, IDs DL001–DL500)** —
UOS E-books Portal (20), HEC Digital Library (20), Academic
Databases & Journals (20), Google Scholar (20), Free & Open Access
Resources (20), Research Paper & PDF Finding (20), Academic Search
Engines (20), E-books & E-journals (20), Zotero Reference Manager
(20), Mendeley & EndNote (20), AI Research Assistants (20), Advanced
Research Searching (20), Keywords & Boolean Operators (20), Journal
Quality & Indexing (20), DOI & Citation Tracking (20), Research
Data & Statistics Resources (20), Digital Access & Troubleshooting
(20), Online Learning Platforms (20), Copyright & Open Access
Ethics (20), Digital Literacy & Online Safety (20), Thesis &
Dissertation Databases (20), Systematic Reviews & Meta-analysis
(20), Research Collaboration & Academic Profiles (20), Research
Visualization & Data Tools (20), and Subject-Specific Digital
Resources (20). Together with the other FAQ modules the chatbot
answers **740 built-in FAQs**.
Every FAQ has an English and a Roman Urdu question and answer, a
source URL, and a source status (Official UOS information / Official
HEC information / Official external resource documentation / General
academic guidance). External resources are never described as UOS
services; UOS subscriptions are claimed only where an official page
states them (IEEE Xplore and Emerald Insight via the HEC Digital
Library, per the library's Resources page). Unpublished details —
portal collection size, off-campus access, personal logins — are
answered honestly as not published. Pirate sites are never
recommended — one FAQ (DL100) exists specifically to warn against
them. The 500-FAQ digital expansion is complete.

## Book Search & Recommendations

Book search is SQLite-only and works by title, author or subject
(substring, case-insensitive), with dedicated author/title/subject
modes when the wording names a field ("Books by Kotler", a quoted
title, "Show Business books"). Results are ranked — exact title
first, then title, author and subject matches, available books
first — and **all** matches are shown with title, author, subject,
ISBN, publisher, year, shelf and availability. When a specific book
is found, 2–3 related demo books (same author first, then same
subject) are suggested; if the book has 0 available copies, available
alternatives from the same subject are suggested instead. When
nothing is found, the chatbot says so honestly and may add a clearly
labelled "Did you mean?" spelling suggestion or available books from
an identified subject. Asking "List subjects" (or using the sidebar)
shows all six demo subjects with their real book counts, and any
subject can be browsed in full. No book, author, ISBN or availability
value is ever invented — everything comes from the 80 demo records.
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
