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

def split_vehicle_type(vehicle_type):
    """Split Vehicle Type into Cost and Vehicle Type"""
    # Example: "RMC TRUCK 250" -> Cost = "250", Vehicle Type = "RMC TRUCK"
    parts = vehicle_type.split()
    if parts and parts[-1].isdigit():  # Check if the last part is a number
        cost = parts[-1]
        vehicle = ' '.join(parts[:-1])  # Join all parts except the last one
        return cost, vehicle
    return '', vehicle_type  # If no cost is found, return empty cost and original vehicle type

def save_to_csv(entries):
    """Save formatted Google Sheets data to CSV"""
    if not entries:
        print("No data to save.")
        return

    # Define field names (headers from the first entry)
    fieldnames = list(entries[0].keys())

    # Remove 'Timestamp' and 'Vehicle Type', and add 'Date', 'Time', 'Cost', and 'Vehicle Type'
    if 'Timestamp' in fieldnames:
        fieldnames.remove('Timestamp')
    if 'Vehicle Type' in fieldnames:
        fieldnames.remove('Vehicle Type')
    fieldnames.extend(['Date', 'Time', 'Cost', 'Vehicle Type'])

    # Check if file exists to avoid rewriting headers
    file_exists = os.path.exists(LOCAL_CSV_PATH)

    # Process entries to split Timestamp, Vehicle Type, and capitalize Yes/No answers
    processed_entries = []
    for entry in entries:
        # Split the Timestamp into Date and Time
        timestamp = entry.pop('Timestamp', '')
        try:
            dt = datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S')  # Adjust format to match your data
            entry['Date'] = dt.strftime('%Y-%m-%d')
            entry['Time'] = dt.strftime('%H:%M:%S')
        except ValueError:
            entry['Date'] = ''
            entry['Time'] = ''

        # Split Vehicle Type into Cost and Vehicle Type
        vehicle_type = entry.pop('Vehicle Type', '')
        cost, vehicle = split_vehicle_type(vehicle_type)
        entry['Cost'] = cost
        entry['Vehicle Type'] = vehicle

        # Capitalize 'Yes' or 'No' answers
        for key, value in entry.items():
            if isinstance(value, str) and value.lower() in ['yes', 'no', 'y', 'n']:
                entry[key] = value.upper()

        processed_entries.append(entry)

    with open(LOCAL_CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Write header only once

        # Write data rows
        writer.writerows(processed_entries)

    print(f"Saved {len(processed_entries)} rows to {LOCAL_CSV_PATH}")

if __name__ == "__main__":
    entries = get_sheet_data()
    save_to_csv(entries)
    print(json.dumps(entries, indent=4))  # Print JSON for debugging