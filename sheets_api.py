import requests
import logging
import csv
import os
import json
from datetime import datetime
from config import SPREADSHEET_ID, SHEET_NAME, API_KEY, LOCAL_CSV_PATH

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_sheet_data():
    """Fetch data from Google Sheets API"""
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{SHEET_NAME}!A1:Z?alt=json&key={API_KEY}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'values' not in data:
            logger.warning("No data found in the sheet.")
            return []
        
        headers = data['values'][0]  # First row as headers
        rows = data['values'][1:]  # Remaining rows as data

        entries = [dict(zip(headers, row + [''] * (len(headers) - len(row)))) for row in rows]
        return entries

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Google Sheets: {e}")
        return []

def save_to_csv(entries):
    """Save formatted Google Sheets data to CSV"""
    if not entries:
        print("No data to save.")
        return

    # Define field names (headers from the first entry)
    fieldnames = list(entries[0].keys())

    # Check if file exists to avoid rewriting headers
    file_exists = os.path.exists(LOCAL_CSV_PATH)

    with open(LOCAL_CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Write header only once

        # Write data rows
        writer.writerows(entries)

    print(f"Saved {len(entries)} rows to {LOCAL_CSV_PATH}")

if __name__ == "__main__":
    entries = get_sheet_data()
    save_to_csv(entries)
    print(json.dumps(entries, indent=4))  # Print JSON for debugging
