-- Password reset support table
-- Stores hashed tokens with expiry and used flag

create table if not exists public.password_resets (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  token_hash text not null,
  expires_at timestamptz not null,
  used boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists idx_password_resets_email on public.password_resets (email);
create index if not exists idx_password_resets_expires_at on public.password_resets (expires_at);

alter table public.password_resets enable row level security;

-- Only service role should operate on this table in backend; for safety, block public access
-- Optionally, deny all by default (no policies). Backend uses service role key.
