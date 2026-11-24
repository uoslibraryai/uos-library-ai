-- ============================================================
-- UOS Library AI - Stage 4: student accounts & chat history
-- Run this ONCE in your Supabase project: SQL Editor -> New
-- query -> paste this file -> Run. Safe to re-run (idempotent).
--
-- Design:
-- * Supabase Auth (auth.users) owns identities and passwords.
--   Passwords are hashed by Supabase Auth; this app never sees
--   or stores a plaintext password and has NO table for them.
-- * public.profiles mirrors the auth user id 1:1 (minimal data:
--   id + email only - no unnecessary personal information).
-- * public.conversations / public.messages belong to a student
--   through user_id = auth.users.id.
-- * Row Level Security is ENABLED on every table and every
--   policy is scoped to auth.uid(), so a signed-in student can
--   only ever read, create, change or delete their OWN rows -
--   even if they guess or modify a conversation id, the
--   database itself returns nothing.
-- * The app connects ONLY with the public anon key + the
--   student's own session token. The service-role key is never
--   used by the app and must never be put in app code/secrets
--   for the frontend.
-- ============================================================

-- ---------- profiles ----------
create table if not exists public.profiles (
    id         uuid primary key references auth.users (id) on delete cascade,
    email      text not null,
    created_at timestamptz not null default now()
);

-- ---------- conversations ----------
create table if not exists public.conversations (
    id         uuid primary key default gen_random_uuid(),
    user_id    uuid not null references public.profiles (id) on delete cascade,
    title      text not null default 'New chat',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists conversations_user_updated_idx
    on public.conversations (user_id, updated_at desc);

-- ---------- messages ----------
create table if not exists public.messages (
    id              uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references public.conversations (id) on delete cascade,
    user_id         uuid not null references public.profiles (id) on delete cascade,
    role            text not null check (role in ('user', 'assistant')),
    content         text not null,
    created_at      timestamptz not null default now()
);
create index if not exists messages_conversation_created_idx
    on public.messages (conversation_id, created_at);
create index if not exists messages_user_idx
    on public.messages (user_id);

-- ---------- auto-create a profile row on sign-up ----------
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (id, email)
    values (new.id, new.email)
    on conflict (id) do nothing;
    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();

-- ---------- Row Level Security ----------
alter table public.profiles      enable row level security;
alter table public.conversations enable row level security;
alter table public.messages      enable row level security;

-- profiles: a student sees and edits only their own profile row.
drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own" on public.profiles
    for select using (id = auth.uid());
drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own" on public.profiles
    for insert with check (id = auth.uid());
drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own" on public.profiles
    for update using (id = auth.uid()) with check (id = auth.uid());

-- conversations: full access to own rows only (select, insert,
-- update, delete are each checked against auth.uid()).
drop policy if exists "conversations_select_own" on public.conversations;
create policy "conversations_select_own" on public.conversations
    for select using (user_id = auth.uid());
drop policy if exists "conversations_insert_own" on public.conversations;
create policy "conversations_insert_own" on public.conversations
    for insert with check (user_id = auth.uid());
drop policy if exists "conversations_update_own" on public.conversations;
create policy "conversations_update_own" on public.conversations
    for update using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists "conversations_delete_own" on public.conversations;
create policy "conversations_delete_own" on public.conversations
    for delete using (user_id = auth.uid());

-- messages: full access to own rows only. user_id is stored on
-- every message (not just via the conversation) so the policy
-- needs no join and a forged conversation id gains nothing.
drop policy if exists "messages_select_own" on public.messages;
create policy "messages_select_own" on public.messages
    for select using (user_id = auth.uid());
drop policy if exists "messages_insert_own" on public.messages;
create policy "messages_insert_own" on public.messages
    for insert with check (user_id = auth.uid());
drop policy if exists "messages_update_own" on public.messages;
create policy "messages_update_own" on public.messages
    for update using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists "messages_delete_own" on public.messages;
create policy "messages_delete_own" on public.messages
    for delete using (user_id = auth.uid());
