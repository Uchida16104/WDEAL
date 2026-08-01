# WDEAL

WDEAL (Web Data Editor, Analyzer and Learner) is a hybrid data-workbench project:

- Python/FastAPI backend for analysis and export
- Vue + TypeScript frontend
- HTMX for real-time server analysis swaps
- Chart.js for chart rendering
- Alpine.js and hyperscript for lightweight interaction hooks
- Motion One for panel animation

## What it does

- Accepts pasted SQL, CSV, and VBA text
- Analyzes the inputs in Python
- Executes SQL against the parsed CSV table via DuckDB
- Generates real-time charts and tables
- Exports the current result as CSV, XLSX, or XLSM

## Project layout

- `backend/` — FastAPI API and export logic
- `frontend/` — Vite + Vue + TypeScript UI

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, usually `http://localhost:5173`.

The frontend proxies `/api/*` to the backend on port `8000`.

## Notes

- The XLSM export writes a macro-enabled workbook container. It does not inject a VBA project module automatically.
- If you want true embedded macros, extend `backend/app/export.py` to copy a trusted `vbaProject.bin` from a template workbook.
- The project is structured to be robust, but environment-specific dependency or browser differences can still require adjustment.
