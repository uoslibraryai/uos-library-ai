"""UOS Library AI - app.py
ChatGPT-style Library Assistant Chatbot (student demo project).

How it answers - in this order, always:
  1. Book search / availability  -> SQLite ONLY (database.py). Never invent.
  2. Library FAQ (hours, membership, borrowing, returning, fines) -> built-in answers.
  3. General chat -> Groq (free tier) IF a key is set, else rule-based fallback.
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

# ---------- Library info (demo / sample - change for your real library) ----------
LIBRARY_HOURS = "Monday to Friday: 8:30 AM - 8:00 PM | Saturday: 9:00 AM - 5:00 PM | Sunday: Closed"
MEMBERSHIP_INFO = (
    "Students can get free library membership with a valid university student card. "
    "Bring your student card to the circulation desk to register."
)
BORROW_INFO = (
    "Students can borrow up to 3 books for 14 days. Bring the book and your student card "
    "to the circulation desk to borrow it."
)
RETURN_INFO = (
    "Return books at the circulation desk before the due date. "
    "You can renew a book once for 7 more days if no one else has reserved it."
)
FINE_INFO = (
    "Late return fine (demo rule): Rs. 10 per day, per book. "
    "Please confirm the current fine at the circulation desk."
)

# Only genuine Roman Urdu words - English words like "time"/"fine"/"member"
# must NOT trigger Urdu detection, or English questions get Urdu replies.
ROMAN_URDU_WORDS = [
    "kis", "kya", "kab", "kahan", "kaise", "mujhe", "chahiye", "kitab",
    "khulti", "band", "baje", "hai", "hain", "karo", "batao",
    "wapas", "lena", "dena", "kitaab",
]

FAQ = [
    # Fine first: "fine for late return" must not be answered as a return question.
    (["fine", "late", "jurmana"], "fine"),
    (["open", "khulti", "timing", "hours", "time"], "hours"),
    (["member", "membership", "register"], "membership"),
    (["borrow", "lena", "issue"], "borrow"),
    (["return", "wapas"], "return"),
]

FAQ_EN = {
    "hours": f"📚 Library hours: {LIBRARY_HOURS}",
    "membership": f"🪪 Membership: {MEMBERSHIP_INFO}",
    "borrow": f"📖 Borrowing: {BORROW_INFO}",
    "return": f"↩️ Returning: {RETURN_INFO}",
    "fine": f"💰 Fines: {FINE_INFO}",
}
FAQ_UR = {
    "hours": f"📚 Library ki timing: {LIBRARY_HOURS}",
    "membership": f"🪪 Membership: {MEMBERSHIP_INFO} Student card saath layein.",
    "borrow": f"📖 Kitab lena: {BORROW_INFO}",
    "return": f"↩️ Kitab wapas: {RETURN_INFO}",
    "fine": f"💰 Fine: {FINE_INFO}",
}


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
    intro = "Mujhe ye kitabein mili hain:" if roman_urdu else "I found these books in the demo library:"
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
                        "Do NOT invent book titles or book availability. "
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


def get_reply(user_text):
    """Main brain: SQLite first, FAQ second, Groq/fallback last."""
    text = user_text.strip()
    low = text.lower()
    roman_urdu = is_roman_urdu(text)

    # 1. FAQ - check before a general search, so "library kis time khulti hai" works.
    for keywords, key in FAQ:
        if any(k in low for k in keywords):
            return (FAQ_UR if roman_urdu else FAQ_EN)[key]

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

    # 3. Greetings / general chat
    if low in ("hi", "hello", "salam", "assalam o alaikum", "aoa"):
        if roman_urdu:
            return "Wa Alaikum Assalam! Main UOS Library AI hoon. Aap kitab search kar sakte hain, ya library timing, membership aur fine ke baare mein pooch sakte hain."
        return "Hello! I am UOS Library AI. You can search for a book, or ask about library hours, membership, borrowing and fines."

    ai_reply = ask_groq_or_fallback(text, roman_urdu)
    if ai_reply:
        return ai_reply

    if roman_urdu:
        return (
            "Main aapki madad kar sakta hoon: kitab search karein (title, author ya subject se), "
            "ya poochein - library timing, membership, borrowing, return ya fine."
        )
    return (
        "I can help you search for books (by title, author or subject), "
        "or answer about library hours, membership, borrowing, returning and fines. "
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
    "content": "Hello! 👋 I am **UOS Library AI**. Ask me to find a book, check if it is available, or tell you the library hours. Try: *Find Python books*",
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
    st.write("Ask about books, hours, membership, borrowing, returns and fines — in English or Roman Urdu.")
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
        "What is the fine for late return?",
    ]:
        if st.button(example, use_container_width=True):
            st.session_state.pending_prompt = example
    st.divider()
    st.caption(
        "Demo project: not officially endorsed by the University of Sargodha "
        "and does not access real university library records. "
        "All book data is sample data. Book availability comes from SQLite only."
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask about a book, library hours, membership, fines...")
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
