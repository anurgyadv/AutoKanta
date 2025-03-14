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

def load_existing_csv():
    """Load existing CSV data to check for duplicates"""
    if not os.path.exists(LOCAL_CSV_PATH):
        return set()  # Return empty set if file doesn't exist

    existing_entries = set()
    with open(LOCAL_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create a tuple key using relevant columns
            key = (row['Timestamp'], row['Vehicle Type'], row['Material'], row['Party Ref:'])
            existing_entries.add(key)

    return existing_entries

def save_to_csv(entries):
    """Save formatted Google Sheets data to CSV while avoiding duplicates"""
    if not entries:
        print("No data to save.")
        return

    existing_entries = load_existing_csv()

    # Define field names (headers from the first entry)
    fieldnames = list(entries[0].keys())

    # Check if file exists to avoid rewriting headers
    file_exists = os.path.exists(LOCAL_CSV_PATH)

    new_entries = []
    for entry in entries:
        key = (entry['Timestamp'], entry['Vehicle Type'], entry['Material'], entry['Party Ref:'])
        if key not in existing_entries:
            new_entries.append(entry)
            existing_entries.add(key)  # Add to set to prevent future duplicates in the same run

    if not new_entries:
        print("No new entries to save.")
        return

    with open(LOCAL_CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Write header only once

        # Write only new data rows
        writer.writerows(new_entries)

    print(f"Saved {len(new_entries)} new rows to {LOCAL_CSV_PATH}")

if __name__ == "__main__":
    entries = get_sheet_data()
    save_to_csv(entries)
    print(json.dumps(entries, indent=4))  # Print JSON for debugging
