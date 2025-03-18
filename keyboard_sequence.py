import time
import pyautogui
import subprocess
import keyboard
import json

# Function to type a string
def type_string(string, delay=0.05):
    for char in string:
        pyautogui.write(char)
        time.sleep(delay)

# Function to switch windows using Alt+Tab
def switch_window():
    pyautogui.hotkey('alt', 'tab')
    time.sleep(1)  # Allow the switch to complete

# Function to fetch data from Google Sheets API
def fetch_google_sheets():
    # Run sheets api script
    subprocess.run(["python", "sheets_api.py"]) 

# Function to type all values from fetched data
def type_data_from_sheets(data):
    if not data:
        print("No data to type.")
        return

    switch_window()  # Switch to the target application
    
    for entry in data:
        row_values = list(entry.values())  # Get all values in the row
        text_to_type = " | ".join(row_values)  # Join values with separator
        type_string(text_to_type)  # Type the values
        pyautogui.press("enter")  # Press Enter after each row

# Function to execute everything when hotkey is pressed
def process_data():
    data = fetch_google_sheets()
    type_data_from_sheets(data)

# Bind a hotkey to fetch data, switch window, and start typing
keyboard.add_hotkey("ctrl+alt+g", process_data)

print("Press 'Ctrl + Alt + G' to fetch Google Sheets data, switch windows, and type the data.")
keyboard.wait()  # Keep the script running
