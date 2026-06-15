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
