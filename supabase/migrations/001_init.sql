-- Enable required extensions
create extension if not exists "uuid-ossp";
create extension if not exists vector;

-- Use auth.users from Supabase Auth and map app profile data by user_id.
create table if not exists public.user_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null,
  learning_level text not null check (learning_level in (
    'Elementary', 'Middle School', 'High School', 'Undergraduate', 'Graduate', 'Professional'
  )),
  preferred_explanation_style text not null default 'Step-by-Step',
  preferred_learning_mode text not null default 'Knowledge Vault' check (preferred_learning_mode in ('Knowledge Vault', 'Global Scholar')),
  subjects text[] not null default '{}',
  xp_points integer not null default 0,
  learning_streak integer not null default 0,
  daily_goal integer not null default 3,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.learning_preferences (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references auth.users(id) on delete cascade,
  explanation_style text not null,
  learning_mode text not null check (learning_mode in ('Knowledge Vault', 'Global Scholar')),
  subjects text[] not null default '{}',
  learning_level text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists idx_learning_preferences_user_active
on public.learning_preferences(user_id)
where is_active = true;

create table if not exists public.conversations (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  subject text not null,
  learning_level text not null,
  explanation_style text not null,
  learning_mode text not null check (learning_mode in ('Knowledge Vault', 'Global Scholar')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_conversations_user_created
on public.conversations(user_id, created_at desc);

create table if not exists public.messages (
  id uuid primary key default uuid_generate_v4(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('system', 'user', 'assistant')),
  content text not null,
  context_chunks jsonb not null default '[]'::jsonb,
  token_count integer,
  created_at timestamptz not null default now()
);

create index if not exists idx_messages_conversation_created
on public.messages(conversation_id, created_at asc);

create table if not exists public.uploaded_documents (
  document_id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references auth.users(id) on delete cascade,
  filename text not null,
  file_path text not null,
  file_type text not null,
  file_size bigint not null,
  embedding_status text not null default 'pending' check (embedding_status in ('pending', 'processing', 'completed', 'failed')),
  indexing_status text not null default 'pending' check (indexing_status in ('pending', 'processing', 'completed', 'failed')),
  processing_status text not null default 'uploaded' check (processing_status in ('uploaded', 'chunking', 'vectorizing', 'indexed', 'failed')),
  upload_date timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_uploaded_documents_user_upload
on public.uploaded_documents(user_id, upload_date desc);

create table if not exists public.document_chunks (
  id uuid primary key default uuid_generate_v4(),
  document_id uuid not null references public.uploaded_documents(document_id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  chunk_index integer not null,
  chunk_text text not null,
  embedding vector(1536),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique(document_id, chunk_index)
);

create index if not exists idx_document_chunks_user_id on public.document_chunks(user_id);
create index if not exists idx_document_chunks_document_id on public.document_chunks(document_id);

-- ivfflat index for cosine similarity search; list count should be tuned by scale.
create index if not exists idx_document_chunks_embedding
on public.document_chunks using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

create table if not exists public.learning_analytics (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references auth.users(id) on delete cascade,
  date_key date not null,
  questions_asked integer not null default 0,
  documents_uploaded integer not null default 0,
  vault_usage_count integer not null default 0,
  global_usage_count integer not null default 0,
  topics_covered text[] not null default '{}',
  xp_earned integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, date_key)
);

create table if not exists public.achievements (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references auth.users(id) on delete cascade,
  code text not null,
  title text not null,
  description text not null,
  earned_at timestamptz not null default now(),
  unique(user_id, code)
);

create table if not exists public.weekly_summaries (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references auth.users(id) on delete cascade,
  week_start date not null,
  week_end date not null,
  summary_markdown text not null,
  created_at timestamptz not null default now(),
  unique(user_id, week_start, week_end)
);

-- Trigger helper for updated_at
create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger trg_user_profiles_updated
before update on public.user_profiles
for each row execute function public.touch_updated_at();

create trigger trg_learning_preferences_updated
before update on public.learning_preferences
for each row execute function public.touch_updated_at();

create trigger trg_conversations_updated
before update on public.conversations
for each row execute function public.touch_updated_at();

create trigger trg_uploaded_documents_updated
before update on public.uploaded_documents
for each row execute function public.touch_updated_at();

create trigger trg_learning_analytics_updated
before update on public.learning_analytics
for each row execute function public.touch_updated_at();

-- RPC for vector search with user scoping
create or replace function public.match_document_chunks(
  p_user_id uuid,
  p_query_embedding vector(1536),
  p_match_count int default 8
)
returns table (
  id uuid,
  document_id uuid,
  chunk_index int,
  chunk_text text,
  similarity float
)
language sql
stable
as $$
  select
    dc.id,
    dc.document_id,
    dc.chunk_index,
    dc.chunk_text,
    1 - (dc.embedding <=> p_query_embedding) as similarity
  from public.document_chunks dc
  where dc.user_id = p_user_id
  order by dc.embedding <=> p_query_embedding
  limit p_match_count;
$$;

-- RLS
alter table public.user_profiles enable row level security;
alter table public.learning_preferences enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;
alter table public.uploaded_documents enable row level security;
alter table public.document_chunks enable row level security;
alter table public.learning_analytics enable row level security;
alter table public.achievements enable row level security;
alter table public.weekly_summaries enable row level security;

create policy "user_profiles_owner_policy" on public.user_profiles
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "learning_preferences_owner_policy" on public.learning_preferences
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "conversations_owner_policy" on public.conversations
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "messages_owner_policy" on public.messages
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "uploaded_documents_owner_policy" on public.uploaded_documents
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "document_chunks_owner_policy" on public.document_chunks
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "learning_analytics_owner_policy" on public.learning_analytics
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "achievements_owner_policy" on public.achievements
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "weekly_summaries_owner_policy" on public.weekly_summaries
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);


