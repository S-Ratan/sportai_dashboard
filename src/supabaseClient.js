import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// In development Vite can move to another available port.  Use the browser's
// actual origin unless an explicit, allow-listed Supabase redirect URL is set.
// Production must configure VITE_SITE_URL (or Supabase's Site URL) explicitly.
const configuredSiteUrl = import.meta.env.VITE_SITE_URL?.replace(/\/$/, '');
export const authRedirectUrl = configuredSiteUrl || (import.meta.env.DEV ? window.location.origin : undefined);

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
