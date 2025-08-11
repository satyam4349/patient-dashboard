-- Create patient data tables: moods and journals
-- Run this in Supabase SQL Editor or via Supabase CLI.

create table if not exists public.moods (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  ciphertext text not null,
  nonce text not null,
  version text not null default 'v1',
  created_at timestamptz not null default now()
);

create table if not exists public.journals (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  ciphertext text not null,
  nonce text not null,
  version text not null default 'v1',
  created_at timestamptz not null default now()
);

-- Indexes for efficient history queries
create index if not exists idx_moods_user_created_at on public.moods (user_id, created_at desc);
create index if not exists idx_journals_user_created_at on public.journals (user_id, created_at desc);

-- Ownership and grants (Supabase usually manages these)
alter table public.moods enable row level security;
alter table public.journals enable row level security;
