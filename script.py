from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pyautogui
from pynput import keyboard, mouse
import threading
import sys
import random
import os
import pystray
from PIL import Image, ImageDraw
import time

pyautogui.FAILSAFE = False

# Variables to store keyboard and mouse events
keyboard_events = []
mouse_events = []

# Events to signal termination and pause
exit_event = threading.Event()
pause_event = threading.Event()

# Global variables
shutdown_system = False
icon = None

# Keyboard event listener
def on_press(key):
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key)
    keyboard_events.append(key_str)

keyboard_listener = keyboard.Listener(on_press=on_press)

# Mouse event listener
def on_click(x, y, button, pressed):
    if pressed:
        mouse_events.append(f'Mouse clicked at ({x}, {y}) with {button}')

mouse_listener = mouse.Listener(on_click=on_click)

# Function to switch between opened tabs and windows
def switch_windows(min_wait=2, max_wait=4):
    wait_options = list(range(min_wait, max_wait + 1))
    action_weights = [
        (pyautogui.hotkey, ['ctrl', 'pgdn'], 3),
        (pyautogui.hotkey, ['alt', 'shift', 'tab'], 2),
        (simulate_scroll, [], 2)
    ]

    while not exit_event.is_set():
        if pause_event.is_set():
            pause_event.wait()
            continue
        
        wait_time = random.choice(wait_options)
        action_func, action_args, weight = random.choices(action_weights, cum_weights=[sum(w for _, _, w in action_weights[:i+1]) for i in range(len(action_weights))], k=1)[0]
        action_func(*action_args)
        exit_event.wait(wait_time)

def simulate_scroll():
    scroll_amount = random.randint(-3000, 3000)
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
    start_listeners()

    duration_minutes = ask_duration()
    if duration_minutes is None:
        print('Invalid duration entered. Exiting.')
        return

    if duration_minutes == -1:
        print('Running indefinitely until stopped.')

    window_thread = threading.Thread(target=switch_windows, daemon=True)
    window_thread.start()

    end_time = None
    if duration_minutes != -1:
        end_time = time.time() + (duration_minutes * 60)

    while not exit_event.is_set():
        if pause_event.is_set():
            time.sleep(1)
            continue

        if end_time and time.time() >= end_time:
            break

        time.sleep(1)

    exit_event.set()
    window_thread.join()
    stop_listeners()

    print(f'Total keyboard buttons pressed: {len(keyboard_events)}')
    print(f'Total mouse clicks recorded: {len(mouse_events)}')
    print('Script finished.')

    if shutdown_system:
        print('Shutting down the system...')
        os.system('shutdown /s /t 1')

def ask_duration():
    def submit(event=None):
        nonlocal minutes
        try:
            minutes = int(a.get())
        except ValueError:
            minutes = None if a.get() else -1  # Run indefinitely if no duration is entered

        global shutdown_system
        shutdown_system = shutdown_var.get()
        
        if minutes is None and shutdown_system:
            messagebox.showwarning("Warning", "Please enter the time duration before submitting.")
        else:
            root.destroy()

    def on_shutdown_var_changed(*args):
        if shutdown_var.get():
            start_button.config(state=DISABLED)
        else:
            start_button.config(state=NORMAL)

    def update_start_button_text(event=None):
        if a.get():
            start_button.config(text="Start")
        else:
            start_button.config(text="Start until stop")

    root = Tk()
    root.title("#SC-BKL?")
    root.geometry('300x200')
    root.resizable(False, False)
    
    frame = Frame(root)
    frame.pack(pady=20)

    label = Label(frame, text="Enter duration in minutes:")
    label.grid(row=0, column=0, columnspan=2)

    a = ttk.Entry(frame, width=38)
    a.grid(row=1, column=0, columnspan=2, pady=5)
    a.bind("<Return>", submit)
    a.bind("<KeyRelease>", update_start_button_text)

    shutdown_var = BooleanVar()
    shutdown_var.trace_add("write", on_shutdown_var_changed)
    shutdown_checkbox = ttk.Checkbutton(frame, text="Shutdown system after completion", variable=shutdown_var, cursor="hand2")
    shutdown_checkbox.grid(row=2, column=0, columnspan=2, pady=5)

    Label(frame, text="--------------------------------------------").grid(row=3, column=0, columnspan=2)
    
    start_button = ttk.Button(frame, text="Start until stop", command=submit, cursor="hand2")
    start_button.grid(row=4, column=0, columnspan=2, pady=10)

    minutes = None
    shutdown_system = False
    root.mainloop()
    return minutes

def create_image():
    # Create an image for the system tray icon
    width = 64
    height = 64
    color1 = "black"
    color2 = "white"

    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2,
    )
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2,
    )

    return image

def on_pause(icon, item):
    pause_event.set()
    icon.update_menu()
    print("Script paused")

def on_resume(icon, item):
    pause_event.clear()
    icon.update_menu()
    print("Script resumed")

def setup_tray_icon():
    global icon
    icon = pystray.Icon("test_icon")

    def get_menu_items():
        return (
            pystray.MenuItem("Resume" if pause_event.is_set() else "Pause", 
                             on_resume if pause_event.is_set() else on_pause),
            pystray.MenuItem("Exit", on_quit)
        )

    icon.menu = pystray.Menu(get_menu_items)
    icon.icon = create_image()
    icon.title = "excel-tech"
    icon.run()

def on_quit(icon, item):
    icon.stop()
    exit_event.set()

if __name__ == '__main__':
    tray_thread = threading.Thread(target=setup_tray_icon)
    tray_thread.start()
    main()
    if icon:
        icon.stop()
    sys.exit(0)