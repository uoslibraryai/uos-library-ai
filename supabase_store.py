"""Stage 4 data layer: student accounts + permanent chat history
on Supabase (free tier), used by app.py.

Security model:
- The app connects with the PUBLIC anon key plus the signed-in
  student's own session token. Row Level Security in the database
  (see supabase_schema.sql) is what actually protects the data:
  every policy is scoped to auth.uid(), so a student can only
  ever reach their own rows, even with a guessed conversation id.
- The service-role key is NEVER used by this app - it would
  bypass RLS. It must not be added to the app's secrets.
- Passwords are handled only by Supabase Auth (hashed by
  Supabase); this module passes them to the auth API over HTTPS
  and never stores or logs them.
- Every query ALSO filters by user_id in the app (defence in
  depth on top of RLS).
- When Supabase is not configured, accounts_enabled() is False
  and the app runs in guest mode exactly as before. Every
  function fails safe (returns None / [] / False) so a database
  outage can never break the chatbot itself.
"""

import os
from datetime import datetime, timezone

try:
    import streamlit as st
except Exception:  # pragma: no cover - streamlit always present in app
    st = None


def _secret(name):
    """Read a value from Streamlit secrets, falling back to the
    environment. Never hardcoded anywhere."""
    try:
        if st is not None:
            value = st.secrets.get(name)
            if value:
                return value
    except Exception:
        pass
    return os.environ.get(name)


def supabase_config():
    """(url, anon_key) or (None, None) when not configured."""
    return _secret("SUPABASE_URL"), _secret("SUPABASE_ANON_KEY")


def accounts_enabled():
    url, key = supabase_config()
    return bool(url and key)


def new_client():
    """A fresh Supabase client using the anon key, or None."""
    url, key = supabase_config()
    if not url or not key:
        return None
    try:
        from supabase import create_client

        return create_client(url, key)
    except Exception:
        return None


def restore_client(access_token, refresh_token):
    """Rebuild a signed-in client from the session tokens kept in
    Streamlit session state (per browser session only)."""
    client = new_client()
    if client is None or not access_token or not refresh_token:
        return None
    try:
        client.auth.set_session(access_token, refresh_token)
        return client
    except Exception:
        return None


def _session_dict(response):
    """Normalize an auth response into plain data (or None)."""
    try:
        user = getattr(response, "user", None)
        session = getattr(response, "session", None)
        if user is None:
            return None
        return {
            "user_id": str(user.id),
            "email": user.email,
            "access_token": getattr(session, "access_token", None),
            "refresh_token": getattr(session, "refresh_token", None),
            "needs_confirmation": session is None,
        }
    except Exception:
        return None


def sign_up(client, email, password):
    """Register a new student. Returns the session dict; when the
    project requires email confirmation, the dict has
    needs_confirmation=True and no tokens yet."""
    try:
        return _session_dict(
            client.auth.sign_up({"email": email, "password": password}))
    except Exception:
        return None


def sign_in(client, email, password):
    """Log in. Returns the session dict or None on bad credentials
    or any error."""
    try:
        return _session_dict(client.auth.sign_in_with_password(
            {"email": email, "password": password}))
    except Exception:
        return None


def sign_out(client):
    try:
        client.auth.sign_out()
        return True
    except Exception:
        return False


def send_password_reset(client, email, redirect_to=None):
    """Ask Supabase Auth to email a password-reset link."""
    try:
        options = {"redirect_to": redirect_to} if redirect_to else {}
        client.auth.reset_password_for_email(email, options)
        return True
    except Exception:
        return False


def exchange_code(client, code):
    """Exchange a recovery/confirmation code from the redirect URL
    for a session (used by the password-reset return flow)."""
    try:
        return _session_dict(client.auth.exchange_code_for_session(
            {"auth_code": code}))
    except Exception:
        return None


def update_password(client, new_password):
    """Set a new password for the currently signed-in session
    (e.g. after a recovery code exchange)."""
    try:
        client.auth.update_user({"password": new_password})
        return True
    except Exception:
        return False


def _now():
    return datetime.now(timezone.utc).isoformat()


def ensure_profile(client, user_id, email):
    """Create the student's profile row if missing (the database
    trigger normally does this; the upsert is a safe fallback and
    is restricted by RLS to the student's own id)."""
    try:
        client.table("profiles").upsert(
            {"id": user_id, "email": email}).execute()
        return True
    except Exception:
        return False


def list_conversations(client, user_id):
    """The student's conversations, most recently active first."""
    try:
        res = (client.table("conversations")
               .select("id,title,updated_at")
               .eq("user_id", user_id)
               .order("updated_at", desc=True)
               .execute())
        return res.data or []
    except Exception:
        return []


def get_messages(client, user_id, conversation_id):
    """Messages of one of the student's conversations, oldest
    first. RLS + the explicit user_id filter both apply, so a
    foreign conversation id returns nothing."""
    try:
        res = (client.table("messages")
               .select("role,content")
               .eq("user_id", user_id)
               .eq("conversation_id", conversation_id)
               .order("created_at")
               .execute())
        return res.data or []
    except Exception:
        return []


def create_conversation(client, user_id, title):
    """Create a conversation row; returns its id or None."""
    try:
        res = (client.table("conversations")
               .insert({"user_id": user_id, "title": title,
                        "updated_at": _now()})
               .execute())
        if res.data:
            return res.data[0]["id"]
    except Exception:
        pass
    return None


def append_message(client, user_id, conversation_id, role, content):
    try:
        (client.table("messages")
         .insert({"user_id": user_id,
                  "conversation_id": conversation_id,
                  "role": role, "content": content})
         .execute())
        return True
    except Exception:
        return False


def update_conversation(client, user_id, conversation_id, title=None):
    """Bump updated_at (and the title when given) on an own
    conversation."""
    try:
        fields = {"updated_at": _now()}
        if title:
            fields["title"] = title
        (client.table("conversations")
         .update(fields)
         .eq("user_id", user_id)
         .eq("id", conversation_id)
         .execute())
        return True
    except Exception:
        return False


def delete_conversation(client, user_id, conversation_id):
    """Delete an own conversation; its messages are removed by
    the database cascade. A foreign id deletes nothing."""
    try:
        (client.table("conversations")
         .delete()
         .eq("user_id", user_id)
         .eq("id", conversation_id)
         .execute())
        return True
    except Exception:
        return False
