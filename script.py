from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pyautogui
from pynput import keyboard, mouse
import threading
import sys
import random
import os

pyautogui.FAILSAFE = False

# Variables to store keyboard and mouse events
keyboard_events = []
mouse_events = []

# Event to signal termination
exit_event = threading.Event()
esc_pressed = threading.Event()  # Flag to indicate if 'Esc' was pressed

# Keyboard event listener
def on_press(key):
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key)

    # Check if the 'Esc' key is pressed
    if key_str == 'Key.esc':
        exit_event.set()
        esc_pressed.set()
        return False
    else:
        keyboard_events.append(key_str)

keyboard_listener = keyboard.Listener(on_press=on_press)

# Mouse event listener
def on_click(x, y, button, pressed):
    if pressed:
        mouse_events.append(f'Mouse clicked at ({x}, {y}) with {button}')

mouse_listener = mouse.Listener(on_click=on_click)

# Function to switch between opened tabs and windows
def switch_windows(min_wait=2, max_wait=5):
    wait_options = list(range(min_wait, max_wait + 1))
    action_weights = [
        (pyautogui.hotkey, ['ctrl', 'pgdn'], 3),
        (pyautogui.hotkey, ['alt', 'shift', 'tab'], 2),
        (simulate_scroll, [], 3)
    ]

    while not exit_event.is_set():
        wait_time = random.choice(wait_options)
        action_func, action_args, weight = random.choices(action_weights, cum_weights=[sum(w for _, _, w in action_weights[:i+1]) for i in range(len(action_weights))], k=1)[0]
        action_func(*action_args)
        exit_event.wait(wait_time)

def simulate_scroll():
    scroll_amount = random.randint(-1000, 1000)
    try:
        pyautogui.scroll(scroll_amount)
    except pyautogui.FailSafeException:
        pass

# Function to start listeners
def start_listeners():
    keyboard_listener.start()
    mouse_listener.start()

# Function to stop listeners
def stop_listeners():
    keyboard_listener.stop()
    mouse_listener.stop()

# Main function to run the script
def main():
    print('Starting the script...')
    print("Press 'Esc' to stop the script.")
    start_listeners()

    # Get user input for script duration
    duration_minutes = ask_duration()
    if duration_minutes is None:
        print('Invalid duration entered. Exiting.')
        return

    if duration_minutes == -1:
        print('Running indefinitely until "Esc" is pressed.')

    # Start thread for switching windows
    window_thread = threading.Thread(target=switch_windows, daemon=True)
    window_thread.start()

    # Wait for specified duration or 'Esc' key press
    if duration_minutes != -1:
        duration_seconds = duration_minutes * 60
        exit_event.wait(duration_seconds)
        exit_event.set()
    else:
        exit_event.wait()

    # Signal threads to stop
    window_thread.join()
    stop_listeners()

    # Print recorded events
    print(f'Total keyboard buttons pressed: {len(keyboard_events)}')
    print(f'Total mouse clicks recorded: {len(mouse_events)}')
    print('Script finished.')

    if shutdown_system and not esc_pressed.is_set():
        print('Shutting down the system...')
        os.system('shutdown /s /t 1')
    
    sys.exit()

def ask_duration():
    def submit(event=None):
        nonlocal minutes
        try:
            minutes = int(a.get())
        except ValueError:
            minutes = None
        
        global shutdown_system
        shutdown_system = shutdown_var.get()
        
        if minutes is None and shutdown_system:
            messagebox.showwarning("Warning", "Please enter the time duration before submitting.")
        else:
            root.destroy()

    def skip():
        nonlocal minutes
        minutes = -1
        root.destroy()

    def on_shutdown_var_changed(*args):
        if shutdown_var.get():
            skip_button.config(state=DISABLED)
        else:
            skip_button.config(state=NORMAL)

    root = Tk()
    root.title("#kaamnhiruknachahiye")
    root.geometry('400x200')
    root.resizable(False, False)
    
    frame = Frame(root)
    frame.pack(pady=20)

    label = Label(frame, text="Enter duration in minutes:")
    label.grid(row=0, column=0, columnspan=2)

    a = ttk.Entry(frame, width=38)
    a.grid(row=1, column=0, columnspan=2, pady=5)
    a.bind("<Return>", submit)

    shutdown_var = BooleanVar()
    shutdown_var.trace_add("write", on_shutdown_var_changed)
    shutdown_checkbox = ttk.Checkbutton(frame, text="Shutdown system after completion", variable=shutdown_var, cursor="hand2")
    shutdown_checkbox.grid(row=2, column=0, columnspan=2, pady=5)
    
    submit_button = ttk.Button(frame, text="Start", command=submit, cursor="hand2")
    submit_button.grid(row=3, column=0, pady=10)
    
    skip_button = ttk.Button(frame, text="Skip", command=skip)
    skip_button.grid(row=3, column=1, pady=10)

    minutes = None
    shutdown_system = False
    root.mainloop()
    return minutes

if __name__ == '__main__':
    main()
