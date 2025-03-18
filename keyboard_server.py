#!/usr/bin/env python3
import time
import json
import logging
from flask import Flask, request, jsonify

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Keyboard configuration
NULL_CHAR = chr(0)

def write_report(report):
    """Write a report to the HID device"""
    try:
        with open('/dev/hidg0', 'rb+') as fd:
            fd.write(report.encode())
        return True
    except Exception as e:
        logger.error(f"Error writing to HID device: {e}")
        return False

def release_keys():
    """Release all keys"""
    return write_report(NULL_CHAR*8)

def press_key(key_code):
    """Press and release a key"""
    write_report(NULL_CHAR*2 + chr(key_code) + NULL_CHAR*5)
    return release_keys()

def press_shift_key(key_code):
    """Press a key with shift modifier"""
    write_report(chr(32) + NULL_CHAR + chr(key_code) + NULL_CHAR*5)
    return release_keys()

def get_key_code(char):
    """Get HID key code for a character"""
    key_codes = {
        'a': 4, 'b': 5, 'c': 6, 'd': 7, 'e': 8, 'f': 9, 'g': 10, 'h': 11, 'i': 12,
        'j': 13, 'k': 14, 'l': 15, 'm': 16, 'n': 17, 'o': 18, 'p': 19, 'q': 20,
        'r': 21, 's': 22, 't': 23, 'u': 24, 'v': 25, 'w': 26, 'x': 27, 'y': 28,
        'z': 29, '1': 30, '2': 31, '3': 32, '4': 33, '5': 34, '6': 35, '7': 36,
        '8': 37, '9': 38, '0': 39, ' ': 44, '-': 45, '=': 46, '[': 47, ']': 48,
        '\\': 49, ';': 51, "'": 52, '`': 53, ',': 54, '.': 55, '/': 56, '\n': 40,
        '\t': 43
    }
    return key_codes.get(char.lower(), 0)

def type_string(text, delay=0.05):
    """Type a string by simulating keypresses"""
    logger.info(f"Typing string (length: {len(text)})")
    
    success = True
    for char in text:
        # Handle uppercase
        if char.isupper() and char.lower() in 'abcdefghijklmnopqrstuvwxyz':
            result = press_shift_key(get_key_code(char.lower()))
        else:
            result = press_key(get_key_code(char))
        
        if not result:
            success = False
        
        time.sleep(delay)  # Small delay between keypresses
    
    return success

# Server status tracking
start_time = time.time()
last_command_time = None
commands_executed = 0

# API endpoints
@app.route('/status', methods=['GET'])
def status():
    """Return the server status"""
    uptime = time.time() - start_time
    return jsonify({
        'status': 'online',
        'uptime': uptime,
        'uptime_formatted': f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
        'commands_executed': commands_executed,
        'last_command_time': last_command_time
    })

@app.route('/type', methods=['POST'])
def type_text():
    """Type the provided text"""
    global commands_executed, last_command_time
    
    try:
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        text = data['text']
        delay = data.get('delay', 0.05)  # Optional delay parameter
        
        logger.info(f"Received type request with text length: {len(text)}")
        
        success = type_string(text, delay)
        commands_executed += 1
        last_command_time = time.time()
        
        return jsonify({'success': success})
    
    except Exception as e:
        logger.error(f"Error processing type request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/keypress', methods=['POST'])
def keypress():
    """Press a specific key or key combination"""
    global commands_executed, last_command_time
    
    try:
        data = request.json
        
        if not data or 'key' not in data:
            return jsonify({'success': False, 'error': 'No key provided'}), 400
        
        key = data['key']
        logger.info(f"Received keypress request for key: {key}")
        
        # Handle special keys
        if key == 'enter':
            success = press_key(40)  # Enter key
        elif key == 'tab':
            success = press_key(43)  # Tab key
        elif key == 'space':
            success = press_key(44)  # Space key
        elif key == 'escape':
            success = press_key(41)  # Escape key
        elif key == 'backspace':
            success = press_key(42)  # Backspace key
        else:
            # Try to handle it as a regular character
            success = press_key(get_key_code(key))
        
        commands_executed += 1
        last_command_time = time.time()
        
        return jsonify({'success': success})
    
    except Exception as e:
        logger.error(f"Error processing keypress request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Run the server
if __name__ == '__main__':
    logger.info("Starting Raspberry Pi Keyboard Server...")
    app.run(host='0.0.0.0', port=5000)