# HaaS Proof-of-Concept

This repository will host a full-stack Hardware-as-a-Service (HaaS) proof-of-concept. Step 1 is a static frontend prototype using React + TypeScript + Vite.

## Run the static frontend locally

Requirements: Node.js 18+

```bash
cd frontend
npm install
npm run dev
```

Then open the URL shown by Vite (typically http://localhost:5173).

## Project structure (current)

- `instructions.txt` — high-level functional + technical spec
- `frontend/` — static React + TypeScript prototype (no API calls yet)

## Next steps

- Hook up backend API (FastAPI/Flask) and MongoDB
- Add auth, projects, and hardware endpoints
- Replace static UI with dynamic data fetching and mutations
- Add tests (PyTest) for backend
- Deploy to cloud (Heroku/Render)
fake change to push