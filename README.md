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

1. Copy `.env.example` to `.env` and supply the Supabase URL and anonymous key.
2. Run `backend/migrations/20260816_analysis_reports.sql` in the Supabase SQL editor after reviewing the existing `analysis_reports` table.
3. Start the backend with `cd backend; .venv\Scripts\python -m uvicorn app.main:app --reload`.
4. Start the dashboard with `npm run dev`.

## API

- `POST /api/analyze` accepts MP4/AVI/MOV/MKV video uploads and returns pose data, biomechanics, rule-based performance/risk screening, recommendations, and technical analysis quality.

Future validation datasets should include athlete ID, sport, movement, camera angle, pose sequence, biomechanical measurements, expert technique label, and expert risk label. Suitable future evaluation includes MAE/RMSE, accuracy, precision, recall, F1, ROC-AUC, calibration, and inter-rater agreement.
