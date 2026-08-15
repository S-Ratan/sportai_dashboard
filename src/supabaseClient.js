import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://eynnhvxzbsexpqezyihl.supabase.co';

const supabaseAnonKey = 'sb_publishable_dmylTk12N6f-9VC1Qu_4yA_8svbBiIj'; 

export const supabase = createClient(supabaseUrl, supabaseAnonKey);