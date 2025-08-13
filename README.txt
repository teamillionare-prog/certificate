
# Certificate Generator (Streamlit)

This is a simple, no‑coding app to generate certificates from a **single template image** and a **list of recipients**.

## Quick Start (Windows/Mac/Linux)
1) Install Python 3.9+ from python.org (if you don't have it).
2) Open a terminal in the folder you downloaded.
3) Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4) Run the app:
   ```
   streamlit run app.py
   ```
5) Your browser will open. Upload:
   - `template_sample.png` (or your own PNG/JPG certificate template)
   - `recipients_sample.csv` or `.xlsx` (or your own file)
   - Optional: a `.ttf` font to match your brand

## How to position the text
- In the left sidebar, adjust **X/Y position** and **Font size** for each field.
- Check **Center this field** to center around X and wrap long text within **Max text width**.
- Use placeholders like `{Name}` or `{Course}` inside the field text to pull data from your column names.

## Output
- Choose **PNG** (images) or **PDF** (one per certificate).
- Click **Generate for all rows**, then download the ZIP.

## Sample files included
- `template_sample.png` – a simple template with border and placeholders.
- `recipients_sample.csv` / `.xlsx` – sample data.

