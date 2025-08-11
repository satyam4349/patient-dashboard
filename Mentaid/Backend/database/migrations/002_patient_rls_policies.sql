-- Row Level Security (RLS) policies for patient data tables
-- Run after creating tables.

-- Ensure RLS is enabled
alter table if exists public.moods enable row level security;
alter table if exists public.journals enable row level security;

-- Drop existing policies if re-running (idempotent)
drop policy if exists moods_select_own on public.moods;
drop policy if exists moods_insert_own on public.moods;
drop policy if exists journals_select_own on public.journals;
drop policy if exists journals_insert_own on public.journals;

-- Users can select their own records
create policy moods_select_own on public.moods
for select using (auth.uid() = user_id);

create policy journals_select_own on public.journals
for select using (auth.uid() = user_id);

-- Users can insert records only for themselves
create policy moods_insert_own on public.moods
for insert with check (auth.uid() = user_id);

create policy journals_insert_own on public.journals
for insert with check (auth.uid() = user_id);

-- (Optional) Prevent updates/deletes by default by not creating policies for them.
-- If needed later, create update/delete policies with similar ownership checks.
