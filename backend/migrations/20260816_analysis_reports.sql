-- Run in the Supabase SQL editor after reviewing existing table ownership.
-- Extends the existing frontend analysis_reports table; it does not create a duplicate report table.
alter table public.analysis_reports add column if not exists analysis_id uuid;
alter table public.analysis_reports add column if not exists video_id uuid;
alter table public.analysis_reports add column if not exists sport text;
alter table public.analysis_reports add column if not exists activity text;
alter table public.analysis_reports add column if not exists status text default 'analyzed';
alter table public.analysis_reports add column if not exists pose_detection_rate numeric;
alter table public.analysis_reports add column if not exists analysis_confidence integer;
alter table public.analysis_reports add column if not exists analysis_quality integer;
alter table public.analysis_reports add column if not exists quality_level text;
alter table public.analysis_reports add column if not exists quality_warnings jsonb default '[]'::jsonb;
alter table public.analysis_reports add column if not exists key_metrics jsonb default '{}'::jsonb;
alter table public.analysis_reports add column if not exists recommendations jsonb default '[]'::jsonb;
create unique index if not exists analysis_reports_analysis_id_key on public.analysis_reports (analysis_id) where analysis_id is not null;
create index if not exists analysis_reports_user_created_at_idx on public.analysis_reports (user_id, created_at desc);
-- Enable RLS and ensure authenticated users can only access their own reports.
alter table public.analysis_reports enable row level security;
drop policy if exists "Users manage their own analysis reports" on public.analysis_reports;
create policy "Users manage their own analysis reports" on public.analysis_reports
  for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
