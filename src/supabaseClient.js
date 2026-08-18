import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

const configuredSiteUrl = import.meta.env.VITE_SITE_URL?.replace(/\/$/, '');
export const authRedirectUrl = configuredSiteUrl || (typeof window !== 'undefined' && import.meta.env.DEV ? window.location.origin : undefined);

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY in environment variables.');
}

// Fall back to dummy values during build/missing envs to prevent app crash
export const supabase = createClient(
  supabaseUrl || 'https://placeholder.supabase.co',
  supabaseAnonKey || 'placeholder'
);