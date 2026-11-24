"""UOS Library AI - app.py
ChatGPT-style Library Assistant Chatbot (student demo project).

How it answers - in this order, always:
  1. Book search / availability  -> SQLite ONLY (database.py). Never invent.
     The 80 books are demonstration data, not verified UOS holdings.
  2. Rules & Regulations FAQs -> library_faq.py: 100 FAQs taken from the
     official Wazir Agha Library Code of Conduct (approved by the Vice
     Chancellor, Registrar notification dated 04-09-2024), the official
     Book Price Payment form, and the library's Information Services
     page. Matching is strict (distinctive phrases only), so unrelated
     questions never receive a wrong rules answer.
  2b. Facilities & Services FAQs -> library_services_faq.py: 60 FAQs
     from the official Library Spaces, Information Services and
     Research Support Lab pages (capacities, services, trainings).
     Checked after the rules FAQs; same strict matching.
  2c. Academic & Research Assistance FAQs ->
     library_academic_faq.py: 80 FAQs of general academic guidance
     (plus the few library services officially published). Checked
     after the services FAQs; same strict matching.
  3. Official library questions -> verified facts in library_info.py only,
     each with its official source link.
  4. Real policy questions whose answers are NOT published (borrowing
     limits, loan periods, membership process, exact fine amounts)
     -> honest "not published in the sources checked" + library contact.
     Demo sample rules are shown ONLY when the user explicitly asks about
     the demo project's sample rules, and always start with the DEMO ONLY
     label (decision D1).
  5. General chat -> Groq (free tier) IF a key is set, else rule-based fallback.
     Groq is never asked about book titles or availability.

Language: English + Roman Urdu. The reply tries to match the user's language.
Chat history: multiple separate chats in the sidebar. Guests are
session-only (nothing is saved). Students who register/sign in
(Stage 4, Supabase, see supabase_store.py + supabase_schema.sql)
get their chats saved permanently and privately under Row Level
Security; guest mode works with no configuration at all.
All book data is demonstration data.
"""

import difflib
import os
import re
import uuid

import streamlit as st

from database import count_by_subject, init_db, search_books
from library_faq import FAQS as RULES_FAQS, _content_words, faq_answer
from library_info import DEMO_LABEL, FACTS, get_fact, policy_not_published

try:
    import supabase_store as store
except Exception:  # accounts are optional - guest mode must never break
    store = None
from library_academic_faq import FAQS as ACADEMIC_FAQS, academic_faq_answer
from library_digital_faq import FAQS as DIGITAL_FAQS, digital_faq_answer
from library_services_faq import FAQS as SERVICES_FAQS, service_faq_answer
from library_guides_faq import FAQS as GUIDES_FAQS, guide_faq_answer

# ---------- DEMO sample policies (student project ONLY - NOT UOS policy) ----------
# These sample rules exist only so the demo can show how a policy answer
# looks. They are NEVER shown automatically (decision D1): get_reply()
# returns them only for an explicit demo-policy question, and every such
# answer begins with DEMO_LABEL from library_info.py.
DEMO_MEMBERSHIP_INFO = (
    "Sample rule: students can get free library membership with a valid "
    "university student card, registered at the circulation desk."
)
DEMO_BORROW_INFO = (
    "Sample rule: students can borrow up to 3 books for 14 days, issued at "
    "the circulation desk with a student card."
)
DEMO_RETURN_INFO = (
    "Sample rule: return books at the circulation desk before the due "
    "date; a book can be renewed once for 7 more days if no one else has "
    "reserved it."
)
DEMO_FINE_INFO = "Sample rule: late return fine of Rs. 10 per day, per book."

DEMO_POLICY_ANSWERS = {
    "membership": DEMO_MEMBERSHIP_INFO,
    "borrow": DEMO_BORROW_INFO,
    "return": DEMO_RETURN_INFO,
    "renew": DEMO_RETURN_INFO,
    "fine": DEMO_FINE_INFO,
}

# Only genuine Roman Urdu words - English words like "time"/"fine"/"member"
# must NOT trigger Urdu detection, or English questions get Urdu replies.
ROMAN_URDU_WORDS = [
    "kis", "kya", "kab", "kahan", "kaise", "mujhe", "chahiye", "kitab",
    "khulti", "band", "baje", "hai", "hain", "karo", "batao",
    "wapas", "lena", "dena", "kitaab",
]

# ---------- Official-info routing (library_info.py facts) ----------
# Order matters: specific topics before generic ones, and all of these
# before the book search, so e.g. "How many books are in the library?"
# reaches the official collections fact instead of the SQLite search.
OFFICIAL_ROUTES = [
    (["sunday", "itwaar"], "sunday"),
    (["break", "lunch", "waqfa"], "break"),
    (["turnitin", "similarity", "plagiarism"], "turnitin"),
    (["pakcat", "opac", "catalogue", "catalog"], "catalogue"),
    (["e-book", "ebook", "ebooks", "portal"], "ebooks"),
    (["hec", "digital library", "online journal"], "hec"),
    (["how many books", "collection", "total books", "printed books",
      "books are in the library", "library collection"], "collections"),
    (["contact", "phone", "email", "address", "helpline", "rabta", "number"], "contact"),
    (["seminar librar"], "seminar_libraries"),
    (["history", "archive", "government college", "purani",
      "old book", "rare book"], "history"),
    (["photocopy", "printing"], "photocopy"),
    (["facilit", "learning zone", "faculty lounge", "research commons",
      "digital commons", "reference hall", "discussion room", "seating",
      "study space"], "facilities"),
    (["wifi", "wi-fi", "internet"], "wifi"),
    (["renew", "reserve", "reservation"], "renewal"),
    (["service", "reference", "orientation", "information literacy",
      "endnote", "mendeley", "spss", "literature search", "research support",
      "research help", "document delivery", "inter-library", "inter library",
      "book searching"], "services"),
    (["open", "khulti", "khuli", "khula", "timing", "hours", "schedule",
      "kis time", "band", "close", "closing"], "hours"),
]

# Real policy questions whose official answers are NOT published (D1).
POLICY_ROUTES = [
    (["fine", "jurmana", "late fee", "penalty", "late return",
      "overdue book", "overdue books"], "fine",
     "borrowing fines and late-return charges", "fine aur late-return charges ki policy"),
    (["member", "library card"], "membership",
     "membership and library-card policy", "membership aur library-card ki policy"),
    (["how many books can", "borrow limit", "borrowing limit", "loan period",
      "how long can i keep", "kitni kitabein le", "kitni books issue",
      "kitni kitabein issue", "kitni books le", "books issue ho sakt",
      "kitabein issue ho sakt", "issue ho sakt", "kitni books borrow",
      "how many books can i borrow", "how many books can i issue",
      "kitne din ke liye", "book mil sakt", "book rakh sakt"], "borrow",
     "borrowing limits and loan periods", "borrowing limits aur loan period ki policy"),
]


def is_roman_urdu(text):
    text = text.lower()
    return any(w in text.split() for w in ROMAN_URDU_WORDS)


def _book_block(b):
    """One book's full details. Every value comes from SQLite; a field
    is omitted only when it is genuinely empty in the record."""
    if b["available_copies"] > 0:
        status = f"✅ Available: {b['available_copies']} of {b['total_copies']} copies"
    else:
        status = "❌ Not available right now (0 copies available)"
    parts = [f"Subject: {b['subject']}"]
    if b.get("shelf_location"):
        parts.append(f"Shelf: {b['shelf_location']}")
    if b.get("year"):
        parts.append(f"Year: {b['year']}")
    lines = [f"**{b['title']}** by {b['author']}", " | ".join(parts)]
    extra = []
    if b.get("publisher"):
        extra.append(f"Publisher: {b['publisher']}")
    if b.get("isbn"):
        extra.append(f"ISBN: {b['isbn']}")
    if extra:
        lines.append(" | ".join(extra))
    lines.append(status)
    return "\n".join(lines)


def format_books(books, roman_urdu=False, intro=None):
    """Show ALL matching books (no silent hiding), in the order given."""
    if intro is None:
        intro = (
            "📚 Ye kitabein demo catalogue (80 sample books — demonstration data, asal UOS holdings nahi) mein mili hain:"
            if roman_urdu
            else "📚 I found these books in the demo catalogue (80 sample books — demonstration data, not verified UOS holdings):"
        )
    return intro + "\n\n" + "\n\n".join(_book_block(b) for b in books)


# ---------- Book search & recommendations (SQLite ONLY) ----------------
# Every book, author, ISBN, publisher, shelf and availability value in
# this section comes from the 80 demo records in library.db through
# database.search_books(). Nothing is invented: recommendations are
# other real rows from the same table (same author / same subject).

# Everyday topic words -> the demo subject they belong to. Used ONLY to
# suggest real demo books when a search finds nothing.
TOPIC_TO_SUBJECT = {
    "programming": "Computer Science", "coding": "Computer Science",
    "software": "Computer Science", "algorithms": "Computer Science",
    "marketing": "Business", "management": "Business",
    "accounting": "Business", "economics": "Business",
    "entrepreneurship": "Business",
    "circuits": "Engineering", "mechanics": "Engineering",
    "thermodynamics": "Engineering", "electronics": "Engineering",
    "grammar": "English", "literature": "English", "novel": "English",
    "novels": "English", "poetry": "English", "linguistics": "English",
    "cataloging": "Library Science", "cataloguing": "Library Science",
    "librarianship": "Library Science",
    "databases": "Information Management",
    "information systems": "Information Management",
}


def _rank_books(books, query):
    """Order results: exact title > title match > author match >
    subject match; within a tier, available books first, then A-Z."""
    q = query.strip().lower()

    def score(b):
        title, author, subject = (
            b["title"].lower(), b["author"].lower(), b["subject"].lower())
        if title == q:
            s = 100
        elif q in title:
            s = 70
        elif q in author:
            s = 50
        elif q in subject:
            s = 30
        else:  # word-overlap fallback (partial multi-word queries)
            words = set(q.split())
            s = 10 + len(words & set(title.split())) * 2
        return (-s, 0 if b["available_copies"] > 0 else 1, title)

    return sorted(books, key=score)


def _related_books(top_book, exclude_ids, limit=3):
    """Up to `limit` related demo books for `top_book`: same author
    first, then same subject (available first). Never includes a book
    already shown."""
    related, seen = [], set(exclude_ids)
    same_author = search_books(top_book["author"], search_by="author")
    same_subject = search_books(top_book["subject"], search_by="subject")
    for pool, tag in ((same_author, "same author"), (same_subject, "same subject")):
        pool = [b for b in pool if b["id"] not in seen]
        pool.sort(key=lambda b: (0 if b["available_copies"] > 0 else 1, b["title"]))
        for b in pool:
            if b["id"] in seen:
                continue
            seen.add(b["id"])
            related.append((b, tag))
            if len(related) >= limit:
                return related
    return related


def _recommendation_block(top_book, shown_books, roman_urdu):
    """Related/alternative suggestions for a specific found book.
    If the book is unavailable, only AVAILABLE alternatives are
    suggested, and they are labelled as alternatives."""
    shown_ids = {b["id"] for b in shown_books}
    if top_book["available_copies"] <= 0:
        alts = [(b, t) for b, t in _related_books(top_book, shown_ids)
                if b["available_copies"] > 0]
        if not alts:
            return ""
        head = (
            f"\n\nYe kitab filhal available nahi hai — demo catalogue mein is subject ki ye available kitabein hain:"
            if roman_urdu else
            f"\n\nThis book is not available right now — here are available alternatives in the same subject from the demo catalogue:"
        )
        return head + "\n\n" + "\n\n".join(_book_block(b) for b, _t in alts)
    rel = _related_books(top_book, shown_ids)
    if not rel:
        return ""
    head = (
        "\n\nDemo catalogue mein in se related kitabein:"
        if roman_urdu else
        "\n\nRelated books in the demo catalogue:"
    )
    return head + "\n\n" + "\n\n".join(
        _book_block(b) + f"\n(Related: {tag})" for b, tag in rel)


def _subject_browse_reply(roman_urdu):
    counts = count_by_subject()
    lines = [
        f"- **{subject}** — {n} demo books" for subject, n in counts.items()
    ]
    if roman_urdu:
        return (
            "Demo catalogue (80 sample books — demonstration data) mein ye subjects hain:\n\n"
            + "\n".join(lines)
            + "\n\nKisi subject ki kitabein dekhne ke liye likhein, masalan: *Show Computer Science books*"
        )
    return (
        "The demo catalogue (80 sample books — demonstration data) has these subjects:\n\n"
        + "\n".join(lines)
        + "\n\nTo browse one, just ask, e.g. *Show Computer Science books*"
    )


def _did_you_mean(text):
    """Spelling-tolerant suggestion: the closest real demo title/author
    to what the user typed, or None. Always presented as a question,
    never as an exact result."""
    books = search_books("")
    candidates = {}
    for b in books:
        candidates[b["title"].lower()] = b
        candidates[b["author"].lower()] = b
        # Individual title/author words too, so a one-word misspelling
        # ("Algoritms") can be matched against the word "Algorithms"
        # inside a long title.
        for w in (b["title"] + " " + b["author"]).lower().split():
            w = w.strip("?.!,:")
            if len(w) >= 4:
                candidates.setdefault(w, b)
    probes = [text.lower()]
    probes += [w.strip("?.!,").lower() for w in text.split()
               if len(w) >= 4 and w.lower() not in SEARCH_STOPWORDS]
    for probe in probes:
        close = difflib.get_close_matches(probe, list(candidates), n=1, cutoff=0.72)
        if close:
            return candidates[close[0]]
    return None


def _not_found_reply(text, low, roman_urdu):
    """Honest not-found, plus (a) a 'Did you mean?' suggestion when a
    real demo book is a close spelling match, and (b) available books
    from an identified subject. Uncertain matches are always labelled
    as suggestions, never as results."""
    base = (
        "Maaf kijiye, ye kitab demo data mein nahi mili."
        if roman_urdu else
        "Sorry, I could not find that book in the demo data."
    )
    suggestion = _did_you_mean(text)
    if suggestion is not None:
        q = (
            f"Kya aap ka matlab ye tha? (ye sirf aik tajweez hai — exact match nahi mila)"
            if roman_urdu else
            f"Did you mean this book? (this is only a suggestion — no exact match was found)"
        )
        return f"{base}\n\n{q}\n\n" + _book_block(suggestion)
    subject = None
    for topic, subj in TOPIC_TO_SUBJECT.items():
        if topic in low:
            subject = subj
            break
    if subject:
        pool = [b for b in search_books(subject, search_by="subject")
                if b["available_copies"] > 0][:3]
        if pool:
            head = (
                f"Albatta demo catalogue mein **{subject}** ki ye available kitabein hain:"
                if roman_urdu else
                f"However, these available books in **{subject}** are in the demo catalogue:"
            )
            return base + "\n\n" + head + "\n\n" + "\n\n".join(
                _book_block(b) for b in pool)
    tail = (
        "Koi aur title, author ya subject try karein."
        if roman_urdu else
        "Please try another title, author or subject."
    )
    return f"{base} {tail}"


# ---------- Stage 2: Groq AI brain (grounded, fallback-safe) ----------
# The deterministic layers (FAQs, official facts, policy honesty,
# SQLite book search) answer FIRST and never call the API. Groq is
# used only for what they cannot answer: natural conversation,
# follow-ups, explanations and open questions. It receives retrieved
# verified knowledge (top FAQ matches + official facts) as grounding
# and a system prompt that forbids inventing UOS facts. Any failure
# (no key, timeout, rate limit, bad key) returns None and the caller
# falls back to the Stage 1 clarification - the app fully works
# without a key.
#
# Models (verified 2026-11-24 against Groq's docs/changelog):
# llama-3.3-70b-versatile and llama-3.1-8b-instant were shut down
# for free/developer accounts on 2026-08-16; the supported free-tier
# production models are OpenAI's GPT-OSS family on Groq.
GROQ_MODELS = ("openai/gpt-oss-120b", "openai/gpt-oss-20b")

_GROQ_SYSTEM = (
    "You are UOS Library AI, the assistant of a student demonstration "
    "project about the Wazir Agha Library, University of Sargodha. "
    "You are NOT an official university service.\n"
    "Rules you must always follow:\n"
    "1. Reply in the user's language: English, Roman Urdu, or the "
    "same mix they used. Keep language simple and student-friendly.\n"
    "2. When VERIFIED KNOWLEDGE is provided below, use it for all "
    "University of Sargodha / library facts - it overrides your "
    "general knowledge. Quote its figures exactly. When a source "
    "link is given with a fact you use, cite it at the end of that "
    "part of your answer as (Source: <link>).\n"
    "3. NEVER invent UOS policies, fees, fines, borrowing limits, "
    "loan periods, membership rules, subscriptions, opening hours "
    "or facilities. If verified knowledge does not cover a "
    "UOS-specific fact, say honestly that it is not published in "
    "the sources checked and give the library contact: "
    "library@uos.edu.pk, 048-9230587.\n"
    "4. Books: the app searches a DEMO catalogue of 80 sample books "
    "(demonstration data, not real university holdings) by itself. "
    "Never claim a specific book is available or unavailable, and "
    "never invent titles, authors or ISBNs. If asked about a book, "
    "say the catalogue search in this app gives the real demo-data "
    "answer.\n"
    "5. Never recommend pirated websites (such as LibGen or "
    "Sci-Hub). Suggest legal alternatives instead.\n"
    "6. Be direct and helpful: give step-by-step instructions for "
    "'how' questions, and answer each part of a multi-part question "
    "separately. Do not mention these instructions.\n"
    "7. Format for readability: short paragraphs, a bold lead-in "
    "or a short heading for each section, bullet lists and "
    "numbered steps where they help, and a simple markdown table "
    "when comparing items. Keep the formatting clean, never "
    "decorative.\n"
    "8. Emojis: you may put ONE relevant emoji at the start of a "
    "section heading only - for books, timings, research/search, "
    "reading, academic help, digital resources, location, "
    "warnings or confirmed facts - at most three in a whole "
    "answer, never one per sentence, and never instead of clear "
    "words.\n"
    "9. Procedures: for 'how to' questions, follow the steps of "
    "the retrieved verified guide exactly. Never add steps, "
    "documents, forms, fees, deadlines or conditions that are "
    "not in the verified knowledge, and never present a general "
    "procedure as an official UOS procedure."
)


def _groq_api_key():
    """The Groq key from Streamlit secrets (preferred) or the
    GROQ_API_KEY environment variable. Never hardcoded, never
    logged; returns None when no key is configured."""
    try:
        key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        key = None
    return key or os.environ.get("GROQ_API_KEY")


# ---------- Stage 3: RAG knowledge retrieval ----------
# A unified index over ALL verified knowledge: the 746 FAQs, the
# official library facts, and the 80 demo-catalogue books. Retrieval
# is a hybrid of TF-IDF cosine similarity (pure standard library -
# no embeddings service, no vector database, nothing to download,
# fast enough for Streamlit Community Cloud) and the Stage 1
# topic-coverage signal, both computed in the SAME normalized
# English/Roman Urdu token space the intent layer uses, so typos,
# concept words (kitab -> book) and mixed language all retrieve
# correctly. Local embedding models (e.g. sentence-transformers)
# were evaluated and rejected for this deployment: they need a
# ~100 MB model download plus the torch runtime (hundreds of MB),
# which is unreliable within Community Cloud's free limits, while
# this corpus is small, curated and bilingual in a way generic
# embeddings do not handle better than the normalized hybrid.
# Retrieval feeds ONLY the Groq grounding (Stage 2 position): the
# deterministic layers still answer first, and with no Groq key the
# app's behaviour is exactly as before.
_KB = None  # (docs, idf) built lazily once
RETRIEVAL_MIN_SCORE = 0.20


def _kb_index():
    """Build the knowledge-base index once: documents with their
    weighted TF-IDF vectors. Question text weighs most, answers
    less; fact documents also carry their Stage 1 signal words as
    alias tokens ('timing' finds the hours fact)."""
    global _KB
    if _KB is not None:
        return _KB
    import math
    from collections import Counter

    docs = []

    def add(doc, weighted_tokens, match_words):
        vec = Counter()
        for tok, w in weighted_tokens:
            vec[tok] += w
        docs.append({**doc, "_vec": vec, "_match": set(match_words)})

    for faqs, label in ((RULES_FAQS, "Library Rules"),
                        (SERVICES_FAQS, "Library Services"),
                        (ACADEMIC_FAQS, "Academic & Research"),
                        (DIGITAL_FAQS, "Digital Library"),
                        (GUIDES_FAQS, "Student Guides")):
        for f in faqs:
            q_words = (_topic_word_list(f["q_en"])
                       + _topic_word_list(f["q_ru"]))
            a_words = (_topic_word_list(f["a_en"])
                       + _topic_word_list(f["a_ru"]))
            weighted = ([(t, 3.0) for t in q_words]
                        + [(t, 1.0) for t in
                           _topic_word_list(f["category"])]
                        + [(t, 0.5) for t in a_words])
            add({"id": f["id"], "kind": "faq", "module": label,
                 "q_en": f["q_en"], "q_ru": f["q_ru"],
                 "a_en": f["a_en"], "a_ru": f["a_ru"],
                 "source": f.get("source", ""),
                 "status": f.get("status", "")},
                weighted, q_words)
    for key, fact in FACTS.items():
        words = (_topic_word_list(fact["en"])
                 + _topic_word_list(fact["ur"]))
        aliases = list(_FACT_SIGNALS.get(key, ()))
        add({"id": f"FACT-{key}", "kind": "fact",
             "module": "Official Library Information", "key": key,
             "source": fact.get("source", "")},
            [(t, 1.0) for t in words] + [(t, 2.0) for t in aliases],
            words + aliases)
    for subject in count_by_subject():
        for b in search_books(subject, search_by="subject"):
            words = (_topic_word_list(b["title"])
                     + _topic_word_list(b["author"])
                     + _topic_word_list(b["subject"]))
            weighted = ([(t, 2.0) for t in _topic_word_list(b["title"])]
                        + [(t, 1.5) for t in _topic_word_list(b["author"])]
                        + [(t, 1.5) for t in _topic_word_list(b["subject"])])
            add({"id": f"BOOK-{b['isbn']}", "kind": "book",
                 "module": "Demo Catalogue (demonstration data)",
                 "title": b["title"], "author": b["author"],
                 "subject": b["subject"], "publisher": b["publisher"],
                 "year": b["year"]},
                weighted, words)
    df = Counter()
    for d in docs:
        for tok in d["_vec"]:
            df[tok] += 1
    n = len(docs)
    idf = {t: math.log((1 + n) / (1 + c)) + 1.0 for t, c in df.items()}
    for d in docs:
        vec = {t: w * idf[t] for t, w in d["_vec"].items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        d["_vec"] = {t: v / norm for t, v in vec.items()}
    _KB = (docs, idf)
    return _KB


def _retrieve_knowledge(user_text, limit=5):
    """Hybrid retrieval over the knowledge base. Score = TF-IDF
    cosine (semantic-ish similarity in normalized token space)
    combined with Stage 1 topic coverage, plus a bonus when a
    specific named entity (Zotero, Coursera, Turnitin...) matches.
    Returns [(score, doc)] above the confidence threshold, best
    first, at most 3 documents per module so multi-part questions
    can draw on several sources. Empty list when the evidence is
    too weak - the caller then asks for clarification instead of
    grounding an answer on irrelevant material."""
    import math
    from collections import Counter

    user_words = _topic_words(user_text)
    # 'library' names the whole domain, not a topic: on its own it
    # matches hundreds of documents and grounds nothing. Drop it
    # when real topic words remain (the Stage 1 gate does the same).
    if len(user_words) > 1:
        user_words.discard("library")
        user_words.discard("librarie")  # stemmed form of 'libraries'
    if not user_words or user_words <= {"library", "librarie"}:
        return []
    docs, idf = _kb_index()
    qcount = Counter(_topic_word_list(user_text))
    if len(_topic_words(user_text)) > 1:
        qcount.pop("library", None)
        qcount.pop("librarie", None)
    if "thesis" in user_words:
        # Same expansion as the Stage 1 assisted matcher: theses
        # live under 'thesis and dissertation' documents.
        qcount["dissertation"] += 1
    qvec = {t: c * idf.get(t, 1.0) for t, c in qcount.items()}
    qnorm = math.sqrt(sum(v * v for v in qvec.values())) or 1.0
    qvec = {t: v / qnorm for t, v in qvec.items()}
    entities = user_words & _SPECIFIC_ENTITIES
    match_words = set(user_words)
    if "thesis" in match_words:
        match_words.add("dissertation")
    scored = []
    for d in docs:
        cos = sum(w * d["_vec"].get(t, 0.0) for t, w in qvec.items())
        if cos <= 0:
            continue
        coverage = min(1.0, len(match_words & d["_match"])
                       / len(user_words))
        score = 0.6 * cos + 0.4 * coverage
        if entities and entities & d["_match"]:
            score += 0.08
        if score >= RETRIEVAL_MIN_SCORE:
            scored.append((score, d))
    scored.sort(key=lambda s: -s[0])
    picked, per_module = [], Counter()
    for score, d in scored:
        if per_module[d["module"]] >= 3:
            continue
        per_module[d["module"]] += 1
        picked.append((score, d))
        if len(picked) == limit:
            break
    return picked


def _grounding_context(user_text, roman_urdu):
    """Stage 3 grounding for the Groq prompt: the top retrieved
    verified sources (FAQs, official facts, demo books) with their
    source links, plus the demo-catalogue summary. Retrieved text
    is labelled by module and status so the model - and the
    student reading a citation - can tell verified UOS information
    from general guidance and demo data."""
    blocks = []
    try:
        hits = _retrieve_knowledge(user_text)
        lines = []
        for _score, d in hits:
            if d["kind"] == "faq":
                q = d["q_ru"] if roman_urdu else d["q_en"]
                a = d["a_ru"] if roman_urdu else d["a_en"]
                lines.append(
                    f"[{d['id']} · {d['module']} · {d['status']}]\n"
                    f"Q: {q}\nA: {a[:700]}\nSource: {d['source']}")
            elif d["kind"] == "fact":
                lines.append(
                    f"[{d['id']} · Official Library Information]\n"
                    + get_fact(d["key"], roman_urdu)[:700])
            else:  # demo book - never state availability here
                lines.append(
                    f"[{d['id']} · Demo Catalogue - DEMONSTRATION "
                    f"DATA, not real university holdings]\n"
                    f"\"{d['title']}\" by {d['author']} - "
                    f"{d['subject']}, {d['publisher']} ({d['year']}). "
                    f"Availability is checked only by the app's own "
                    f"catalogue search.")
        if lines:
            blocks.append("Retrieved verified sources:\n"
                          + "\n\n".join(lines))
    except Exception:
        pass
    # Official facts the question touches directly (Stage 2 path,
    # kept as a booster alongside retrieval).
    try:
        tokens = set(_normalize_query(user_text).split())
        facts = [get_fact(k, roman_urdu)
                 for k, sig in _FACT_SIGNALS.items() if sig & tokens]
        if facts:
            blocks.append("Official library facts:\n"
                          + "\n\n".join(f[:500] for f in facts[:2]))
    except Exception:
        pass
    # Demo catalogue summary (real counts from SQLite).
    try:
        counts = count_by_subject()
        summary = ", ".join(f"{s}: {n}" for s, n in counts.items())
        blocks.append(
            f"Demo catalogue: 80 sample books (demonstration data) "
            f"in these subjects - {summary}. Availability is checked "
            f"only by the app's own catalogue search.")
    except Exception:
        pass
    return "\n\n".join(blocks)


def ask_groq_or_fallback(user_text, roman_urdu, history=None):
    """Grounded Groq conversation for questions the deterministic
    layers could not answer. Returns None on ANY problem (no key,
    SDK missing, timeout, rate limit, invalid key, empty reply) -
    the caller then uses the Stage 1 clarification fallback."""
    api_key = _groq_api_key()
    if not api_key:
        return None
    try:
        from groq import Groq
    except Exception:
        return None
    messages = [{"role": "system", "content": _GROQ_SYSTEM}]
    grounding = _grounding_context(user_text, roman_urdu)
    if grounding:
        messages.append({
            "role": "system",
            "content": "VERIFIED KNOWLEDGE (use this for library "
                       "facts):\n" + grounding,
        })
    # Conversation context for follow-ups: the last few turns of
    # THIS chat only, oldest first, current question excluded (it
    # is appended separately below).
    if history:
        turns = []
        for msg in history:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role")
            content = str(msg.get("content", "")).strip()
            if role in ("user", "assistant") and content:
                turns.append({"role": role,
                              "content": content[:1200]})
        messages.extend(turns[-8:])
    messages.append({"role": "user", "content": user_text})
    try:
        client = Groq(api_key=api_key, timeout=30.0, max_retries=1)
    except Exception:
        return None
    for model in GROQ_MODELS:
        try:
            reply = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_completion_tokens=900,
                reasoning_effort="low",
            )
            content = reply.choices[0].message.content
            if content and content.strip():
                return content.strip()
        except Exception:
            continue  # rate limit / error on this model -> try next
    return None


# Generic words that must NOT be used as a book search term on their own.
# Without this, "Find a book that does not exist" matched "book" inside
# "Workbook" ("Creative Writing: A Workbook...") and returned a wrong book
# instead of "not found in demo data".
SEARCH_STOPWORDS = {
    "book", "books", "kitab", "kitaab", "find", "search", "available",
    "availability", "author", "subject", "does", "not", "exist", "exists",
    "that", "this", "want", "need", "please", "show", "give", "me", "a",
    "an", "the", "on", "about", "mujhe", "chahiye", "karo", "batao",
    "hai", "hain", "ki", "ka", "ko", "library",
}


def _demo_policy_key(low):
    """Which demo sample policy (if any) a question is about."""
    if any(k in low for k in ["fine", "jurmana", "late"]):
        return "fine"
    if any(k in low for k in ["member", "card"]):
        return "membership"
    if "renew" in low:
        return "renew"
    if any(k in low for k in ["return", "wapas"]):
        return "return"
    if any(k in low for k in ["borrow", "rule"]):
        return "borrow"
    return None


# ---------- Intent layer (answer-quality upgrade) ----------
# The strict FAQ matchers are precise but brittle: a one-letter typo
# ("servise", "scholer") or a natural paraphrase used to fall through
# every check and land in the book search, so a services question got
# "Sorry, I could not find that book...". This layer fixes the routing
# WITHOUT touching the FAQ modules or the database:
#   1. spelling normalization for common English/Roman-Urdu typos,
#   2. greeting/thanks handling before everything else,
#   3. assisted FAQ matching (content-word coverage + clear margin),
#   4. multi-topic answers (each part answered separately),
#   5. a book-search GATE - book results only for book questions,
#   6. a short clarification reply instead of a generic paragraph.

_SPELLING_VARIANTS = {
    "servise": "service", "servises": "services", "sarvice": "service",
    "libary": "library", "libraray": "library", "libray": "library",
    "liberry": "library", "scholer": "scholar", "scholr": "scholar",
    "refrence": "reference", "refrences": "reference",
    "turnitn": "turnitin", "timming": "timing",
    "timmings": "timings", "emial": "email", "adress": "address",
    "facilties": "facilities", "facilites": "facilities",
    "availble": "available", "avalable": "available",
    "availabe": "available", "memership": "membership",
    "reserch": "research", "assigment": "assignment",
    "assignement": "assignment", "litrature": "literature",
    "refernce": "reference", "plagiarizm": "plagiarism",
    "turniten": "turnitin", "googel": "google", "digitial": "digital",
    "onilne": "online", "journel": "journal", "artical": "article",
    "theis": "thesis", "methodolgy": "methodology",
    "statistcs": "statistics", "databse": "database",
    "wifii": "wifi", "internt": "internet", "opning": "opening",
    "isue": "issue", "bok": "book", "boks": "books",
    "auther": "author", "subjekt": "subject",
    # Roman Urdu concept words, normalized so topic matching works
    # across languages (routing only - never shown to the user).
    "madad": "help", "likhne": "write", "likhna": "write",
    "likh": "write", "writing": "write",
    "kitab": "book", "kitaab": "book", "kitabein": "book",
    "kitabon": "book",
    "sahulat": "service", "sahulaten": "services",
    "sahulatein": "services",
    "charger": "charge", "charging": "charge", "sona": "sleep",
    "referencing": "citation",
    # 'Is X allowed?' is the same routing concept as 'Can I use X?'.
    "allowed": "use", "permitted": "use",
}


def _normalize_query(text):
    """Lowercase, punctuation-free text with common spelling mistakes
    corrected word by word. Used ONLY for routing/matching decisions -
    never shown to the user and never used as a book-search term."""
    words = re.findall(r"[a-z0-9\-]+", text.lower())
    return " ".join(_SPELLING_VARIANTS.get(w, w) for w in words)


_GREETING_STARTERS = (
    "assalam o alaikum", "assalamualaikum", "assalam", "salam", "aoa",
    "hello", "hi", "hey", "good morning", "good afternoon",
    "good evening",
)
_SMALLTALK_REMAINDERS = {
    "", "how are you", "how are you doing", "how r you",
    "kya hal hai", "kaise ho", "kese ho", "kya haal hai", "theek ho",
    "how do you do",
}
_THANKS = {
    "thank you", "thanks", "thank you so much", "shukriya",
    "bohat shukriya", "boht shukriya", "jazakallah", "jazak allah",
    "thanks a lot", "thank you very much", "bohat bohat shukriya",
}


def _greeting_remainder(norm):
    """If the normalized text starts with a greeting, return the rest
    of the message ('' for a greeting-only message); otherwise None.
    A greeting followed by a real question returns that question, so
    the question - not the greeting - gets answered."""
    for g in _GREETING_STARTERS:
        if norm == g:
            return ""
        if norm.startswith(g + " "):
            return norm[len(g):].strip(" ,.!?")
    return None


def _phone_use_question(tokens):
    """'Can I USE my mobile phone?' is a rules question, not a contact
    question - the word 'phone' alone must never hijack it."""
    t = set(tokens)
    if not ({"phone", "mobile"} & t):
        return False
    return bool({"use", "istemal", "allowed", "chala"} & t) or \
        "kar sakt" in " ".join(tokens)


_SERVICES_TOKENS = {"service", "services", "sahulat", "sahulatain",
                    "khidmat", "khidmaat"}
_FACILITY_TOKENS = {"facility", "facilities", "sahulat", "sahulatain"}
_OVERVIEW_TOKENS = {"kon", "kaun", "kn", "kya", "what", "which",
                    "available", "hain", "hai", "list", "batao", "tell",
                    "offer", "offers", "provide", "provided"}
_SPECIFIC_TOPIC_TOKENS = {"wifi", "wi-fi", "internet", "turnitin",
                          "photocopy", "printing", "discussion",
                          "room", "rooms", "ebook", "ebooks", "hec",
                          "book", "books", "kitab", "kitaab"}


def _overview_fact_key(tokens):
    """'Which services / facilities are available?' overview questions
    (including Urdu words like 'sahulat' that no keyword route knows)
    -> the matching verified overview fact, or None."""
    t = set(tokens)
    if _SPECIFIC_TOPIC_TOKENS & t or not (_OVERVIEW_TOKENS & t):
        return None
    if _SERVICES_TOKENS & t:
        return "services"
    if _FACILITY_TOKENS & t:
        return "facilities"
    return None


_FACT_SIGNALS = {
    "hours": {"open", "khulti", "khula", "band", "close", "closing",
              "timing", "timings", "hours", "schedule", "waqt", "baje"},
    "contact": {"contact", "number", "email", "address", "rabta",
                "helpline", "phone"},
    "wifi": {"wifi", "wi-fi", "internet"},
    "turnitin": {"turnitin", "similarity"},
    "ebooks": {"ebook", "ebooks", "e-book", "e-books"},
    "hec": {"hec"},
    "collections": {"collection", "collections", "printed"},
    "facilities": {"facilities", "facility", "seating"},
    "services": {"service", "services", "sahulat", "khidmat"},
}


def _multi_fact_reply(norm, roman_urdu):
    """Two different official topics asked in one message ('Library kab
    band hoti hai aur number kya hai?') -> answer each part separately
    instead of answering only one (or neither)."""
    tokens = norm.split()
    t = set(tokens)
    found = [k for k, sig in _FACT_SIGNALS.items() if sig & t]
    if "contact" in found and _phone_use_question(tokens):
        found.remove("contact")
    if len(found) != 2:
        return None
    if not any(c in norm for c in (" aur ", " and ", " & ", "?")):
        return None
    return "\n\n---\n\n".join(get_fact(k, roman_urdu) for k in found)


# Function/auxiliary words (English + Roman Urdu) carry no topic, so
# they are removed before assisted matching: "Google Scholar kaise use
# karun?" must be scored on {google, scholar, use} alone, otherwise
# every Urdu auxiliary word dilutes the match into failure.
_AUX_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "do", "does", "did",
    "can", "could", "should", "would", "i", "me", "my", "we", "you",
    "your", "it", "its", "in", "on", "of", "for", "to", "from", "by",
    "at", "with", "about", "what", "how", "when", "where", "why",
    "which", "who", "please", "tell", "give", "show",
    "kya", "hai", "hain", "ka", "ki", "ke", "ko", "mein", "se", "aur",
    "par", "bhi", "to", "ye", "yeh", "wo", "woh", "aap", "ap", "main",
    "mera", "meri", "mujhe", "apni", "apna", "apne", "liye",
    "kaise", "kab", "kahan", "kyun", "kyon", "kar", "karo", "karun",
    "karna", "karne", "karte", "karti", "karein", "karta",
    "banaun", "banta", "banti", "hoga", "hogi", "milega", "milegi",
    "milenge", "dein", "parta", "parti", "padta",
    "sakte", "sakta", "sakti", "chahiye", "batao",
    "batain", "hota", "hoti", "hote", "wala", "wali", "wale", "kuch",
    "koi", "ne", "ho", "hun", "he", "ha", "tha", "thi",
    "cheez", "kaisa", "kesi", "aisa", "aisi", "waisa", "thing",
    "something", "anything", "stuff", "everything",
}


_TOPIC_STEMS = {"these": "thesis", "theses": "thesis",
                "citation": "cite", "citations": "cite",
                "citing": "cite"}
_NO_STEM = {"thesis", "analysis", "basis"}
_RU_MARKERS = {"mein", "hai", "hain", "kya", "sakte", "sakta",
               "kar", "ka", "ki", "ke", "ko", "se"}


def _topic_word_list(text):
    """Ordered topic words (see _topic_words) - order matters for
    phrase detection: 'research paper' as a phrase is a stronger
    signal than the two words separately."""
    raw = re.findall(r"[a-z0-9\-]+", text.lower())
    ru_context = bool(set(raw) & _RU_MARKERS)
    norm_text = _normalize_query(text).replace(
        "group study", "discussion room")
    out = []
    for w in norm_text.split():
        if w == "so" and ru_context:
            w = "sleep"
        if w in _AUX_WORDS or len(w) < 3:
            continue
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss") \
                and w not in _NO_STEM:
            w = w[:-1]
        out.append(_TOPIC_STEMS.get(w, w))
    if "mobile" in out:
        out = ["phone" if w == "mobile" else w for w in out]
    return out


def _topic_words(text):
    """The topic-carrying words of a question: spelling-normalized,
    auxiliary words removed, light plural stemming (phones -> phone)
    applied consistently to questions and FAQ canonicals alike."""
    raw = re.findall(r"[a-z0-9\-]+", text.lower())
    ru_context = bool(set(raw) & _RU_MARKERS)
    norm_text = _normalize_query(text).replace(
        "group study", "discussion room")  # one concept, two phrasings
    out = set()
    for w in norm_text.split():
        if w == "so" and ru_context:
            w = "sleep"  # Roman Urdu 'so sakte hain' = 'can I sleep'
        if w in _AUX_WORDS or len(w) < 3:
            continue
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss") \
                and w not in _NO_STEM:
            w = w[:-1]
        out.add(_TOPIC_STEMS.get(w, w))
    if "mobile" in out:
        # 'mobile' and 'phone' are one concept - counting both would
        # dilute coverage ('mobile silent karna hai?' vs the phone
        # rule), so keep only 'phone'.
        out.discard("mobile")
        out.add("phone")
    return out


_PAIR_BLOCK = {"use", "library", "book", "get", "make", "find",
               "help", "student", "students", "online", "free",
               "good", "many", "much", "first"}

# Generic words that must never be answered from a single-word query
# ('help' alone gets a clarification, not a random FAQ about help).
_SINGLE_WORD_BLOCK = {
    "help", "information", "service", "services", "online", "study",
    "data", "free", "work", "use", "find", "get", "make", "good",
    "best", "paper", "research", "book", "library", "download",
    "search", "available", "access", "account", "website", "open",
    "close", "start", "check", "learn", "learning", "read",
    "reading", "write", "writing", "guide", "support", "list",
    "show", "tell", "give", "know", "want", "need", "question",
    "questions", "detail", "details", "step", "steps", "topic",
    "topics", "course", "courses", "class", "classes", "student",
    "students", "user", "users", "people", "time", "long", "many",
    "much", "difference", "example", "examples", "important",
    "benefits", "tips", "resources", "resource", "tools", "tool",
    "materials", "material", "content", "part", "parts", "type",
    "types", "way", "ways", "meaning", "mean", "means",
}

# Named products/portals/services. If an FAQ is about one of these and
# the user never mentioned it, that FAQ is probably about a different
# thing than the user asked (e.g. 'Can I use the E-BOOKS PORTAL on my
# mobile phone?' must not answer 'Can I use my phone in the library?').
_SPECIFIC_ENTITIES = {
    "portal", "e-book", "e-books", "ebook", "ebooks", "turnitin",
    "zotero", "mendeley", "endnote", "spss", "smartpls", "nvivo",
    "maxqda", "scholar", "hec", "ieee", "emerald", "scopus",
    "sciencedirect", "pubmed", "orcid", "researchgate", "linkedin",
    "coursera", "edx", "udemy", "kaggle", "tableau", "qgis", "doi",
    "whatsapp", "facebook", "youtube", "instagram", "gmail",
    "proquest", "jstor", "springer", "wiley", "taylor", "francis",
    "libgen", "sci-hub", "google",
}

_FAQ_INDEX = None
_WORD_HITS = None


def _faq_index():
    """Every FAQ's canonical-question topic words, per module, plus a
    count of how many FAQs use each word (for distinctiveness
    tie-breaks). Built once, lazily."""
    global _FAQ_INDEX, _WORD_HITS
    if _FAQ_INDEX is None:
        _FAQ_INDEX = []
        _WORD_HITS = {}
        for rank, (faqs, answer_fn) in enumerate((
            (RULES_FAQS, faq_answer),
            (SERVICES_FAQS, service_faq_answer),
            (ACADEMIC_FAQS, academic_faq_answer),
            (DIGITAL_FAQS, digital_faq_answer),
            (GUIDES_FAQS, guide_faq_answer),
        )):
            for faq in faqs:
                words = _topic_words(faq["q_en"]) | \
                    _topic_words(faq["q_ru"])
                pairs = set()
                for q in (faq["q_en"], faq["q_ru"]):
                    lst = _topic_word_list(q)
                    pairs |= set(zip(lst, lst[1:]))
                _FAQ_INDEX.append((words, faq, answer_fn, rank, pairs))
                for w in words:
                    _WORD_HITS[w] = _WORD_HITS.get(w, 0) + 1
    return _FAQ_INDEX


def _assisted_faq_answer(text, roman_urdu):
    """Stage-2 FAQ matching for natural or misspelled phrasings the
    strict matchers miss. The question's topic words are scored
    against all 746 canonical questions (coverage = share of the
    user's topic words the FAQ's question also uses). Acceptance
    needs coverage >= 60% AND a decisive win: a clear margin over the
    runner-up, very high coverage, or a strict win on the tie-breaks
    (smaller/more general canonical question, then more distinctive
    overlapping words). FAQs about a named product/portal the user
    never mentioned are only used when no clean candidate reaches
    60% - so one similar word can never hijack an answer."""
    user_words = _topic_words(text)
    if not user_words:
        return None
    _faq_index()
    if len(user_words) == 1:
        # A single topic word is enough only when it is distinctive
        # (used by few FAQs) and not a generic word like 'help' -
        # a lone generic word gets a clarification, not a guess.
        w = next(iter(user_words))
        if w in _SINGLE_WORD_BLOCK or _WORD_HITS.get(w, 99) > 25:
            return None
    # Concept expansion for scoring only: a thesis question is also
    # about dissertations (the FAQ category's own wording), so both
    # words count for overlap - but coverage is still measured
    # against the words the user actually used.
    expanded = set(user_words)
    if "thesis" in expanded:
        expanded.add("dissertation")
    user_list = _topic_word_list(text)
    user_pairs = set(zip(user_list, user_list[1:]))
    scored = []
    for pos, (words, faq, answer_fn, rank, pairs) in \
            enumerate(_FAQ_INDEX):
        overlap = expanded & words
        if len(overlap) >= 2 or (len(user_words) == 1 and overlap):
            idf = sum(1.0 / _WORD_HITS[w] for w in overlap)
            # Phrase bonus: an FAQ whose question uses the user's
            # own two-word phrase ('research paper', 'thesis write')
            # is about exactly that thing, not just the words. A
            # pair of two ultra-common words ('use library') is not
            # a phrase and earns no bonus.
            bonus = 1 if any(
                p in pairs and not (p[0] in _PAIR_BLOCK
                                    and p[1] in _PAIR_BLOCK)
                for p in user_pairs) else 0
            cov = min(1.0, (len(overlap) + bonus) / len(user_words))
            scored.append((cov, len(words), idf, rank,
                           frozenset(overlap), words, faq, answer_fn,
                           pos))
    if scored:
        clean = [s for s in scored
                 if not ((s[5] & _SPECIFIC_ENTITIES) - user_words)]
        pool = clean if any(s[0] >= 0.6 for s in clean) else scored
        # Winner order: coverage, then - among equals - an FAQ whose
        # overlap covers ALL of the user's distinctive words (used
        # by <= 5 FAQs, e.g. 'harvard': the Harvard FAQ must beat a
        # generic APA FAQ that merely shares 'style'), then the
        # more general (smaller) canonical question, then IDF,
        # then earlier module (official before general guidance).
        _distinct = {w for w in user_words
                     if _WORD_HITS.get(w, 99) <= 5}
        pool.sort(key=lambda s: (
            -s[0],
            0 if _distinct and _distinct <= set(s[4]) else 1,
            s[1], -s[2], s[3], s[8]))
        best_cov, best_size, best_idf, best_rank, best_ov = pool[0][:5]
        if best_cov >= 0.6:
            rivals = [s for s in pool[1:] if best_cov - s[0] < 0.12]
            decisive = (
                not rivals
                or best_cov >= 0.75
                or (best_cov >= 0.66 and all(
                    s[1] > best_size
                    or (s[1] == best_size and s[2] < best_idf)
                    or (s[1] == best_size and s[2] == best_idf
                        and s[3] > best_rank)
                    or (s[1] == best_size and s[2] == best_idf
                        and s[3] == best_rank and s[4] == best_ov)
                    for s in rivals))
            )
            if decisive:
                return pool[0][7](pool[0][6]["q_en"], roman_urdu)
    # Fallback 1: the user named ONE specific product/platform that
    # only a few FAQs cover ('coursera par course karna hai') - the
    # most general of those FAQs is the right answer.
    ents = [w for w in user_words
            if w in _SPECIFIC_ENTITIES and _WORD_HITS.get(w, 99) <= 6]
    if len(ents) == 1:
        cands = [(len(words), rank, pos, faq, answer_fn)
                 for pos, (words, faq, answer_fn, rank, _p)
                 in enumerate(_FAQ_INDEX) if ents[0] in words]
        if cands:
            cands.sort()
            return cands[0][4](cands[0][3]["q_en"], roman_urdu)
    # Fallback 2: a very distinctive word (used by at most 2 of the
    # 746 FAQs, e.g. 'interview') - the FAQ that uses it is almost
    # certainly the one the user means.
    rare = [w for w in user_words if _WORD_HITS.get(w, 99) <= 2]
    if rare:
        cands = []
        for pos, (words, faq, answer_fn, rank, _p) in \
                enumerate(_FAQ_INDEX):
            hits = len(set(rare) & words)
            if hits:
                cands.append((-hits, len(words), rank, pos, faq,
                              answer_fn))
        if cands:
            cands.sort()
            return cands[0][5](cands[0][4]["q_en"], roman_urdu)
    return None


_BOOK_INTENT_TOKENS = {"book", "books", "kitab", "kitaab", "novel",
                       "novels", "textbook", "textbooks"}
_GENERIC_TOKENS = {"library", "science", "studies", "study", "system",
                   "systems", "introduction", "management", "university",
                   "research", "education", "learning", "general"}
_CATALOGUE_TOKENS = None


def _catalogue_tokens():
    """Signals from the real demo catalogue, built once:
    - author words (in at most 6 of the 80 books): a strong book
      signal at any query length - nobody asks about 'Tanenbaum'
      except for his books;
    - the exact normalized titles: typing a book's full title IS a
      book question, however many words it has ('Python Crash
      Course', 'Operating System Concepts');
    - distinctive title/subject words: a book signal only in SHORT
      queries ('python', 'data structures') - in a longer sentence
      the same word is usually a topic, not a book request ('thesis
      likhne mein madad chahiye' asks for help, not a book);
    - any word appearing in a title: enough for a one-word query
      ('management', 'algorithms') - except ambient words about the
      library itself ('library' alone asks for clarification)."""
    global _CATALOGUE_TOKENS
    if _CATALOGUE_TOKENS is None:
        author_counts, title_counts = {}, {}
        titles, title_words = set(), set()
        for subject in count_by_subject():
            for b in search_books(subject, search_by="subject"):
                titles.add(_normalize_query(b["title"]))
                for w in set(re.findall(r"[a-z]+", b["author"].lower())):
                    author_counts[w] = author_counts.get(w, 0) + 1
                for w in set(re.findall(r"[a-z]+", b["title"].lower())):
                    title_words.add(w)
                    title_counts[w] = title_counts.get(w, 0) + 1
                for w in set(re.findall(r"[a-z]+", b["subject"].lower())):
                    title_counts[w] = title_counts.get(w, 0) + 1
        pick = lambda counts: {
            w for w, c in counts.items()
            if len(w) >= 4 and c <= 6 and w not in _GENERIC_TOKENS
        }
        _CATALOGUE_TOKENS = (pick(author_counts), pick(title_counts),
                             titles, title_words)
    return _CATALOGUE_TOKENS


def _has_book_intent(text, norm):
    """Book results are ONLY for book questions: an explicit book word,
    a quoted title, an author pattern or name, an exact catalogue
    title, or a distinctive catalogue word in a short query.
    Everything else must never reach the book search."""
    tokens = set(norm.split())
    if "open access" in norm:
        return False  # a digital-resources concept, never a book
        # search - even though a demo title contains the word 'Access'
    if _BOOK_INTENT_TOKENS & tokens:
        return True
    if '"' in text or " by " in f" {norm} ":
        return True
    author_tokens, title_tokens, titles, title_words = \
        _catalogue_tokens()
    if tokens & author_tokens or norm in titles:
        return True
    # A catalogue title named inside a longer question is still a
    # book question ('kya Clean Code available hai?').
    padded = f" {norm} "
    if any(f" {t} " in padded for t in titles if len(t) >= 4):
        return True
    # Two or more consecutive Capitalized words usually name a book
    # ('Harry Potter hai library mein?') - unless they name a known
    # non-book service or product.
    for pair in re.findall(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+", text):
        if pair.lower() not in ("google scholar", "hec digital",
                                "digital library", "research support",
                                "reference manager", "library ai"):
            return True
    # A distinctive catalogue word in a short query is a book signal -
    # UNLESS the query names a specific product/platform that has its
    # own FAQs ('coursera par course karna hai' is about Coursera,
    # not the book 'Python Crash Course'), or the query's other topic
    # words are not catalogue words at all ('assignment likh kar de
    # dein' contains the title word 'write' but is not a book ask).
    if tokens & _SPECIFIC_ENTITIES:
        return False
    if len(_topic_words(text)) <= 2 and tokens & title_tokens:
        stem = lambda w: w[:-1] if len(w) > 3 and w.endswith("s") \
            and not w.endswith("ss") and w not in _NO_STEM else w
        catalogue_words = {stem(w) for w in title_tokens} \
            | {stem(w) for w in author_tokens} \
            | _GENERIC_TOKENS | _BOOK_INTENT_TOKENS
        if _topic_words(text) <= catalogue_words:
            return True
    return len(tokens) == 1 and bool(tokens & title_words) \
        and tokens != {"library"}


def _clarification_reply(roman_urdu):
    """Short, relevant clarification instead of a generic paragraph or
    a wrong answer, when no intent could be identified."""
    if roman_urdu:
        return (
            "Aap ka sawal mujhe poori tarah samajh nahi aaya - zara si "
            "wazahat kar dein, taake main bilkul sahi jawab dun. Aap kis "
            "baare mein poochna chahte hain?\n"
            "- Kitabein (title, author ya subject se search)\n"
            "- Library timings ya contact details\n"
            "- Library services aur facilities\n"
            "- Digital resources (HEC Digital Library, Google Scholar, e-books)\n"
            "Misal: 'Mujhe Python ki kitab chahiye' ya 'Library kab band hoti hai?'"
        )
    return (
        "I want to make sure I answer exactly what you asked. Could you "
        "say a little more - what would you like to ask about?\n"
        "- Books (search by title, author or subject)\n"
        "- Library hours or contact details\n"
        "- Library services and facilities\n"
        "- Digital resources (HEC Digital Library, Google Scholar, e-books)\n"
        "I can also answer from 746 built-in FAQs. Try e.g. 'Find Python "
        "books' or 'What time does the library close?'"
    )


def get_reply(user_text, history=None):
    """Main brain, in order: explicit demo-policy request, greetings,
    strict FAQ modules, unpublished-policy honesty, multi-topic and
    assisted FAQ matching, official facts, circulation, GATED SQLite
    book search (book questions only), Groq/clarification."""
    text = user_text.strip()
    low = text.lower()
    roman_urdu = is_roman_urdu(text)

    # 1. Explicit demo-policy request ONLY (D1): the user must actually
    # ask about the demo project's sample rules. The answer always
    # begins with the exact DEMO ONLY label.
    if "demo" in low or "sample" in low:
        key = _demo_policy_key(low)
        if key:
            return f"{DEMO_LABEL}\n\n{DEMO_POLICY_ANSWERS[key]}"

    norm = _normalize_query(text)
    norm_tokens = norm.split()

    # 1b. Thanks and greeting-only messages get a natural reply. A
    # greeting followed by a real question falls through, so the
    # question itself - not the greeting - is answered.
    if norm in _THANKS:
        if roman_urdu or norm.split()[0] in ("shukriya", "jazakallah", "jazak"):
            return "Khushi hui madad karke! Agar library, kitabon ya digital resources ke baare mein aur kuch poochna ho to main hazir hoon."
        return "You're welcome! If you need anything else about the library, books or digital resources, just ask."
    # 1c. Pirated-site questions get the stored warning answer
    # (DL100: pirate libraries such as LibGen distribute copyrighted
    # material illegally) before anything else can claim them -
    # never a book search, never a recommendation.
    if "libgen" in norm_tokens or "sci-hub" in norm_tokens or (
            "sci" in norm_tokens and "hub" in norm_tokens):
        for _f in DIGITAL_FAQS:
            if _f["id"] == "DL100":
                return digital_faq_answer(_f["q_en"], roman_urdu)

    # 1d. 'Write my assignment for me' delegation requests get the
    # honest stored answer (AC10: the library helps you learn to do
    # it, it does not do it for you) - not a random writing FAQ.
    if ("assignment" in norm or "homework" in norm) and (
            re.search(r"\b(likh|bana|kar|solve) (kar )?(de|do|dein)\b",
                      norm)
            or "write my" in norm or "do my" in norm):
        for _f in ACADEMIC_FAQS:
            if _f["id"] == "AC10":
                return academic_faq_answer(_f["q_en"], roman_urdu)

    remainder = _greeting_remainder(norm)
    if remainder is not None and remainder in _SMALLTALK_REMAINDERS:
        if roman_urdu or norm.split()[0] in ("salam", "aoa", "assalam", "assalamualaikum"):
            return "Wa Alaikum Assalam! Main UOS Library AI hoon. Aap demo catalogue mein kitab search kar sakte hain, ya official library timing, services, Turnitin aur contact ke baare mein pooch sakte hain."
        return "Hello! I am UOS Library AI. You can search the demo book catalogue, or ask about official library hours, services, Turnitin and contact details."

    # 2. Rules & Regulations FAQs (library_faq.py) - official Code of
    # Conduct / payment form / information page answers. The matcher is
    # strict (distinctive phrases, no ties), so this only fires on a
    # strong rules match and never hijacks book searches or the
    # unpublished-policy questions handled in step 3.
    faq = faq_answer(text, roman_urdu)
    if faq:
        return faq

    # 2b. Facilities & Services FAQs (library_services_faq.py) - 60 FAQs
    # from the official Library Spaces, Information Services and
    # Research Support Lab pages. Checked after the rules FAQs so
    # rules answers keep priority; same strict matching, so unrelated
    # questions fall through safely.
    svc = service_faq_answer(text, roman_urdu)
    if svc:
        return svc

    # 2c. Academic & Research Assistance FAQs (library_academic_faq.py)
    # - 80 FAQs of general academic guidance (assignments, topics,
    # literature reviews, methodology, referencing, tools, thesis
    # writing, ethics). Checked after the rules and services FAQs so
    # official answers keep priority; same strict matching.
    acad = academic_faq_answer(text, roman_urdu)
    if acad:
        return acad

    # 2d. Digital Library & Online Resources FAQs
    # (library_digital_faq.py) - COMPLETE: all 10 approved batches
    # of 50 (DL001-DL500, 25 categories x 20 - e-books portal, HEC
    # Digital Library, academic databases, Google Scholar, open
    # access, paper/PDF finding, academic search engines, e-books
    # & e-journals, Zotero, Mendeley & EndNote, AI research
    # assistants, advanced searching, keywords & Boolean, journal
    # quality & indexing, DOI & citation tracking, research data
    # & statistics, digital access & troubleshooting, online
    # learning platforms, copyright & OA ethics, digital literacy
    # & online safety, thesis & dissertation databases, systematic
    # reviews & meta-analysis, research collaboration & academic
    # profiles, research visualization & data tools, subject-
    # specific digital resources). Checked after the academic FAQs
    # so earlier modules keep priority; same strict matching.
    digi = digital_faq_answer(text, roman_urdu)
    if digi:
        return digi

    # 2e. Student Guidance & Procedural Knowledge guides
    # (library_guides_faq.py) - Stage 4.6: 6 step-by-step guides
    # (G01-G06) assembled only from already-verified facts, incl.
    # honest not-published guides for membership, lost cards and
    # complaints. Checked after the four FAQ modules so their
    # specific answers keep priority; same strict matching.
    guide = guide_faq_answer(text, roman_urdu)
    if guide:
        return guide

    # 3. Real policy questions that are NOT officially published (D1):
    # honest "not published" + library contact. No demo figures, ever.
    # Checked BEFORE the official routes: "How many books can I borrow?"
    # is a borrow-limit question, not a collections question.
    for keywords, _key, topic_en, topic_ur in POLICY_ROUTES:
        if any(k in low or k in norm for k in keywords):
            return policy_not_published(topic_en, topic_ur, roman_urdu)

    # 3b. Two official topics in one message: answer each part
    # separately (e.g. closing time AND contact number).
    multi = _multi_fact_reply(norm, roman_urdu)
    if multi:
        return multi

    # 4. Official verified information (library_info.py), with sources.
    # Keywords are checked against the original text AND the
    # spelling-normalized text, so 'servise' still finds services.
    for keywords, key in OFFICIAL_ROUTES:
        if key == "contact" and _phone_use_question(norm_tokens):
            continue
        if key == "services" and "reference manager" in norm:
            continue  # a reference MANAGER (Zotero/Mendeley) question,
            # not the library's reference service - assisted matching
            # below owns it
        if key == "services" and set(norm_tokens) & {
                "apa", "harvard", "citation", "mla", "chicago",
                "vancouver", "referencing"}:
            continue  # a CITATION-style question ('apa format mein
            # reference kaise banaun?'), not the library's reference
            # service - the academic FAQs own it
        if key == "hours" and "open access" in norm:
            continue  # 'open access kya hai?' is a digital-resources
            # question, not an opening-hours question
        if any(k in low or k in norm for k in keywords):
            return get_fact(key, roman_urdu)

    # 4a. Overview questions ('which services are available?', 'kon
    # kon si sahulat hain?') that no route caught get the verified
    # services/facilities overview - never a book answer.
    overview = _overview_fact_key(norm_tokens)
    if overview:
        return get_fact(overview, roman_urdu)

    # 4c. Assisted FAQ matching (stage 2): natural or misspelled
    # phrasings the strict matchers missed. Runs after the official
    # routes (which own hours/contact/etc.), and the contact route
    # above is guarded, so a mobile-phone RULE question reaches the
    # rules FAQ here instead of being hijacked by the word 'phone'.
    # Skipped for clear book questions - those belong to the book
    # search below ('Find Python books' must return books, not an
    # FAQ that happens to share the words 'find' and 'book'). Two
    # exceptions: citation-style questions that merely MENTION a
    # book ('apa mein book ka reference kaise banta hai?') and
    # own-book rule questions ('apni kitab parh sakte hain?') are
    # FAQ questions, not catalogue searches.
    _cite_ctx = bool(set(norm_tokens) & {
        "apa", "harvard", "citation", "mla", "chicago", "vancouver",
        "referencing"})
    _own_ctx = "apni kitab" in low or "apni book" in low \
        or "own book" in low
    if _cite_ctx or _own_ctx or not _has_book_intent(text, norm):
        assisted = _assisted_faq_answer(text, roman_urdu)
        if assisted:
            return assisted

    # 4b. Borrowing / returning process: the official circulation-desk
    # answer (limits themselves stay unpublished - see step 3).
    if any(k in low for k in ["borrow", "issue", "lena", "return", "wapas"]):
        return get_fact("circulation", roman_urdu)

    # 5. Book search & recommendations - SQLite ONLY (database.py).
    # Order inside this step: subject browsing -> subject mode ->
    # author mode -> title mode -> ranked general search -> honest
    # not-found with suggestions. Stopword protection is preserved.
    subjects = list(count_by_subject().keys())

    # 5a. Subject browsing: list all subjects with their real counts.
    if any(p in low for p in [
            "list subjects", "which subjects", "what subjects", "show subjects",
            "browse subjects", "subjects available", "subjects hain",
            "subjects ki list", "browse by subject", "books by subject"]):
        return _subject_browse_reply(roman_urdu)

    # 5b. Subject mode: a subject name is mentioned and the user wants
    # its books (or typed just the subject). Shows ALL of its books.
    for subject in subjects:
        if subject.lower() in low:
            wants_books = any(w in low for w in [
                "book", "books", "kitab", "kitaab", "show", "list",
                "browse", "dikhao", "batao"]) or low.strip(" ?.!,") == subject.lower()
            if wants_books:
                books = search_books(subject, search_by="subject")
                books.sort(key=lambda b: (0 if b["available_copies"] > 0 else 1, b["title"]))
                intro = (
                    f"Demo catalogue mein **{subject}** ki {len(books)} kitabein (demonstration data):"
                    if roman_urdu else
                    f"📚 Here are all {len(books)} **{subject}** books in the demo catalogue (demonstration data):"
                )
                return format_books(books, roman_urdu, intro=intro)

    # 5c. Author mode: "books by X" / "X ki books" style wording.
    author_match = re.search(r"\bby\s+([a-z][a-z .']{2,})$", low) or \
        re.search(r"\bbooks?\s+by\s+([a-z][a-z .']{2,})", low)
    if author_match:
        name = author_match.group(1).strip(" ?.!,")
        books = search_books(name, search_by="author")
        if not books and " " in name:  # fall back to the surname
            books = search_books(name.split()[-1], search_by="author")
        if books:
            books = _rank_books(books, name)
            return format_books(books, roman_urdu) + (
                _recommendation_block(books[0], books, roman_urdu)
                if len(books) <= 3 else "")

    # 5d. Title mode: quoted text, or "book titled/called/named X".
    title_match = re.search(r'"([^"]{3,})"', text) or \
        re.search(r"\b(?:titled|called|named)\s+(.+)$", low)
    if title_match:
        name = title_match.group(1).strip(" ?.!,")
        books = search_books(name, search_by="title")
        if books:
            books = _rank_books(books, name)
            return format_books(books, roman_urdu) + (
                _recommendation_block(books[0], books, roman_urdu)
                if len(books) <= 3 else "")

    # 5e. General search - GATED: this step runs ONLY when the user is
    # actually asking about books (explicit book words, a quoted
    # title, an author pattern, or a distinctive catalogue word).
    # A non-book question must never be answered with book results.
    # Whole text first, then each word longest-first, so "Mujhe Python
    # ki kitab chahiye" finds Python (not "chahiye"). Results are
    # ranked (exact title > title > author > subject), ALL shown.
    if _has_book_intent(text, norm) and not _cite_ctx and not _own_ctx:
        words = sorted({w.strip("?.!,") for w in text.split()}, key=len, reverse=True)
        for query in [text] + words:
            if len(query) < 3 or query.lower() in SEARCH_STOPWORDS:
                continue
            books = search_books(query)
            if books:
                books = _rank_books(books, query)
                reply = format_books(books, roman_urdu)
                if len(books) <= 3:
                    reply += _recommendation_block(books[0], books, roman_urdu)
                return reply

        # 5f. Book question, nothing found: honest not-found +
        # spelling/subject suggestions. Only reachable inside the
        # gate, i.e. for genuine book questions ('Harry Potter hai
        # library mein?' gets not-found, not a clarification).
        return _not_found_reply(text, low, roman_urdu)

    # 6. General chat via Groq when a key exists (never for book
    # availability), otherwise a short clarification question - a
    # student should never get an unrelated answer or a generic
    # paragraph when a specific answer exists.
    ai_reply = ask_groq_or_fallback(text, roman_urdu, history=history)
    if ai_reply:
        return ai_reply

    return _clarification_reply(roman_urdu)


# ---------- Multiple-chat history ----------
# Chats live in st.session_state while the app runs. GUESTS stay
# session-only: nothing is written anywhere, chats vanish with the
# tab. SIGNED-IN STUDENTS (Stage 4) get the same in-session chats
# mirrored to their private Supabase account - every query there
# is filtered by their user id AND protected by Row Level
# Security, so no student can ever see another's chats.
GREETING = {
    "role": "assistant",
    "content": "Hello! 👋 I am **UOS Library AI**. Ask me to find a book in the demo catalogue, or ask about official library hours, services, Turnitin and contact details. Try: *Find Python books*",
}


def _next_activity():
    """A simple increasing counter: bigger = more recently active."""
    counter = st.session_state.get("activity_counter", 0) + 1
    st.session_state.activity_counter = counter
    return counter


def touch_current_chat():
    """Mark the current chat as the most recently active one."""
    chat = st.session_state.chats.get(st.session_state.get("current_chat_id"))
    if chat is not None:
        chat["last_active"] = _next_activity()


def start_new_chat():
    """Create a fresh, empty chat, make it the current one, return its id."""
    chat_id = uuid.uuid4().hex[:8]
    st.session_state.chats[chat_id] = {
        "title": "New chat",
        "messages": [dict(GREETING)],
        "last_active": _next_activity(),
    }
    st.session_state.current_chat_id = chat_id
    # "messages" always points to the current chat's message list,
    # so the rest of the app keeps working with one simple list.
    st.session_state.messages = st.session_state.chats[chat_id]["messages"]
    return chat_id


def open_chat(chat_id):
    """Reopen an earlier chat so the user can read and continue it."""
    if chat_id in st.session_state.chats:
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = st.session_state.chats[chat_id]["messages"]
        touch_current_chat()


def sorted_chat_items():
    """(chat_id, chat) pairs, most recently active first - sidebar order."""
    return sorted(
        st.session_state.chats.items(),
        key=lambda item: item[1].get("last_active", 0),
        reverse=True,
    )


def ensure_chat_state():
    """Set up the chats dictionary and a first chat, if needed."""
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    # Chats created before ordering existed get a starting value.
    for chat in st.session_state.chats.values():
        if "last_active" not in chat:
            chat["last_active"] = _next_activity()
    if "current_chat_id" not in st.session_state or (
        st.session_state.current_chat_id not in st.session_state.chats
    ):
        start_new_chat()
    else:
        st.session_state.messages = st.session_state.chats[
            st.session_state.current_chat_id
        ]["messages"]


def set_chat_title_from_first_question(prompt):
    """Title = first user question in this chat, shortened for the sidebar."""
    chat = st.session_state.chats[st.session_state.current_chat_id]
    if chat["title"] == "New chat":
        title = prompt.strip()
        chat["title"] = title[:32] + "..." if len(title) > 32 else title


# ---------- Stage 4: student accounts & permanent history ----------
# All database work goes through supabase_store (anon key + the
# student's own session; RLS enforces ownership in the database).
# Guests never touch it: no rows are written for them, ever.

def _accounts_on():
    return store is not None and store.accounts_enabled()


def _sb_user():
    """{'id', 'email'} of the signed-in student, or None (guest)."""
    return st.session_state.get("sb_user")


def _sb_client():
    """The signed-in student's Supabase client (restored from the
    session tokens when needed), or None."""
    if not _accounts_on():
        return None
    client = st.session_state.get("sb_client")
    if client is not None:
        return client
    tokens = st.session_state.get("sb_tokens")
    if tokens:
        client = store.restore_client(tokens[0], tokens[1])
        if client is not None:
            st.session_state.sb_client = client
            return client
    return None


def _notice(kind, text):
    st.session_state.sb_notice = (kind, text)


def _load_db_chats(client, user):
    """Replace the session chats with the student's saved ones
    (titles + timestamps come from the database; the static
    greeting is prepended locally - it is never stored)."""
    chats = {}
    convs = store.list_conversations(client, user["id"])
    for i, conv in enumerate(reversed(convs)):
        msgs = [dict(GREETING)]
        for m in store.get_messages(client, user["id"], conv["id"]):
            if m.get("role") in ("user", "assistant"):
                msgs.append({"role": m["role"],
                             "content": m["content"]})
        cid = uuid.uuid4().hex[:8]
        chats[cid] = {"title": conv.get("title") or "New chat",
                      "messages": msgs, "last_active": i + 1,
                      "db_id": conv["id"],
                      "updated_at": conv.get("updated_at")}
    st.session_state.chats = chats
    st.session_state.activity_counter = len(chats)
    if chats:
        current = max(chats,
                      key=lambda c: chats[c].get("last_active", 0))
        st.session_state.current_chat_id = current
        st.session_state.messages = chats[current]["messages"]
    else:
        start_new_chat()


def _after_auth(session, client, notice_text):
    """Common success path for login / register / recovery."""
    user = {"id": session["user_id"], "email": session["email"]}
    st.session_state.sb_user = user
    st.session_state.sb_client = client
    if session.get("access_token"):
        st.session_state.sb_tokens = (
            session["access_token"], session["refresh_token"])
    store.ensure_profile(client, user["id"], user["email"])
    _load_db_chats(client, user)
    _notice("success", notice_text)


def _do_sign_out():
    client = _sb_client()
    if client is not None:
        store.sign_out(client)
    for key in ("sb_user", "sb_client", "sb_tokens", "sb_recovery"):
        st.session_state.pop(key, None)
    st.session_state.chats = {}
    start_new_chat()
    _notice("success",
            "You have been signed out. You are now a guest; new "
            "chats will not be saved.")


def _persist_exchange(prompt, reply):
    """Save the just-finished exchange for a signed-in student
    (creating the conversation row on its first exchange). Guests:
    nothing is stored anywhere."""
    user = _sb_user()
    if not user:
        return
    client = _sb_client()
    if client is None:
        return
    chat = st.session_state.chats.get(
        st.session_state.current_chat_id)
    if chat is None:
        return
    db_id = chat.get("db_id")
    if not db_id:
        db_id = store.create_conversation(
            client, user["id"], chat.get("title") or "New chat")
        if db_id:
            chat["db_id"] = db_id
    if not db_id:
        return
    store.append_message(client, user["id"], db_id, "user", prompt)
    store.append_message(client, user["id"], db_id, "assistant", reply)
    store.update_conversation(client, user["id"], db_id,
                              chat.get("title"))


def _delete_chat(chat_id):
    """Delete one chat: its database row too, when signed in
    (messages are removed by the database cascade)."""
    chat = st.session_state.chats.get(chat_id)
    if chat is None:
        return
    user = _sb_user()
    if user and chat.get("db_id"):
        client = _sb_client()
        if client is not None:
            store.delete_conversation(client, user["id"],
                                      chat["db_id"])
    del st.session_state.chats[chat_id]
    if st.session_state.get("current_chat_id") == chat_id:
        if st.session_state.chats:
            open_chat(max(
                st.session_state.chats,
                key=lambda c: st.session_state.chats[c].get(
                    "last_active", 0)))
        else:
            start_new_chat()


def _account_panel():
    """Sidebar Student Account section: guest note, login /
    register / forgot-password form, or the signed-in controls
    (logout + delete a saved chat)."""
    T = _t()
    with st.expander(T["account"]):
        notice = st.session_state.pop("sb_notice", None)
        if notice:
            (st.success if notice[0] == "success" else st.error)(
                notice[1])
        if not _accounts_on():
            st.markdown(f'<div class="uos-guest-note">'
                        f'{T["accounts_off"]}</div>',
                        unsafe_allow_html=True)
            return
        user = _sb_user()
        if user and st.session_state.get("sb_recovery"):
            st.write("Set a new password for "
                     f"**{user['email']}**:")
            with st.form("sb_newpw"):
                new_pw = st.text_input("New password",
                                       type="password")
                save = st.form_submit_button("Set new password")
            if save:
                client = _sb_client()
                if client is not None and store.update_password(
                        client, new_pw):
                    st.session_state.pop("sb_recovery", None)
                    _notice("success", "Your password has been "
                                       "updated.")
                else:
                    _notice("error", "Could not update the password "
                                     "- please try the reset link "
                                     "again.")
                st.rerun()
            return
        if user:
            st.markdown(f"**{T['signed_in']}** {user['email']}")
            if st.button(T["logout"], key="sb_logout",
                         use_container_width=True):
                _do_sign_out()
                st.rerun()
            items = sorted_chat_items()
            if items:
                labels = {cid: c["title"] for cid, c in items}
                sel = st.selectbox(
                    "Delete a chat", list(labels),
                    format_func=lambda cid: labels[cid],
                    key="sb_del_sel", label_visibility="collapsed")
                if st.button(T["delete_chat"], key="sb_del",
                             use_container_width=True):
                    _delete_chat(sel)
                    _notice("success", "Chat deleted.")
                    st.rerun()
            return
        st.markdown(f'<div class="uos-guest-note">'
                    f'{T["guest_note"]}</div>',
                    unsafe_allow_html=True)
        with st.form("sb_auth"):
            email = st.text_input(T["email"], key="sb_email")
            password = st.text_input(T["password"], type="password",
                                     key="sb_pw")
            c1, c2 = st.columns(2)
            login = c1.form_submit_button(T["login"],
                                          use_container_width=True)
            register = c2.form_submit_button(
                T["register"], use_container_width=True)
            forgot = st.form_submit_button(T["forgot"])
        if login or register or forgot:
            client = store.new_client()
            if client is None:
                _notice("error", "Accounts are unavailable right "
                                 "now - please continue as a guest.")
            elif forgot:
                redirect = None
                try:
                    redirect = st.secrets.get("APP_URL")
                except Exception:
                    redirect = None
                if email and store.send_password_reset(
                        client, email, redirect):
                    _notice("success",
                            "If that email is registered, a "
                            "password-reset link has been sent to "
                            "it.")
                else:
                    _notice("error", "Please enter your email "
                                     "first.")
            elif login:
                session = store.sign_in(client, email, password)
                if session and not session["needs_confirmation"]:
                    _after_auth(session, client,
                                "Welcome back! Your saved chats "
                                "are loaded.")
                else:
                    _notice("error", "Login failed - check the "
                                     "email and password (or "
                                     "confirm your email first).")
            else:  # register
                session = store.sign_up(client, email, password)
                if session is None:
                    _notice("error",
                            "Registration failed - the email may "
                            "already be registered, or the password "
                            "is too short (minimum 6 characters).")
                elif session["needs_confirmation"]:
                    _notice("success",
                            "Account created. Please open the "
                            "confirmation link in your email, then "
                            "log in.")
                else:
                    _after_auth(session, client,
                                "Account created - your chats will "
                                "now be saved permanently.")
            st.rerun()


# ---------- Streamlit UI (redesigned 2026-11-23) ----------
# Frontend redesign approved by the user against a supplied visual
# reference: dark navy sidebar, light welcome dashboard with four
# category cards, suggested-question chips, About/Help/Clear Chat
# actions, English/Roman Urdu selector and Light/Dark theme.
# ONLY the presentation layer changed: get_reply(), the FAQ modules,
# the book-search logic, database.py and library.db are untouched.
# All UI code lives in main() so that importing this module (as the
# test suites do) never executes Streamlit widgets.

# Small stroke icons (feather-style paths), drawn inline as SVG so no
# image assets or official logos are needed. The reference design's
# university seal is NOT reproduced: no authorized logo asset exists
# in the project, so a clean book icon is used instead (per spec).
_ICONS = {
    "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "home": '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "folder": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "cap": '<path d="M22 10L12 5 2 10l10 5 10-5z"/><path d="M6 12.5V16c0 1.7 2.7 3 6 3s6-1.3 6-3v-3.5"/>',
    "bank": '<path d="M3 21h18"/><path d="M5 21v-8"/><path d="M9.5 21v-8"/><path d="M14.5 21v-8"/><path d="M19 21v-8"/><path d="M2 10l10-6 10 6z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    "clear": '<path d="M21 12a9 9 0 1 1-2.64-6.36"/><path d="M21 3v6h-6"/>',
}


def _icon(name, size=20, color="currentColor", sw=2):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round" '
        f'stroke-linejoin="round" style="vertical-align:-4px">{_ICONS[name]}</svg>'
    )


# Dashboard wording in both UI languages. The selector changes the
# interface text and the language of the built-in example prompts;
# typed questions keep the existing automatic EN/RU detection.
UI_TEXT = {
    "English": {
        "tagline": "Your Smart Library Assistant",
        "support": "Search books \u2022 Explore resources \u2022 Get research assistance",
        "welcome": "How can I help you today?",
        "welcome_sub": "Ask anything about the UOS Library, its services, resources or research support.",
        "try": "Try asking:",
        "home": "Home", "new_chat": "New Chat", "history": "Chat History",
        "sec_main": "Main Navigation", "sec_discovery": "Library Discovery",
        "sec_prefs": "Preferences",
        "categories": "Library Categories", "quick": "Quick Access",
        "language": "Language", "theme": "Theme", "light": "Light", "dark": "Dark",
        "about": "About", "help": "Help", "clear": "Clear Chat",
        "placeholder": "Ask anything about your library...",
        "subjects": "Demo catalogue subjects",
        "links": "Official links",
        "account": "Student Account", "email": "Email",
        "password": "Password", "login": "Log in",
        "register": "Register", "logout": "Log out",
        "forgot": "Forgot password",
        "guest_note": "Guest mode: chats stay only for this session and are not saved. Register to save your chats permanently.",
        "signed_in": "Signed in as",
        "delete_chat": "Delete selected chat",
        "accounts_off": "Student accounts are not configured on this deployment, so you are chatting as a guest and chats are not saved.",
    },
    "Roman Urdu": {
        "tagline": "Your Smart Library Assistant",
        "support": "Search books \u2022 Explore resources \u2022 Get research assistance",
        "welcome": "Main aaj aap ki kya madad kar sakta hun?",
        "welcome_sub": "UOS Library, is ki services, resources ya research support ke bare mein kuch bhi poochein.",
        "try": "Yeh pooch kar dekhein:",
        "home": "Home", "new_chat": "New Chat", "history": "Chat History",
        "sec_main": "Bunyadi Menu", "sec_discovery": "Library ke Hisse",
        "sec_prefs": "Tarjeehat",
        "categories": "Library Categories", "quick": "Quick Access",
        "language": "Language", "theme": "Theme", "light": "Light", "dark": "Dark",
        "about": "About", "help": "Help", "clear": "Clear Chat",
        "placeholder": "Apni library ke bare mein kuch bhi poochein...",
        "subjects": "Demo catalogue subjects",
        "links": "Official links",
        "account": "Student Account", "email": "Email",
        "password": "Password", "login": "Log in",
        "register": "Register", "logout": "Log out",
        "forgot": "Forgot password",
        "guest_note": "Guest mode: chats sirf is session ke liye hain, save nahi hoti. Chats hamesha ke liye save karne ke liye register karein.",
        "signed_in": "Signed in as",
        "delete_chat": "Delete selected chat",
        "accounts_off": "Is deployment par student accounts configured nahi hain, is liye aap guest ke tor par chat kar rahe hain aur chats save nahi hoti.",
    },
}

# (icon, EN title, RU title, EN description, RU description,
#  css class, EN prompt, RU prompt) for the four dashboard cards and
# the sidebar Quick Access shortcuts. Prompts are real questions the
# existing chatbot already answers reliably.
CARDS = [
    ("book", "Book Search", "Book Search",
     "Find books, check availability and get recommendations.",
     "Books dhundein, availability check karein aur recommendations lein.",
     "uos-card-blue", "Find Python books", "Mujhe Python ki kitab chahiye"),
    ("cap", "Research Help", "Research Help",
     "Get guidance on assignments, research methods and tools.",
     "Assignments, research methods aur tools par guidance lein.",
     "uos-card-green", "How do I write an abstract?", "How do I write an abstract?"),
    ("globe", "Digital Resources", "Digital Resources",
     "Explore e-books, e-journals, databases and online resources.",
     "E-books, e-journals, databases aur online resources explore karein.",
     "uos-card-purple", "What is the HEC Digital Library?", "What is the HEC Digital Library?"),
    ("bank", "Library Services", "Library Services",
     "Discover library facilities, services and user guidance.",
     "Library facilities, services aur user guidance discover karein.",
     "uos-card-yellow", "How many discussion rooms are there?", "How many discussion rooms are there?"),
]

# Sidebar Library Discovery order (Stage 4.5): Book Search,
# Digital Resources, Library Services, Research Help.
DISCOVERY_CARDS = [CARDS[0], CARDS[2], CARDS[3], CARDS[1]]

# Suggested-question chips from the approved reference (EN + RU forms).
CHIPS = [
    ("How can I search books in the UOS Library?", "How can I search books in the UOS Library?"),
    ("What is the HEC Digital Library?", "HEC Digital Library kya hai?"),
    ("How do I use Google Scholar?", "How do I use Google Scholar?"),
    ("What facilities does the library offer?", "What facilities does the library offer?"),
]

# Library Categories (sidebar expander): label -> prompt the chatbot
# already routes to the matching area.
CATEGORIES = [
    ("Book Search & Recommendations", "List subjects"),
    ("Library Usage & Daily Questions", "What time does the library open?"),
    ("Borrowing, Returning & Renewal", "Can I renew an overdue book?"),
    ("Assignment & Research Help", "How do I write an abstract?"),
    ("Digital Library & Online Resources", "What is the HEC Digital Library?"),
    ("Referencing & Citation", "How do I cite a book in APA style?"),
    ("Library Facilities & Services", "How many discussion rooms are there?"),
    ("Library Rules & Student Guidance", "Can I eat in the library?"),
]

ABOUT_TEXT = (
    "**UOS Library AI — Your Smart Library Assistant**\n\n"
    "A **student demonstration project** in the context of the University of "
    "Sargodha's Wazir Agha Library. It is **not an officially endorsed "
    "University of Sargodha application** and it has **no access to real "
    "university library records**.\n\n"
    "- The book catalogue contains **80 demonstration books** in SQLite; "
    "availability always comes from that demo database only.\n"
    "- Library facts (hours, services, Turnitin, contacts) come from the "
    "university's public pages, with sources shown in the answers. Policies "
    "that are not published there are answered honestly as not published.\n"
    "- The chatbot answers **746 built-in FAQs** (100 Rules & Regulations, "
    "60 Facilities & Services, 80 Academic & Research Assistance, 500 Digital "
    "Library & Online Resources, 6 Student Guidance guides) plus demo book "
    "search, in English and Roman Urdu.\n"
    "- Guest chats are kept only in this browser session. Students who "
    "register and log in (when accounts are configured) get their chats "
    "saved permanently and privately."
)

HELP_TEXT = (
    "**How to use UOS Library AI**\n\n"
    "- **Book Search** — ask for a title, author or subject, e.g. *Find Python "
    "books*, *Books by Tanenbaum*, or *List subjects* to browse the demo "
    "catalogue. Availability comes only from the demo database.\n"
    "- **Research Help** — assignments, literature reviews, referencing, "
    "plagiarism and research tools, e.g. *How do I write an abstract?*\n"
    "- **Digital Resources** — e-books, the HEC Digital Library, databases, "
    "Google Scholar, Zotero, systematic reviews and more, e.g. *What is the "
    "HEC Digital Library?*\n"
    "- **Library Services** — hours, spaces, discussion rooms, Research "
    "Support Lab and Turnitin, e.g. *What time does the library open?*\n\n"
    "You can ask in **English or Roman Urdu** — the assistant replies in the "
    "same language. Use **New Chat** to start a separate conversation; "
    "previous chats stay available in the sidebar during this session. "
    "Students who register in the **Student Account** panel get their "
    "chats saved permanently and privately; guests are not saved."
)

DISCLAIMER = (
    "Student demonstration project — not an officially endorsed University "
    "of Sargodha application. The book catalogue is 80 demonstration books "
    "only and does not access real university library records. Library "
    "information comes from the university's public pages, with sources."
)

_CSS = """
<style>
/* ===== Sidebar: fixed dark navy in both themes ===== */
section[data-testid="stSidebar"] { background: #0B2345; min-width: 290px; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] .stMarkdown { color: #EAF1F9 !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.16); }
section[data-testid="stSidebar"] button {
  background: transparent !important; color: #DCE7F5 !important;
  border: 1px solid rgba(255,255,255,.16) !important; border-radius: 10px !important;
  justify-content: flex-start !important; text-align: left !important;
}
section[data-testid="stSidebar"] button:hover {
  background: rgba(255,255,255,.10) !important; color: #FFFFFF !important;
}
section[data-testid="stSidebar"] a { color: #9CC2F2 !important; }
section[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.14);
}
/* ===== Main workspace: light theme ===== */
[data-testid="stAppViewContainer"] { background: #F6F8FB; }
[data-testid="stAppViewContainer"] .block-container { padding-top: 1.4rem; max-width: 1200px; }
[data-testid="stAppViewContainer"] button {
  border-radius: 999px !important; background: #FFFFFF !important;
  border: 1px solid #D3DEEB !important; color: #0B2345 !important;
}
[data-testid="stAppViewContainer"] button:hover { border-color: #0B2345 !important; }
.uos-banner {
  background: linear-gradient(115deg, #E7F0FD 0%, #F4F9FF 55%, #EAF6EE 100%);
  border: 1px solid #DCE7F5; border-radius: 20px; padding: 26px 30px; margin-bottom: 10px;
}
.uos-banner h1 { color: #0B2345; font-size: 2.1rem; margin: 0; }
.uos-banner .tag { color: #33506E; font-size: 1.05rem; margin-top: 2px; }
.uos-banner .sup {
  display: inline-block; margin-top: 12px; background: rgba(255,255,255,.75);
  border: 1px solid #D3DEEB; color: #33506E; border-radius: 999px;
  padding: 4px 14px; font-size: .85rem;
}
.uos-welcome { text-align: center; margin: 18px 0 6px 0; }
.uos-welcome h1 { color: #0B2345; font-size: 2.3rem; margin-bottom: 4px; }
.uos-welcome p { color: #5A6E84; font-size: 1.02rem; }
.uos-card { border-radius: 16px; padding: 18px 18px 12px 18px; min-height: 138px; }
.uos-card-blue { background: #E2EDFC; } .uos-card-green { background: #E2F4E8; }
.uos-card-purple { background: #EDE7FA; } .uos-card-yellow { background: #FAF0D7; }
.uos-card h3 { color: #12283F; margin: 10px 0 4px 0; font-size: 1.06rem; }
.uos-card p { color: #47617E; font-size: .88rem; line-height: 1.35; margin: 0; }
div[data-testid="stColumn"]:has(.uos-card) button {
  background: rgba(255,255,255,.65) !important; border: none !important;
  color: #0B2345 !important; font-weight: 600;
}
[data-testid="stChatMessage"] {
  background: #FFFFFF; border: 1px solid #E1E9F2; border-radius: 14px;
}
[data-testid="stChatInput"] { border-radius: 16px !important; border-color: #C4D3E6 !important; }
/* ===== Main workspace: dark theme (marker div .uos-dark present) ===== */
[data-testid="stAppViewContainer"]:has(.uos-dark) { background: #0C1A2E; }
[data-testid="stAppViewContainer"]:has(.uos-dark) h1,
[data-testid="stAppViewContainer"]:has(.uos-dark) h2,
[data-testid="stAppViewContainer"]:has(.uos-dark) h3,
[data-testid="stAppViewContainer"]:has(.uos-dark) p,
[data-testid="stAppViewContainer"]:has(.uos-dark) label,
[data-testid="stAppViewContainer"]:has(.uos-dark) .stMarkdown { color: #E9F0F8 !important; }
[data-testid="stAppViewContainer"]:has(.uos-dark) button {
  background: #16283F !important; border-color: #2A425F !important; color: #E9F0F8 !important;
}
[data-testid="stAppViewContainer"]:has(.uos-dark) .uos-banner {
  background: linear-gradient(115deg, #12283F 0%, #10233A 60%, #14301F 100%);
  border-color: #24405F;
}
[data-testid="stAppViewContainer"]:has(.uos-dark) .uos-banner .tag { color: #B9C7D9; }
[data-testid="stAppViewContainer"]:has(.uos-dark) .uos-banner .sup {
  background: rgba(255,255,255,.06); border-color: #2A425F; color: #B9C7D9;
}
[data-testid="stAppViewContainer"]:has(.uos-dark) .uos-welcome p { color: #AFC2D8 !important; }
[data-testid="stAppViewContainer"]:has(.uos-dark) .uos-card-blue { background: #1C3257; }
[data-testid="stAppViewContainer"]:has(.uos-dark) .uos-card-green { background: #1E4030; }
[data-testid="stAppViewContainer"]:has(.uos-dark) .uos-card-purple { background: #322A55; }
[data-testid="stAppViewContainer"]:has(.uos-dark) .uos-card-yellow { background: #4A3D20; }
[data-testid="stAppViewContainer"]:has(.uos-dark) .uos-card h3 { color: #F2F6FB !important; }
[data-testid="stAppViewContainer"]:has(.uos-dark) .uos-card p { color: #C3D2E4 !important; }
[data-testid="stAppViewContainer"]:has(.uos-dark) div[data-testid="stColumn"]:has(.uos-card) button {
  background: rgba(255,255,255,.10) !important; color: #FFFFFF !important;
}
[data-testid="stAppViewContainer"]:has(.uos-dark) [data-testid="stChatMessage"] {
  background: #13253D; border-color: #24405F;
}
[data-testid="stAppViewContainer"]:has(.uos-dark) [data-testid="stChatInput"] {
  background: #13253D !important; border-color: #2A425F !important;
}
.uos-dark { display: none; }
/* ===== Stage 4.5: sidebar section headings + account contrast ===== */
.uos-side-h {
  font-size: .72rem; letter-spacing: .14em; text-transform: uppercase;
  color: #8FA9C7 !important; font-weight: 700; margin: 10px 0 4px 0;
}
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
  background: #2E6BD8 !important; border-color: #2E6BD8 !important;
  color: #FFFFFF !important;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: rgba(255,255,255,.09) !important;
  border: 1px solid rgba(255,255,255,.28) !important;
}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
  color: #C9D9EE !important;
}
.uos-guest-note {
  background: rgba(46,107,216,.20); border-left: 3px solid #7FB0F5;
  border-radius: 8px; padding: 9px 12px; color: #EAF1F9 !important;
  font-size: .86rem; line-height: 1.45; margin: 6px 0;
}
/* ===== Stage 4.5: chat readability + chat-input clearance ===== */
[data-testid="stAppViewContainer"] .block-container { padding-bottom: 9rem; }
[data-testid="stChatMessage"] { padding: 12px 16px; }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
  line-height: 1.65; font-size: .98rem;
}
[data-testid="stChatMessage"] p { margin-bottom: .55rem; }
[data-testid="stChatMessage"] ul, [data-testid="stChatMessage"] ol {
  margin: .3rem 0 .7rem 0;
}
[data-testid="stChatMessage"] li { margin-bottom: .25rem; }
[data-testid="stChatMessage"] h2, [data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4 { margin: .8rem 0 .4rem 0; }
[data-testid="stChatMessage"] table {
  border-collapse: collapse; margin: .5rem 0 .8rem 0; font-size: .92rem;
}
[data-testid="stChatMessage"] th, [data-testid="stChatMessage"] td {
  border: 1px solid #D3DEEB; padding: 5px 10px;
}
[data-testid="stChatMessage"] a { color: #1F5FC4; }
[data-testid="stChatMessageAvatar"] img { border-radius: 8px; }
[data-testid="stAppViewContainer"]:has(.uos-dark) [data-testid="stChatMessage"] th,
[data-testid="stAppViewContainer"]:has(.uos-dark) [data-testid="stChatMessage"] td {
  border-color: #2A425F;
}
[data-testid="stAppViewContainer"]:has(.uos-dark) [data-testid="stChatMessage"] a {
  color: #9CC2F2;
}
</style>
"""


_AVATAR_DIR = os.path.dirname(os.path.abspath(__file__))


def _avatar_for(role):
    """Stage 4.5: one consistent professional icon per role (book
    for the assistant, profile silhouette for the user) instead of
    Streamlit's default face/robot avatars. Falls back to no
    avatar if the image file is missing."""
    path = os.path.join(_AVATAR_DIR, f"avatar_{role}.png")
    return path if os.path.exists(path) else None


def _t():
    """UI text for the currently selected interface language."""
    return UI_TEXT[st.session_state.get("ui_lang", "English")]


def _lang_idx():
    return 1 if st.session_state.get("ui_lang") == "Roman Urdu" else 0


def _submit(prompt_text):
    """Queue a prompt for the normal chat flow and show the conversation."""
    st.session_state.pending_prompt = prompt_text
    st.session_state.view = "chat"


def _sidebar():
    T = _t()
    ru = _lang_idx()
    with st.sidebar:
        # --- Branding (book icon, no unverified university seal) ---
        st.markdown(
            f'<div style="display:flex;gap:12px;align-items:center">'
            f'<div style="background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.25);'
            f'border-radius:12px;padding:9px 10px">{_icon("book", 26, "#FFFFFF")}</div>'
            f'<div><div style="font-size:1.25rem;font-weight:700;color:#FFFFFF">UOS Library AI</div>'
            f'<div style="font-size:.82rem;color:#B9CBE4">University of Sargodha</div>'
            f'<div style="font-size:.78rem;color:#8FA9C7">{T["tagline"]}</div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )
        st.write("")
        # --- Main navigation ---
        st.markdown(f'<div class="uos-side-h">{T["sec_main"]}</div>',
                    unsafe_allow_html=True)
        if st.button(T["home"], key="nav_home", use_container_width=True):
            st.session_state.view = "home"
            st.rerun()
        if st.button(T["new_chat"], key="nav_new", type="primary",
                     use_container_width=True):
            # The old chat stays saved in st.session_state.chats.
            start_new_chat()
            st.session_state.view = "home"
            st.rerun()
        if st.button(T["history"], key="nav_hist", use_container_width=True):
            st.session_state.show_history = not st.session_state.get("show_history", True)
            st.rerun()
        if st.session_state.get("show_history", True):
            # Most recently ACTIVE chat first; click reopens it.
            for chat_id, chat in sorted_chat_items():
                label = chat["title"]
                if chat_id == st.session_state.current_chat_id:
                    label = f"\u25b6 {label}"
                if st.button(label, key=f"open_{chat_id}", use_container_width=True):
                    open_chat(chat_id)
                    st.session_state.view = (
                        "chat" if len(chat["messages"]) > 1 else "home"
                    )
                    st.rerun()
        st.divider()
        # --- Library Discovery: categories + four shortcuts in
        # the Stage 4.5 order (Book Search, Digital Resources,
        # Library Services, Research Help) ---
        st.markdown(f'<div class="uos-side-h">{T["sec_discovery"]}</div>',
                    unsafe_allow_html=True)
        with st.expander(T["categories"]):
            for label, prompt_text in CATEGORIES:
                if st.button(label, key=f"cat_{label[:18]}", use_container_width=True):
                    _submit(prompt_text)
                    st.rerun()
        for i, card in enumerate(DISCOVERY_CARDS):
            title = card[1] if ru == 0 else card[2]
            if st.button(title, key=f"quick_{i}", use_container_width=True):
                _submit(card[6] if ru == 0 else card[7])
                st.rerun()
        st.divider()
        # --- Student Account (Stage 4: guest / login / saved chats) ---
        _account_panel()
        st.divider()
        # --- Preferences: language & theme (session-persistent) ---
        st.markdown(f'<div class="uos-side-h">{T["sec_prefs"]}</div>',
                    unsafe_allow_html=True)
        st.markdown(f"**{T['language']}**")
        st.segmented_control(
            "Language", ["English", "Roman Urdu"],
            key="ui_lang", label_visibility="collapsed",
        )
        st.markdown(f"**{T['theme']}**")
        st.segmented_control(
            "Theme", ["Light", "Dark"],
            key="theme", label_visibility="collapsed",
        )
        st.divider()
        # --- Demo subjects, official links, honesty caption ---
        with st.expander(T["subjects"]):
            st.markdown(
                "\n".join(
                    f"- {subject} \u2014 {n} books"
                    for subject, n in count_by_subject().items()
                )
                + "\n\nAsk e.g. *Show Business books* to browse one."
            )
        st.markdown(f"**{T['links']}**")
        st.markdown(
            "- [Wazir Agha Library](https://library.su.edu.pk/)\n"
            "- [PakCat catalogue \u2014 UOS](https://pakcat.pastic.gov.pk/library/45/university-of-sargodha)\n"
            "- [UOS E-Books](https://ebooks.su.edu.pk/)\n"
            "- [HEC Digital Library \u2014 UOS](https://www.digitallibrary.edu.pk/sargodhauni.html)"
        )
        st.caption(DISCLAIMER)


def _dashboard():
    """Welcome dashboard shown before the conversation starts."""
    T = _t()
    ru = _lang_idx()
    st.markdown(
        f'<div class="uos-banner"><div style="display:flex;gap:16px;align-items:center">'
        f'<div>{_icon("book", 52, "#0B2345", 1.6)}</div>'
        f'<div><h1>UOS Library AI</h1><div class="tag">{T["tagline"]}</div>'
        f'<div class="sup">{T["support"]}</div></div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="uos-welcome"><h1>{T["welcome"]}</h1><p>{T["welcome_sub"]}</p></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    for i, card in enumerate(CARDS):
        with cols[i]:
            st.markdown(
                f'<div class="uos-card {card[5]}">{_icon(card[0], 32, "#0B2345", 1.7)}'
                f"<h3>{card[1] if ru == 0 else card[2]}</h3>"
                f"<p>{card[3] if ru == 0 else card[4]}</p></div>",
                unsafe_allow_html=True,
            )
            if st.button("Open \u2192", key=f"card_{i}", use_container_width=True):
                _submit(card[6] if ru == 0 else card[7])
                st.rerun()
    st.markdown(f"**\u2726 {T['try']}**")
    chip_cols = st.columns(4)
    for i, chip in enumerate(CHIPS):
        with chip_cols[i]:
            label = chip[ru]
            if st.button(label, key=f"chip_{i}", use_container_width=True):
                _submit(label)
                st.rerun()


def main():
    st.set_page_config(page_title="UOS Library AI", page_icon="\U0001F4DA", layout="wide")

    # Make sure the demo database exists and has books - create it
    # automatically when needed (first run, missing file, empty database).
    try:
        if sum(count_by_subject().values()) == 0:
            init_db()
    except Exception:
        init_db()

    ensure_chat_state()
    # Stage 4: a password-reset / email-confirmation link returns
    # to the app with ?code=... - exchange it for a session and
    # flag the recovery so the account panel offers a new-password
    # form. Runs once; the code is removed from the URL afterwards.
    if _accounts_on() and not _sb_user():
        try:
            _code = st.query_params.get("code")
        except Exception:
            _code = None
        if _code:
            _client = store.new_client()
            _session = (store.exchange_code(_client, _code)
                        if _client is not None else None)
            if _session and _session.get("access_token"):
                _after_auth(_session, _client,
                            "Link verified. Set a new password "
                            "from the Student Account panel in "
                            "the sidebar.")
                st.session_state.sb_recovery = True
            try:
                del st.query_params["code"]
            except Exception:
                pass
    if "view" not in st.session_state:
        st.session_state.view = "home"
    if "ui_lang" not in st.session_state:
        st.session_state.ui_lang = "English"
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"

    # Theme marker + the whole redesign stylesheet.
    if st.session_state.theme == "Dark":
        st.markdown('<div class="uos-dark"></div>', unsafe_allow_html=True)
    st.markdown(_CSS, unsafe_allow_html=True)

    @st.dialog("About UOS Library AI")
    def _about():
        st.markdown(ABOUT_TEXT)

    @st.dialog("Help")
    def _help():
        st.markdown(HELP_TEXT)

    @st.dialog("Clear this chat?")
    def _clear():
        st.write(
            "This clears the messages of the current conversation only. "
            "Your other chats in this session are not touched."
        )
        if st.button("Yes, clear this chat", key="clear_confirm"):
            chat_id = st.session_state.current_chat_id
            chat = st.session_state.chats[chat_id]
            if _sb_user() and chat.get("db_id"):
                # Signed in: clearing removes the saved
                # conversation entirely (database + sidebar).
                _delete_chat(chat_id)
            else:
                chat["messages"] = [dict(GREETING)]
                chat["title"] = "New chat"
                st.session_state.messages = chat["messages"]
            st.session_state.view = "home"
            st.rerun()

    _sidebar()
    T = _t()

    # --- Top-right actions (About / Help / Clear Chat) ---
    _sp, c_about, c_help, c_clear = st.columns([5.2, 1, 1, 1.3])
    with c_about:
        if st.button(T["about"], key="top_about", use_container_width=True):
            _about()
    with c_help:
        if st.button(T["help"], key="top_help", use_container_width=True):
            _help()
    with c_clear:
        if st.button(T["clear"], key="top_clear", use_container_width=True):
            _clear()

    # --- Dashboard (home) or conversation ---
    messages = st.session_state.messages
    if st.session_state.view == "home":
        _dashboard()
    else:
        for msg in messages:
            with st.chat_message(msg["role"],
                                 avatar=_avatar_for(msg["role"])):
                st.markdown(msg["content"])

    # --- Chat input + queued prompts (cards, chips, categories) ---
    prompt = st.chat_input(T["placeholder"])
    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pop("pending_prompt")

    if prompt:
        set_chat_title_from_first_question(prompt)
        touch_current_chat()
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Conversation history (this chat only) lets the Groq layer
        # understand follow-ups; deterministic layers ignore it.
        reply = get_reply(prompt,
                          history=st.session_state.messages[:-1])
        st.session_state.messages.append({"role": "assistant", "content": reply})
        # Stage 4: save the exchange to the student's account
        # (no-op for guests - nothing is stored for them).
        _persist_exchange(prompt, reply)
        st.session_state.view = "chat"
        st.rerun()


if __name__ == "__main__":
    main()
