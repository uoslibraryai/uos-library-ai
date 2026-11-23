"""UOS Library AI - app.py
ChatGPT-style Library Assistant Chatbot (student demo project).

How it answers - in this order, always:
  1. Book search / availability  -> SQLite ONLY (database.py). Never invent.
     The 80 books are demonstration data, not verified UOS holdings.
  2. Official library questions -> verified facts in library_info.py only,
     each with its official source link.
  3. Real policy questions (limits, fines, membership, renewal conditions)
     -> honest "not published in the sources checked" + library contact.
     Demo sample rules are shown ONLY when the user explicitly asks about
     the demo project's sample rules, and always start with the DEMO ONLY
     label (decision D1).
  4. General chat -> Groq (free tier) IF a key is set, else rule-based fallback.
     Groq is never asked about book titles or availability.

Language: English + Roman Urdu. The reply tries to match the user's language.
Chat history: multiple separate chats in the sidebar (session-only -
kept while the browser session is active, not saved after it closes).
No student login system. All book data is demonstration data.
"""

import os
import uuid

import streamlit as st

from database import count_by_subject, init_db, search_books
from library_info import DEMO_LABEL, get_fact, policy_not_published

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


def format_books(books, roman_urdu=False):
    lines = []
    for b in books[:5]:
        if b["available_copies"] > 0:
            status = f"✅ Available: {b['available_copies']} of {b['total_copies']} copies"
        else:
            status = "❌ Not available right now (0 copies available)"
        lines.append(
            f"**{b['title']}** by {b['author']}\n"
            f"Subject: {b['subject']} | Shelf: {b['shelf_location']} | Year: {b['year']}\n"
            f"{status}"
        )
    extra = ""
    if len(books) > 5:
        extra = f"\n...and {len(books) - 5} more matching books in the demo data."
    intro = (
        "Ye kitabein demo catalogue (80 sample books — demonstration data, asal UOS holdings nahi) mein mili hain:"
        if roman_urdu
        else "I found these books in the demo catalogue (80 sample books — demonstration data, not verified UOS holdings):"
    )
    return intro + "\n\n" + "\n\n".join(lines) + extra


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

    # 2. Real policy questions that are NOT officially published (D1):
    # honest "not published" + library contact. No demo figures, ever.
    # Checked BEFORE the official routes: "How many books can I borrow?"
    # is a borrow-limit question, not a collections question.
    for keywords, _key, topic_en, topic_ur in POLICY_ROUTES:
        if any(k in low for k in keywords):
            return policy_not_published(topic_en, topic_ur, roman_urdu)

    # 3. Official verified information (library_info.py), with sources.
    for keywords, key in OFFICIAL_ROUTES:
        if any(k in low for k in keywords):
            return get_fact(key, roman_urdu)

    # 3b. Borrowing / returning process: the official circulation-desk
    # answer (limits themselves stay unpublished - see step 3).
    if any(k in low for k in ["borrow", "issue", "lena", "return", "wapas"]):
        return get_fact("circulation", roman_urdu)

    # 2. Book search - any question mentioning a book, author or subject.
    # Try the whole text first, then each word longest-first, so
    # "Mujhe Python ki kitab chahiye" finds Python (not "chahiye").
    words = sorted({w.strip("?.!,") for w in text.split()}, key=len, reverse=True)
    for query in [text] + words:
        if len(query) < 3 or query.lower() in SEARCH_STOPWORDS:
            continue
        books = search_books(query)
        if books:
            return format_books(books, roman_urdu)
    if any(w in low for w in ["book", "kitab", "kitaab", "author", "subject", "search", "find", "available", "availability"]):
        if roman_urdu:
            return "Maaf kijiye, ye kitab demo data mein nahi mili. Koi aur title, author ya subject try karein."
        return "Sorry, I could not find that book in the demo data. Please try another title, author or subject."

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
        "or answer about official library hours, services, Turnitin, e-books, the HEC Digital Library and contact details. "
        "Try e.g. 'Find Python books' or 'What time does the library open?'"
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


# ---------- Streamlit UI ----------
st.set_page_config(page_title="UOS Library AI", page_icon="📚", layout="wide")

# Make sure the demo database exists and has books - create it
# automatically when needed (first run, missing file, or empty database).
try:
    if sum(count_by_subject().values()) == 0:
        init_db()
except Exception:
    init_db()

ensure_chat_state()

st.title("📚 UOS Library AI")
st.caption("Your Smart Library Assistant  •  Demonstration data only")

with st.sidebar:
    st.header("UOS Library AI")
    st.write("Search the demo book catalogue, or ask about official library hours, services, Turnitin and contacts — in English or Roman Urdu.")
    if st.button("➕ New Chat", use_container_width=True):
        # The old chat stays saved in st.session_state.chats - it is
        # NOT deleted. A fresh chat simply becomes the current one.
        start_new_chat()
        st.rerun()
    st.divider()
    st.subheader("Previous chats")
    # Most recently ACTIVE chat first. Clicking a title reopens that chat.
    for chat_id, chat in sorted_chat_items():
        label = chat["title"]
        if chat_id == st.session_state.current_chat_id:
            label = f"▶ {label}"
        if st.button(label, key=f"open_{chat_id}", use_container_width=True):
            open_chat(chat_id)
            st.rerun()
    st.divider()
    st.subheader("Try these")
    for example in [
        "Find Python books",
        "Books by Tanenbaum",
        "What time does the library open?",
        "Library kis time khulti hai?",
        "Mujhe Python ki kitab chahiye",
        "How do I get a Turnitin check?",
        "Show me the online catalogue",
        "What is the fine for late return?",
    ]:
        if st.button(example, use_container_width=True):
            st.session_state.pending_prompt = example
    st.divider()
    st.subheader("Official links")
    st.markdown(
        "- [Wazir Agha Library](https://library.su.edu.pk/)\n"
        "- [PakCat catalogue — UOS](https://pakcat.pastic.gov.pk/library/45/university-of-sargodha)\n"
        "- [UOS E-Books](https://ebooks.su.edu.pk/)\n"
        "- [HEC Digital Library — UOS](https://www.digitallibrary.edu.pk/sargodhauni.html)"
    )
    st.divider()
    st.caption(
        "Student demo project: not officially endorsed by the University of "
        "Sargodha. Library information shown here comes from the university's "
        "public pages, with sources. The book catalogue is 80 demonstration "
        "books only and does not access real university library records. "
        "Book availability comes from SQLite only."
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask about a book, library hours, services, Turnitin...")
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    set_chat_title_from_first_question(prompt)
    touch_current_chat()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    reply = get_reply(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
