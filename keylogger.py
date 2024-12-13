import ctypes
import requests
from pynput.keyboard import Listener, Key
import uuid  
import sys
from datetime import datetime

admin_server_url = ''
student_name = ''
admin_id = ''
pc_number = 'PC-1'  
session_id = '' 
caps_lock_on = False
shift_pressed = False 
ctrl_pressed = False  
typed_text = "" 
admin_ip = ''

def disable_close_button():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        GWL_STYLE = -16
        WS_SYSMENU = 0x00080000  
        WS_MINIMIZEBOX = 0x20000 
        WS_MAXIMIZEBOX = 0x10000  
        
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        
        new_style = style & ~WS_SYSMENU & ~WS_MINIMIZEBOX & ~WS_MAXIMIZEBOX
        
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
        
        ctypes.windll.user32.DrawMenuBar(hwnd)

def validate_admin(admin_id, admin_ip):
    try:
        response = requests.post(f'http://{admin_ip}:5000/validate_admin', json={'admin_id': admin_id})
        if response.status_code == 200:
            return True
        else:
            print(f"Admin validation failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error validating admin: {e}")
        return False

def start_keylogger(admin_id, admin_ip, name, pc_num):
    global admin_server_url, student_name, pc_number, session_id
    admin_server_url = f'http://{admin_ip}:5000/log'  
    student_name = name
    pc_number = pc_num  
    session_id = str(uuid.uuid4()) 

def send_key_to_admin(key):
    global student_name, admin_id, pc_number, session_id, caps_lock_on, shift_pressed, ctrl_pressed, typed_text

    try:
        if key == Key.caps_lock:
            caps_lock_on = not caps_lock_on
            # print(f"Caps Lock toggled: {'ON' if caps_lock_on else 'OFF'}")
            return

        if key in {Key.shift, Key.shift_l, Key.shift_r}:
            shift_pressed = True
            # print("Shift pressed")
            return

        if key in {Key.ctrl_l, Key.ctrl_r}:
            ctrl_pressed = True
            # print("Ctrl pressed")
            return
        
        
        if ctrl_pressed and hasattr(key, 'char') and key.char == '\x09':
            print("Ctrl+i detected. Closing the program...")
            cleanup_and_exit()  
            return

        if ctrl_pressed and hasattr(key, 'char') and key.char == '\x03':
            # print(f"Debug: Ctrl+C detected by {student_name} on PC {pc_number}")
            current_time = datetime.now().strftime('%Y-%m-%d %I:%M %p')
            # print(f"Debug: Ctrl+C detected - Name: {student_name}, PC Number: {pc_number}, Time: {current_time}")
            response = requests.post(f'http://{admin_ip}:5000/notify', json={
                'notification': f"{student_name} pressed Ctrl+C on PC: {pc_number} at {current_time}",
                'name': student_name,
                'admin_id': admin_id,
                'pc_number': pc_number,
                'session_id': session_id,
                'timestamp': current_time
            })
            # print(f"Sent Ctrl+C notification, Status: {response.status_code}")
            return  

        if ctrl_pressed and hasattr(key, 'char') and key.char == '\x16':
            # print(f"Debug: Ctrl+V detected by {student_name} on PC {pc_number}")
            current_time = datetime.now().strftime('%Y-%m-%d %I:%M %p')
            # print(f"Debug: Ctrl+v detected - Name: {student_name}, PC Number: {pc_number}, Time: {current_time}")
            response = requests.post(f'http://{admin_ip}:5000/notify', json={
                'notification': f"{student_name} pressed Ctrl+V on PC: {pc_number} at {current_time}",
                'name': student_name,
                'admin_id': admin_id,
                'pc_number': pc_number,
                'session_id': session_id
            })
            # print(f"Sent Ctrl+V notification, Status: {response.status_code}")
            return  

        
        if ctrl_pressed and hasattr(key, 'char') and key.char == '\x18':
            # print(f"Debug: Ctrl+X detected by {student_name} on PC {pc_number}")
            current_time = datetime.now().strftime('%Y-%m-%d %I:%M %p')
            # print(f"Debug: Ctrl+x detected - Name: {student_name}, PC Number: {pc_number}, Time: {current_time}")
            response = requests.post(f'http://{admin_ip}:5000/notify', json={
                'notification': f"{student_name} pressed Ctrl+X on PC: {pc_number} at {current_time}",
                'name': student_name,
                'admin_id': admin_id,
                'pc_number': pc_number,
                'session_id': session_id
            })
            # print(f"Sent Ctrl+X notification, Status: {response.status_code}")
            return  

        if hasattr(key, 'char') and key.char:
            char = key.char

            if shift_pressed and char.isalpha():
                char = char.upper() if char.islower() else char.lower()

            elif not shift_pressed and caps_lock_on and char.isalpha():
                char = char.upper() if char.islower() else char

            typed_text += char

            response = requests.post(admin_server_url, json={
                'typed_text': char,
                'name': student_name,
                'admin_id': admin_id,
                'pc_number': pc_number,
                'session_id': session_id
            })
            # print(f"Sent character: {char}, Status: {response.status_code}")

        elif key == Key.space:
            typed_text += " "
            response = requests.post(admin_server_url, json={
                'typed_text': " ",
                'name': student_name,
                'admin_id': admin_id,
                'pc_number': pc_number,
                'session_id': session_id
            })
            # print(f"Sent space, Status: {response.status_code}")

        elif key == Key.enter:
            typed_text += "\n"
            response = requests.post(admin_server_url, json={
                'typed_text': "\n",
                'name': student_name,
                'admin_id': admin_id,
                'pc_number': pc_number,
                'session_id': session_id
            })
            # print(f"Sent newline, Status: {response.status_code}")

        elif key == Key.backspace:
            if typed_text:
                typed_text = typed_text[:-1]
                response = requests.post(admin_server_url, json={
                    'action': 'backspace',
                    'name': student_name,
                    'admin_id': admin_id,
                    'pc_number': pc_number,
                    'session_id': session_id
                })
                # print(f"Sent backspace, Status: {response.status_code}")

        elif key == Key.tab:
            typed_text += "\t"
            response = requests.post(admin_server_url, json={
                'typed_text': "\t",
                'name': student_name,
                'admin_id': admin_id,
                'pc_number': pc_number,
                'session_id': session_id
            })
            # print(f"Sent tab, Status: {response.status_code}")

    except Exception as e:
        print(f"Failed to send keypress: {e}")

def on_key_release(key):
    global shift_pressed, ctrl_pressed
    if key in {Key.shift, Key.shift_l, Key.shift_r}:
        shift_pressed = False
        # print("Shift released")
    elif key in {Key.ctrl_l, Key.ctrl_r}:
        ctrl_pressed = False
        # print("Ctrl released")


def cleanup_and_exit():
    """Perform cleanup and exit the program."""
    print("Performing cleanup...")
    current_time = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    try:
        response = requests.post(f'http://{admin_ip}:5000/notify', json={
            'notification': f"The executable has been closed by {student_name} on PC No: {pc_number} at {current_time}.",
            'name': student_name,
            'admin_id': admin_id,
            'pc_number': pc_number,
            'session_id': session_id
        })
        print(f"Session closed notification sent, Status: {response.status_code}")
    except Exception as e:
        print(f"Failed to notify server about session closure: {e}")

    sys.exit("Keylogger closed by user with Ctrl+i")




def start_listener():
    with Listener(on_press=send_key_to_admin, on_release=on_key_release) as listener:
        listener.join()

def main():
    global admin_id, admin_ip, student_name, pc_number
    try:
        print("Important Note :-")
        print("1.To minimize the window, click anywhere outside the executable window.")
        print("2.Press Ctrl+I to close the executable window.")
        print("3.The executable will continue running in the background until you press Ctrl+I to close it.")
        print("4.Avoid using boilerplate code, as this keylogger is not designed to detect such patterns.")
        print("  It is focused solely on detecting individual key presses.")
        print(" ")
        disable_close_button()
        admin_id = input("Enter Admin ID: ")
        admin_ip = input("Enter Admin IP: ")
        student_name = input("Enter Your Name: ")
        pc_number = input("Enter Your PC Number: ")  

        if validate_admin(admin_id, admin_ip):
            start_keylogger(admin_id, admin_ip, student_name, pc_number)
            print(f"Session started with ID: {session_id}") 
            start_listener()  
        else:
            print("Error: Admin ID does not match any registered admin ID.")
    except Exception as e:
        print(f"An error occurred: {e}")

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()