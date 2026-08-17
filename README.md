# SportAI Dashboard

Frontend dashboard prototype for the SIH PS-02 AI-based Sports Performance Analysis and Injury Prevention System.

## Run

```bash
npm install
npm run dev
```

The dashboard reads completed analysis reports from Supabase and sends video analysis to the FastAPI backend.

This system provides biomechanical analysis and injury-risk screening indicators. It is not a medical diagnosis and should not replace professional medical or sports-science assessment.

## Run

1. Copy `.env.example` to `.env`, supply the Supabase URL and anonymous key, and keep `VITE_API_URL=http://127.0.0.1:8001` for local development.
2. Run `backend/migrations/20260816_analysis_reports.sql` in the Supabase SQL editor after reviewing the existing `analysis_reports` table.
3. Start the backend with `cd backend; .venv\Scripts\python -m uvicorn app.main:app --reload --port 8001`.
4. Start the dashboard with `npm run dev`.

## API

- `POST /api/analyze` accepts MP4/AVI/MOV/MKV video uploads and returns pose data, biomechanics, rule-based performance/risk screening, recommendations, and technical analysis quality.

## Local Supabase Authentication

Use a dedicated Supabase development project for local testing when possible. Copy
`.env.example` to `.env` and provide only the public project URL and anonymous
key:

```dotenv
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_SITE_URL=http://localhost:5173
```

`VITE_SITE_URL` is passed as the email confirmation redirect. In the Supabase
Dashboard for the development project, add the active Vite address to **Auth →
URL Configuration → Redirect URLs**. Add `http://localhost:5173/**` (and any
fallback port such as `http://localhost:5174/**` that you use), or set
`VITE_SITE_URL` to that active address before starting Vite. Configure the
development project's Site URL consistently as well.

Email confirmation remains enabled. New development accounts must confirm the
email sent by Supabase before they can sign in. If the login screen reports that
the email is not confirmed, use **Resend confirmation email** and then open the
new confirmation link. The application does not create a fake session or bypass
Supabase authentication for local development.

For production, use a separate Supabase project and its production URL settings.
**Do not disable email confirmation in production.** Never put a service-role
key in a `VITE_*` variable or frontend source. The anonymous key is intended for
the browser; server-only credentials, if the deployment ever needs them, must
remain outside the frontend environment.

Future validation datasets should include athlete ID, sport, movement, camera angle, pose sequence, biomechanical measurements, expert technique label, and expert risk label. Suitable future evaluation includes MAE/RMSE, accuracy, precision, recall, F1, ROC-AUC, calibration, and inter-rater agreement.
