# AI Smart Wardrobe — Working Web Application

A fully functional, local web application using Streamlit and SQLite.

## Run

1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Install dependencies: `python -m pip install -r requirements.txt`
4. Start the web application: `python -m streamlit run app.py`
5. Open the local URL displayed in your terminal (normally http://localhost:8501).

On Windows, `py -m pip install -r requirements.txt` and `py -m streamlit run app.py` may be used instead.

## Demo in class

1. Go to Dashboard and click **Load 12 sample clothing items**.
2. Open My Wardrobe and show that the items are stored.
3. Add a new clothing item and show it in My Wardrobe.
4. Open Outfit Generator, select **Work** and **Classic**, and generate outfits.
5. Save a recommendation and open Saved Outfits.
6. Stop and restart the server; the saved data persists in `wardrobe.db`.

## Technical details

- `wardrobe.db` is created automatically in this directory on first run.
- `clothes` stores clothing attributes and optional local image paths.
- `saved_outfits` stores selected outfit IDs and the occasion/style.
- The matching algorithm scores occasion, style, season and color harmony, without an external AI service.
- ChatGPT was used as an AI development assistant. Do not claim this is a trained machine-learning model.
- Local data remains on the machine hosting Streamlit. Do not deploy publicly without adding authentication and storage security.

## Instructor rubric

- Problem: daily clothing decisions and wardrobe organization.
- Working web app + database: Streamlit CRUD, SQLite storage and saved outfits.
- AI tools used: ChatGPT for coding, design, troubleshooting and recommendation rules.
- Live demo: see steps above.
