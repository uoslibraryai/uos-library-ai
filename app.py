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
Chat history: multiple separate chats in the sidebar (session-only -
kept while the browser session is active, not saved after it closes).
No student login system. All book data is demonstration data.
"""

import difflib
import os
import re
import uuid

import streamlit as st

from database import count_by_subject, init_db, search_books
from library_faq import faq_answer
from library_info import DEMO_LABEL, get_fact, policy_not_published
from library_academic_faq import academic_faq_answer
from library_digital_faq import digital_faq_answer
from library_services_faq import service_faq_answer

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
    (["e-book", "ebook", "ebooks"], "ebooks"),
    (["hec", "digital library", "online journal"], "hec"),
    (["how many books", "collection", "total books", "printed books",
      "books are in the library", "library collection"], "collections"),
    (["contact", "phone", "email", "address", "helpline", "rabta"], "contact"),
    (["seminar librar"], "seminar_libraries"),
    (["history", "archive", "government college"], "history"),
    (["facilit", "learning zone", "faculty lounge", "research commons",
      "digital commons", "reference hall", "discussion room", "seating",
      "study space"], "facilities"),
    (["wifi", "wi-fi", "internet"], "wifi"),
    (["photocopy", "printing"], "photocopy"),
    (["renew", "reserve", "reservation"], "renewal"),
    (["service", "reference", "orientation", "information literacy",
      "endnote", "mendeley", "spss", "literature search", "research support",
      "research help", "document delivery", "inter-library", "inter library",
      "book searching"], "services"),
    (["open", "khulti", "timing", "hours", "schedule", "kis time"], "hours"),
]

# Real policy questions whose official answers are NOT published (D1).
POLICY_ROUTES = [
    (["fine", "jurmana", "late fee", "penalty"], "fine",
     "borrowing fines and late-return charges", "fine aur late-return charges ki policy"),
    (["member", "library card"], "membership",
     "membership and library-card policy", "membership aur library-card ki policy"),
    (["how many books can", "borrow limit", "borrowing limit", "loan period",
      "how long can i keep", "kitni kitabein le"], "borrow",
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
            "Ye kitabein demo catalogue (80 sample books — demonstration data, asal UOS holdings nahi) mein mili hain:"
            if roman_urdu
            else "I found these books in the demo catalogue (80 sample books — demonstration data, not verified UOS holdings):"
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


def ask_groq_or_fallback(user_text, roman_urdu):
    """General chat only. Returns None if no Groq key - caller uses fallback."""
    api_key = None
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None
    api_key = api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        reply = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are UOS Library AI, a helpful library assistant. "
                        "Do NOT invent book titles, book availability, or library policies, fines or fees. "
                        "For any book search or availability question, say the user "
                        "should search the library database. Answer in the user's language."
                    ),
                },
                {"role": "user", "content": user_text},
            ],
            max_tokens=300,
        )
        return reply.choices[0].message.content
    except Exception:
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
    "hai", "hain", "ki", "ka", "ko",
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


def get_reply(user_text):
    """Main brain, in order: explicit demo-policy request, official facts,
    unpublished-policy honesty, SQLite book search, Groq/fallback."""
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

    # 3. Real policy questions that are NOT officially published (D1):
    # honest "not published" + library contact. No demo figures, ever.
    # Checked BEFORE the official routes: "How many books can I borrow?"
    # is a borrow-limit question, not a collections question.
    for keywords, _key, topic_en, topic_ur in POLICY_ROUTES:
        if any(k in low for k in keywords):
            return policy_not_published(topic_en, topic_ur, roman_urdu)

    # 4. Official verified information (library_info.py), with sources.
    for keywords, key in OFFICIAL_ROUTES:
        if any(k in low for k in keywords):
            return get_fact(key, roman_urdu)

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
                    f"Here are all {len(books)} **{subject}** books in the demo catalogue (demonstration data):"
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

    # 5e. General search: whole text first, then each word
    # longest-first, so "Mujhe Python ki kitab chahiye" finds Python
    # (not "chahiye"). Results are ranked (exact title > title >
    # author > subject) and ALL matches are shown.
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

    # 5f. Not found: honest message + spelling/subject suggestions.
    if any(w in low for w in ["book", "kitab", "kitaab", "author", "subject", "search", "find", "available", "availability"]) \
            or any(topic in low for topic in TOPIC_TO_SUBJECT):
        return _not_found_reply(text, low, roman_urdu)

    # 4. Greetings / general chat
    if low in ("hi", "hello", "salam", "assalam o alaikum", "aoa"):
        if roman_urdu:
            return "Wa Alaikum Assalam! Main UOS Library AI hoon. Aap demo catalogue mein kitab search kar sakte hain, ya official library timing, services, Turnitin aur contact ke baare mein pooch sakte hain."
        return "Hello! I am UOS Library AI. You can search the demo book catalogue, or ask about official library hours, services, Turnitin and contact details."

    ai_reply = ask_groq_or_fallback(text, roman_urdu)
    if ai_reply:
        return ai_reply

    if roman_urdu:
        return (
            "Main aapki madad kar sakta hoon: demo catalogue mein kitab search karein (title, author ya subject se), "
            "ya poochein - library timing, services, Turnitin, e-books, HEC Digital Library ya contact."
        )
    return (
        "I can help you search the demo book catalogue (by title, author or subject), "
        "answer about official library hours, services, Turnitin, e-books, the HEC Digital Library and contact details, "
        "or answer from 740 built-in FAQs (100 Rules & Regulations, 60 Facilities & Services, "
        "80 Academic & Research Assistance, 500 Digital Library & Online Resources). "
        "Try e.g. 'Find Python books', 'What time does the library open?' or 'Can I bring a bag?'"
    )


# ---------- Multiple-chat history (session-only) ----------
# Chats live in st.session_state only, like ChatGPT without an account.
# They are kept separately for the whole active browser session, but
# are NOT saved to disk/database, so they are gone when the tab closes.
# That is deliberate for this no-login demo: a shared database would
# show one visitor's chats to every other visitor.
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
        "categories": "Library Categories", "quick": "Quick Access",
        "language": "Language", "theme": "Theme", "light": "Light", "dark": "Dark",
        "about": "About", "help": "Help", "clear": "Clear Chat",
        "placeholder": "Ask anything about your library...",
        "subjects": "Demo catalogue subjects",
        "links": "Official links",
    },
    "Roman Urdu": {
        "tagline": "Your Smart Library Assistant",
        "support": "Search books \u2022 Explore resources \u2022 Get research assistance",
        "welcome": "Main aaj aap ki kya madad kar sakta hun?",
        "welcome_sub": "UOS Library, is ki services, resources ya research support ke bare mein kuch bhi poochein.",
        "try": "Yeh pooch kar dekhein:",
        "home": "Home", "new_chat": "New Chat", "history": "Chat History",
        "categories": "Library Categories", "quick": "Quick Access",
        "language": "Language", "theme": "Theme", "light": "Light", "dark": "Dark",
        "about": "About", "help": "Help", "clear": "Clear Chat",
        "placeholder": "Apni library ke bare mein kuch bhi poochein...",
        "subjects": "Demo catalogue subjects",
        "links": "Official links",
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
    "- The chatbot answers **740 built-in FAQs** (100 Rules & Regulations, "
    "60 Facilities & Services, 80 Academic & Research Assistance, 500 Digital "
    "Library & Online Resources) plus demo book search, in English and "
    "Roman Urdu.\n"
    "- Chats are kept only in this browser session — there is no login and "
    "nothing is saved permanently."
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
    "previous chats stay available in the sidebar during this session."
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
</style>
"""


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
            f'<div style="font-size:.82rem;color:#B9CBE4">University of Sargodha<br/>Library Assistant</div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )
        st.write("")
        # --- Main navigation ---
        if st.button(T["home"], key="nav_home", use_container_width=True):
            st.session_state.view = "home"
            st.rerun()
        if st.button(T["new_chat"], key="nav_new", use_container_width=True):
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
        with st.expander(T["categories"]):
            for label, prompt_text in CATEGORIES:
                if st.button(label, key=f"cat_{label[:18]}", use_container_width=True):
                    _submit(prompt_text)
                    st.rerun()
        st.divider()
        # --- Quick Access ---
        st.markdown(f"**{T['quick']}**")
        for i, card in enumerate(CARDS):
            title = card[1] if ru == 0 else card[2]
            if st.button(title, key=f"quick_{i}", use_container_width=True):
                _submit(card[6] if ru == 0 else card[7])
                st.rerun()
        st.divider()
        # --- Language & theme selectors (session-persistent) ---
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
            chat = st.session_state.chats[st.session_state.current_chat_id]
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
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # --- Chat input + queued prompts (cards, chips, categories) ---
    prompt = st.chat_input(T["placeholder"])
    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pop("pending_prompt")

    if prompt:
        set_chat_title_from_first_question(prompt)
        touch_current_chat()
        st.session_state.messages.append({"role": "user", "content": prompt})
        reply = get_reply(prompt)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.view = "chat"
        st.rerun()


if __name__ == "__main__":
    main()
