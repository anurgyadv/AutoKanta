import requests
import argparse
import json

def check_status(host):
    """Check the status of the keyboard server"""
    try:
        response = requests.get(f"http://{host}:5000/status")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def type_text(host, text, delay=0.05):
    """Send text to be typed by the keyboard server"""
    try:
        data = {
            "text": text,
            "delay": delay
        }
        print(f"Sending text: '{text}' to server...")
        response = requests.post(f"http://{host}:5000/type", json=data)
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def press_key(host, key):
    """Send a specific keypress to the keyboard server"""
    try:
        data = {
            "key": key
        }
        print(f"Sending keypress '{key}' to server...")
        response = requests.post(f"http://{host}:5000/keypress", json=data)
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test client for Raspberry Pi Keyboard Server")
    parser.add_argument("--host", required=True, help="IP address of the Raspberry Pi")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check server status")
    
    # Type command
    type_parser = subparsers.add_parser("type", help="Type text")
    type_parser.add_argument("text", help="Text to type")
    type_parser.add_argument("--delay", type=float, default=0.05, help="Delay between keypresses")
    
    # Key command
    key_parser = subparsers.add_parser("key", help="Press a key")
    key_parser.add_argument("key", help="Key to press (e.g., 'enter', 'tab', 'a')")
    
    args = parser.parse_args()
    
    if args.command == "status":
        check_status(args.host)
    elif args.command == "type":
        type_text(args.host, args.text, args.delay)
    elif args.command == "key":
        press_key(args.host, args.key)
    else:
        parser.print_help()