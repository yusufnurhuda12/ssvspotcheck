# KMZ Generator

A premium web application built with Python (Flask) that instantly converts spreadsheet data (Excel/Google Sheets) into Google Earth KMZ pinpoints.

## Features
- **Copy & Paste Data:** Directly paste your tabular coordinates without needing to upload files.
- **Auto-parse Merged Cells:** Intelligently handles missing sequential rows (merged cell effect).
- **Custom Site ID:** Set a specific name for your exported KMZ files through an elegant modal.
- **Premium UI/UX:** Deep space dashboard theme with glassmorphism effects and modern typography.
- **Vercel Ready:** Pre-configured for serverless deployment on Vercel.

## Tech Stack
- **Backend:** Python, Flask, `simplekml`
- **Frontend:** HTML5, CSS3 (Vanilla, Glassmorphism), Vanilla JavaScript
- **Deployment:** Vercel (Serverless)

## How to Run Locally

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the environment and install dependencies:
```bash
# Windows
.\venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the Flask server:
```bash
python app.py
```

4. Open `http://127.0.0.1:5000` in your browser.

## Deployment to Vercel
Simply import this repository into Vercel. The included `vercel.json` and `requirements.txt` will automatically handle the serverless Python setup and dependencies. No further configuration is needed!
