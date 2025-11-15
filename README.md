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

## Reproducible development environment (how to get exactly what I have)

This project includes small helpers so someone who clones the repo can get the same
development environment you see locally (on Windows PowerShell).

1. Copy environment secrets into a local file named `.env` at the repository root.
	 Use the included `.env.example` as a template and DO NOT commit `.env`.

	 - Create `.env` (example):

		 MONGODB_URI="mongodb+srv://<db_user>:<db_password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"

2. Run the setup script (PowerShell) from the repo root to create the Python venv and
	 install backend and frontend dependencies:

```powershell
# from repo root
.\setup-dev.ps1
# or to also open new windows and start backend/frontend:
.\setup-dev.ps1 -Start
```

3. Run servers (if you didn't use -Start):

```powershell
# Backend (from repo root)
cd api
. .\.venv\Scripts\Activate.ps1
python app.py

# Frontend (new terminal)
cd frontend
npm run dev
```

Notes
- The file `.env.example` shows the required secrets. Keep your real `.env` private.
- The repository no longer tracks `api/venv` (virtualenv) so clones will be lean. Use the
	setup script to recreate the environment locally.


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