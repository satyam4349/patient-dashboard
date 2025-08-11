-- Add sleep tracking and clinician-patient connections
-- Run this in Supabase SQL Editor or via Supabase CLI.

-- Add sleep hours to moods table (we'll store it in the encrypted data)
-- No schema change needed for moods table as sleep will be part of encrypted payload

-- Create clinician-patient connections table
create table if not exists public.clinician_connections (
  id uuid primary key default gen_random_uuid(),
  clinician_id uuid not null,
  patient_id uuid not null,
  status text not null default 'pending' check (status in ('pending', 'accepted', 'rejected', 'blocked')),
  requested_at timestamptz not null default now(),
  responded_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  
  -- Ensure unique connection per clinician-patient pair
  unique(clinician_id, patient_id)
);

-- Create privacy settings table
create table if not exists public.privacy_settings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique,
  share_raw_text boolean not null default false,
  share_summaries_only boolean not null default true,
  allow_clinician_access boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Create user connection codes table for easy clinician discovery
create table if not exists public.user_connection_codes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique,
  connection_code text not null unique,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Indexes for efficient queries
create index if not exists idx_clinician_connections_clinician_id on public.clinician_connections (clinician_id, status);
create index if not exists idx_clinician_connections_patient_id on public.clinician_connections (patient_id, status);
create index if not exists idx_privacy_settings_user_id on public.privacy_settings (user_id);
create index if not exists idx_user_connection_codes_code on public.user_connection_codes (connection_code);
create index if not exists idx_user_connection_codes_user_id on public.user_connection_codes (user_id);

-- Enable RLS
alter table public.clinician_connections enable row level security;
alter table public.privacy_settings enable row level security;
alter table public.user_connection_codes enable row level security;

-- RLS Policies for clinician_connections
create policy "Users can view their own connections" on public.clinician_connections
  for select using (
    auth.uid() = clinician_id or auth.uid() = patient_id
  );

create policy "Clinicians can create connection requests" on public.clinician_connections
  for insert with check (
    auth.uid() = clinician_id and 
    exists (select 1 from auth.users where id = auth.uid() and raw_user_meta_data->>'role' = 'clinician')
  );

create policy "Users can update their own connections" on public.clinician_connections
  for update using (
    auth.uid() = clinician_id or auth.uid() = patient_id
  );

-- RLS Policies for privacy_settings
create policy "Users can manage their own privacy settings" on public.privacy_settings
  for all using (auth.uid() = user_id);

-- RLS Policies for user_connection_codes
create policy "Users can manage their own connection codes" on public.user_connection_codes
  for all using (auth.uid() = user_id);

-- Function to generate unique connection codes
create or replace function generate_connection_code()
returns text as $$
declare
  code text;
  exists_check boolean;
begin
  loop
    -- Generate a 8-character alphanumeric code
    code := upper(substring(md5(random()::text) from 1 for 8));
    
    -- Check if code already exists
    select exists(select 1 from public.user_connection_codes where connection_code = code) into exists_check;
    
    -- If code doesn't exist, return it
    if not exists_check then
      return code;
    end if;
  end loop;
end;
$$ language plpgsql;

-- Function to automatically create connection code for new users
create or replace function create_user_connection_code()
returns trigger as $$
begin
  insert into public.user_connection_codes (user_id, connection_code)
  values (new.id, generate_connection_code());
  
  insert into public.privacy_settings (user_id)
  values (new.id);
  
  return new;
end;
$$ language plpgsql;

-- Trigger to create connection code for new users
create trigger on_user_created
  after insert on auth.users
  for each row execute function create_user_connection_code();