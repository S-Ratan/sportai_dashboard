# SportAI Dashboard

Frontend dashboard prototype for the SIH PS-02 AI-based Sports Performance Analysis and Injury Prevention System.

## Run

```bash
npm install
npm run dev
```

The current dashboard uses mock data and is ready to connect to a FastAPI backend.

## Planned API integration

- `/api/athletes`
- `/api/sessions`
- `/api/analysis/upload`
- `/api/analysis/{session_id}`
- `/api/performance/{athlete_id}`
- `/api/risk/{athlete_id}`
- `/api/recommendations/{athlete_id}`
