import time
import pyautogui

# Function to type a string
def type_string(string, delay=0.05):
    for char in string:
        pyautogui.write(char)  # Simulate typing each character
        # time.sleep(delay)  # Small delay between keystrokes

# Function to press a key multiple times
def press_key(key, times=1, delay=0.2):
    for _ in range(times):
        pyautogui.press(key)
        # time.sleep(delay)

def switch_window():
    pyautogui.hotkey('alt', 'tab')
    # time.sleep(1)  

print("Switching window in 3 seconds...")
# time.sleep(3)

switch_window()

press_key('esc', 3)

type_string("Hello, Testing how the typing works")

pyautogui.press('enter')

type_string("Hmmmm, works fine?")

print("Typing completed.")
