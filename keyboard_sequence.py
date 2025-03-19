#!/usr/bin/env python3
import time
import requests
import json
import csv
import os
import logging
from datetime import datetime

# Import configuration settings
from config import (
    SPREADSHEET_ID, SHEET_NAME, API_KEY, LOCAL_CSV_PATH, LOG_FILE,
    TYPE_DELAY, FIELD_DELAY, ENTRY_DELAY, INITIAL_DELAY, CHECK_INTERVAL,
    FIELDS_TO_TYPE, FIELD_MAPPINGS, ID_FIELDS, BETWEEN_FIELDS_KEY, END_ENTRY_KEYS
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Keyboard HID constants
NULL_CHAR = chr(0)

def write_report(report):
    """Write a report to the HID device"""
    try:
        with open('/dev/hidg0', 'rb+') as fd:
            fd.write(report.encode())
        # Print statement for keyboard activity
        print(f"Keyboard action: Sent keyboard report")
    except Exception as e:
        error_msg = f"Error writing to HID device: {e}"
        logger.error(error_msg)
        print(f"ERROR: {error_msg}")
        raise

def release_keys():
    """Release all keys"""
    write_report(NULL_CHAR*8)

def press_key(key_code):
    """Press and release a key"""
    write_report(NULL_CHAR*2 + chr(key_code) + NULL_CHAR*5)
    release_keys()

def press_shift_key(key_code):
    """Press a key with shift modifier"""
    write_report(chr(32) + NULL_CHAR + chr(key_code) + NULL_CHAR*5)
    release_keys()

def get_key_code(char):
    """Get HID key code for a character"""
    key_codes = {
        'a': 4, 'b': 5, 'c': 6, 'd': 7, 'e': 8, 'f': 9, 'g': 10, 'h': 11, 'i': 12,
        'j': 13, 'k': 14, 'l': 15, 'm': 16, 'n': 17, 'o': 18, 'p': 19, 'q': 20,
        'r': 21, 's': 22, 't': 23, 'u': 24, 'v': 25, 'w': 26, 'x': 27, 'y': 28,
        'z': 29, '1': 30, '2': 31, '3': 32, '4': 33, '5': 34, '6': 35, '7': 36,
        '8': 37, '9': 38, '0': 39, ' ': 44, '-': 45, '=': 46, '[': 47, ']': 48,
        '\\': 49, ';': 51, "'": 52, '`': 53, ',': 54, '.': 55, '/': 56, '\t': 43,
        '|': 49, ':': 51, '"': 52, '<': 54, '>': 55, '?': 56, '_': 45, '+': 46,
        '{': 47, '}': 48
    }
    return key_codes.get(char.lower(), 0)

def type_string(string, delay=None):
    """Type a string by simulating keypresses"""
    if delay is None:
        delay = TYPE_DELAY
        
    logger.info(f"Typing string: {string}")
    print(f"TYPING: '{string}'")
    
    for char in string:
        if char.isupper() or char in '!@#$%^&*()_+{}|:"<>?':
            # Special characters that need shift
            shifted_chars = {
                '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', 
                '*': '8', '(': '9', ')': '0', '_': '-', '+': '=', '{': '[', '}': ']', 
                '|': '\\', ':': ';', '"': "'", '<': ',', '>': '.', '?': '/'
            }
            
            if char in shifted_chars:
                print(f"  - Pressing SHIFT+{shifted_chars[char]}")
                press_shift_key(get_key_code(shifted_chars[char]))
            else:
                print(f"  - Pressing SHIFT+{char.lower()}")
                press_shift_key(get_key_code(char.lower()))
        else:
            print(f"  - Pressing {char}")
            press_key(get_key_code(char))
        time.sleep(delay)  # Small delay between keypresses

def press_enter():
    """Press the Enter key"""
    print("ACTION: Pressing ENTER key")
    press_key(40)  # 40 is ENTER key

def press_tab():
    """Press the Tab key"""
    print("ACTION: Pressing TAB key")
    press_key(43)  # 43 is TAB key

def press_escape():
    """Press the Escape key"""
    print("ACTION: Pressing ESC key")
    press_key(41)  # 41 is ESC key

def press_key_by_name(key_name, times=1):
    """Press a key by name (e.g., 'enter', 'tab', 'esc')"""
    key_name = key_name.lower()
    for _ in range(times):
        if key_name == 'enter':
            press_enter()
        elif key_name == 'tab':
            press_tab()
        elif key_name == 'esc' or key_name == 'escape':
            press_escape()
        else:
            try:
                # Try to use it as a key code number
                key_code = int(key_name)
                print(f"ACTION: Pressing key code {key_code}")
                press_key(key_code)
            except ValueError:
                print(f"WARNING: Unknown key '{key_name}'")
        time.sleep(0.1)  # Small delay between key presses

def get_sheet_data():
    """Fetch data from Google Sheets API"""
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{SHEET_NAME}!A1:Z?alt=json&key={API_KEY}'
    
    print("\n" + "="*60)
    print(f"FETCHING DATA: Requesting data from Google Sheets API")
    print(f"URL: {url}")
    
    try:
        logger.info(f"Fetching data from Google Sheets")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if 'values' not in data:
            warning_msg = "No data found in the sheet."
            logger.warning(warning_msg)
            print(f"WARNING: {warning_msg}")
            return []
            
        headers = data['values'][0]
        rows = data['values'][1:]
        
        print(f"SUCCESS: Retrieved data with {len(rows)} rows")
        print(f"Headers: {headers}")
        
        # Convert to list of dictionaries
        entries = []
        for row in rows:
            # Pad row with empty strings if shorter than headers
            padded_row = row + [''] * (len(headers) - len(row))
            entries.append(dict(zip(headers, padded_row)))
        
        logger.info(f"Fetched {len(entries)} entries from Google Sheets")
        
        # Print the first entry as an example
        if entries:
            print("\nSample entry:")
            for key, value in entries[0].items():
                print(f"  {key}: {value}")
        
        return entries
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching data from Google Sheets: {e}"
        logger.error(error_msg)
        print(f"ERROR: {error_msg}")
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

def process_sheet_data(entries):
    """Process the sheet data similar to your save_to_csv function"""
    processed_entries = []
    
    print("\nPROCESSING DATA: Preparing entries for typing")
    
    for i, entry in enumerate(entries):
        # Create a copy of the entry to avoid modifying the original
        processed_entry = entry.copy()
        
        print(f"\nProcessing entry #{i+1}:")
        
        # Process timestamp if present
        if 'Timestamp' in processed_entry:
            timestamp = processed_entry['Timestamp']
            try:
                dt = datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S')
                processed_entry['Date'] = dt.strftime('%Y-%m-%d')
                processed_entry['Time'] = dt.strftime('%H:%M:%S')
                print(f"  - Split Timestamp: Date={processed_entry['Date']}, Time={processed_entry['Time']}")
            except ValueError:
                processed_entry['Date'] = ''
                processed_entry['Time'] = ''
                print(f"  - Could not parse Timestamp: {timestamp}")
        
        # Process Vehicle Type if present
        if 'Vehicle Type' in processed_entry:
            vehicle_type = processed_entry['Vehicle Type']
            cost, vehicle = split_vehicle_type(vehicle_type)
            processed_entry['Cost'] = cost
            processed_entry['Vehicle Type'] = vehicle
            print(f"  - Split Vehicle Type: Vehicle={processed_entry['Vehicle Type']}, Cost={processed_entry['Cost']}")
        
        processed_entries.append(processed_entry)
    
    print(f"\nProcessed {len(processed_entries)} entries total")
    return processed_entries

def load_processed_entries():
    """Load previously processed entries from local CSV"""
    processed = set()
    
    print(f"\nLOADING PROCESSED ENTRIES: from {LOCAL_CSV_PATH}")
    
    if not os.path.exists(LOCAL_CSV_PATH):
        # Create the file with headers if it doesn't exist
        print(f"  - CSV file not found. Creating new file with headers")
        with open(LOCAL_CSV_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'UniqueID'])
        print(f"  - Created new empty CSV tracking file")
        return processed
    
    try:
        with open(LOCAL_CSV_PATH, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    processed.add(row[1])  # Add unique ID to set
        
        logger.info(f"Loaded {len(processed)} processed entries from local CSV")
        print(f"  - Successfully loaded {len(processed)} processed entries")
        
        # Print a few examples if available
        processed_list = list(processed)
        if processed_list:
            examples = processed_list[:3]  # First 3 examples
            print(f"  - Sample IDs:")
            for i, example in enumerate(examples):
                # Truncate very long IDs for readability
                if len(example) > 50:
                    print(f"    {i+1}. {example[:50]}...")
                else:
                    print(f"    {i+1}. {example}")
                    
            if len(processed_list) > 3:
                print(f"    ... and {len(processed_list) - 3} more")
        
        return processed
    except Exception as e:
        error_msg = f"Error loading processed entries: {e}"
        logger.error(error_msg)
        print(f"  - ERROR: {error_msg}")
        return set()

def save_processed_entry(entry_id):
    """Save a processed entry to the local CSV"""
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\nSAVING PROCESSED ENTRY:")
        print(f"  - Timestamp: {now}")
        print(f"  - Entry ID: {entry_id[:50]}..." if len(entry_id) > 50 else f"  - Entry ID: {entry_id}")
        
        with open(LOCAL_CSV_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([now, entry_id])
            
        logger.info(f"Saved entry {entry_id} to processed entries")
        print(f"  - Successfully saved to {LOCAL_CSV_PATH}")
    except Exception as e:
        error_msg = f"Error saving processed entry: {e}"
        logger.error(error_msg)
        print(f"  - ERROR: {error_msg}")

def generate_entry_id(entry):
    """Generate a unique ID for an entry based on its content"""
    # Join all values from configured fields
    values = []
    for field in ID_FIELDS:
        values.append(str(entry.get(field, '')))
    
    unique_id = '|'.join(values)
    print(f"Generated unique ID: {unique_id[:50]}..." if len(unique_id) > 50 else f"Generated unique ID: {unique_id}")
    return unique_id

def apply_field_mapping(field, value):
    """Apply any configured field mappings"""
    if field in FIELD_MAPPINGS and value in FIELD_MAPPINGS[field]:
        mapped_value = FIELD_MAPPINGS[field][value]
        print(f"  Applied mapping: '{value}' -> '{mapped_value}'")
        return mapped_value
    return value

def type_entry_data(entry):
    """Type the data from a single entry"""
    logger.info(f"Starting to type data for entry")
    
    print("\n" + "="*60)
    print("TYPING ENTRY: Beginning keyboard automation sequence")
    print("Entry data:")
    for k, v in entry.items():
        print(f"  {k}: {v}")
    
    # Give some time to switch focus if needed
    print(f"\nWaiting {INITIAL_DELAY} seconds for application focus...")
    time.sleep(INITIAL_DELAY)
    
    # Type fields in the specified order
    print("\nTyping fields in sequence:")
    for field in FIELDS_TO_TYPE:
        if field in entry:
            value = entry.get(field, '')
            print(f"\nField: {field}")
            print(f"  Original value: '{value}'")
            
            # Apply any configured field mappings
            mapped_value = apply_field_mapping(field, value)
            if mapped_value != value:
                print(f"  Mapped value: '{mapped_value}'")
                value = mapped_value
            
            # Type the value
            print(f"  Typing value: '{value}'")
            type_string(str(value))
            
            # Press configured key between fields
            print(f"  Pressing: {BETWEEN_FIELDS_KEY}")
            press_key_by_name(BETWEEN_FIELDS_KEY)
            
            # Delay between fields
            print(f"  Waiting {FIELD_DELAY} seconds before next field...")        
            time.sleep(FIELD_DELAY)
        else:
            print(f"\nSkipping field {field} (not in entry data)")
    
    # Press any configured end-of-entry keys
    if END_ENTRY_KEYS:
        print("\nFinishing entry:")
        for key_config in END_ENTRY_KEYS:
            key_name = key_config.get('key', 'enter')
            times = key_config.get('times', 1)
            print(f"  - Pressing {key_name.upper()} x{times}")
            press_key_by_name(key_name, times)
    
    print(f"\nWaiting {ENTRY_DELAY} seconds after entry completion...")
    time.sleep(ENTRY_DELAY)  # Delay after completing an entry
    print("ENTRY COMPLETED: Keyboard sequence finished")
    logger.info(f"Completed typing entry data")

def main():
    """Main function to check for new data and type it"""
    logger.info("Starting Vehicle Entry Keyboard Automation")
    
    print("\n" + "="*80)
    print("STARTING VEHICLE ENTRY KEYBOARD AUTOMATION")
    print("="*80)
    print(f"Configuration:")
    print(f"  Spreadsheet ID: {SPREADSHEET_ID}")
    print(f"  Sheet Name: {SHEET_NAME}")
    print(f"  CSV Path: {LOCAL_CSV_PATH}")
    print(f"  Check Interval: {CHECK_INTERVAL} seconds")
    print(f"  Fields to Type: {', '.join(FIELDS_TO_TYPE)}")
    print("="*80 + "\n")
    
    cycle_count = 0
    
    while True:
        cycle_count += 1
        try:
            print("\n" + "="*60)
            print(f"CYCLE #{cycle_count}: Checking for new entries")
            print("="*60)
            
            # Load previously processed entries
            processed_entries = load_processed_entries()
            print(f"Loaded {len(processed_entries)} previously processed entries")
            
            # Fetch current sheet data
            raw_entries = get_sheet_data()
            
            if not raw_entries:
                print("No entries found in the Google Sheet")
                logger.warning("No entries found in the Google Sheet")
            else:
                # Process the sheet data to prepare for typing
                entries = process_sheet_data(raw_entries)
                
                # Find new entries
                new_entries = []
                for entry in entries:
                    # Generate a unique ID for this entry
                    entry_id = generate_entry_id(entry)
                    
                    # Check if this entry has already been processed
                    if entry_id not in processed_entries:
                        print(f"Found NEW entry with ID: {entry_id[:30]}...")
                        new_entries.append((entry, entry_id))
                    else:
                        print(f"Skipping EXISTING entry with ID: {entry_id[:30]}...")
                
                if new_entries:
                    print("\n" + "-"*60)
                    print(f"FOUND {len(new_entries)} NEW ENTRIES TO PROCESS")
                    print("-"*60)
                    logger.info(f"Found {len(new_entries)} new entries to process")
                    
                    for i, (entry, entry_id) in enumerate(new_entries):
                        print(f"\nPROCESSING ENTRY {i+1} of {len(new_entries)}")
                        logger.info(f"Processing entry {i+1}/{len(new_entries)} with ID: {entry_id}")
                        
                        # Type this entry's data
                        type_entry_data(entry)
                        
                        # Mark as processed
                        save_processed_entry(entry_id)
                        print(f"Entry marked as processed in tracking file")
                        
                        # Add a delay between entries
                        if i < len(new_entries) - 1:  # Skip delay after last entry
                            print(f"Waiting {ENTRY_DELAY} seconds before next entry...")
                            time.sleep(ENTRY_DELAY)
                else:
                    print("\nNo new entries found to process")
                    logger.info("No new entries to process")
            
            # Wait before next check
            print(f"\nCycle complete. Waiting {CHECK_INTERVAL} seconds before next check...")
            logger.info(f"Waiting {CHECK_INTERVAL} seconds before next check")
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            error_msg = f"Error in main loop: {e}"
            logger.error(error_msg)
            print(f"\nERROR: {error_msg}")
            print(f"Waiting {CHECK_INTERVAL} seconds before retry...")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()