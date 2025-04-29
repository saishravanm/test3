import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from beacon_detect import run_beacon_detection
import os, datetime

NOTIF_DIR = "notifications"
os.makedirs(NOTIF_DIR, exist_ok = True)

MENU_OPTIONS = [
    "Beacon Detection",
    "Historical Data Viewer",
    "Notifications and Alerts"
]

output_console = None
root = tk.Tk()
root.title("SARSAT GUI")
root.geometry("600x500")

# Global references to dynamic screens
detecting_frame = None
results_frame = None

def flash_window(times=4, interval=150):
    """
    Flash the root window background between its normal color
    and yellow, `times` times, at `interval` ms intervals.
    """
    original = root.cget("bg")
    def _flash(count):
        if count <= 0:
            root.config(bg=original)
            return
        # toggle
        root.config(bg="yellow" if (count % 2) else original)
        root.after(interval, lambda: _flash(count - 1))
    _flash(times * 2)

def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

def show_main_menu():
    global output_console
    clear_screen()

    tk.Label(root, text="Main Menu", font=("Arial", 16)).pack(pady=10)
    for i, option in enumerate(MENU_OPTIONS):
        tk.Button(root, text=option, width=30, height=2, command=lambda idx=i: menu_action(idx)).pack(pady=5)

    output_console = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10)
    output_console.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

def log_to_console(msg):
    def safe_insert():
        if output_console and output_console.winfo_exists():
            output_console.insert(tk.END, msg + "\n")
            output_console.see(tk.END)
    root.after(0, safe_insert)


def show_detecting_screen():
    clear_screen()
    tk.Label(root, text="🔍 Detecting beacon...", font=("Arial",16)).pack(pady=30)
    tk.Button(root, text="Cancel", command=show_main_menu).pack(pady=20)
    threading.Thread(
        target=lambda: run_beacon_detection(
            log=log_to_console,
            callback=lambda d: root.after(0, on_detection_result, d)
        ),
        daemon=True
    ).start()

def show_result_screen(data):
    clear_screen()

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="📡 Beacon Detected!", font=("Arial", 16)).pack(pady=10)

    for key, value in data.items():
        tk.Label(frame, text=f"{key}: {value}", font=("Arial", 12)).pack(pady=2)
    tk.Button(frame, text="Back to Menu", command=show_main_menu).pack(pady=20)


def on_detection_result(data):
    if not data:
        messagebox.showerror("Error", "Failed to decode beacon.")
        return show_main_menu()

    # 1) flash as alert
    flash_window()

    # 2) save to timestamped text file
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{NOTIF_DIR}/{ts}.txt"
    with open(fname, "w") as f:
        for key, val in data.items():
            f.write(f"{key}: {val}\n")

    # 3) show the results screen
    show_result_screen(data)


def show_file_browser():
    clear_screen()
    tk.Label(root, text="Historical Data Viewer", font=("Arial", 14)).pack(pady=10)
    tk.Button(root, text="Back", command=show_main_menu).pack(pady=20)

def show_notification_screen():
    clear_screen()
    tk.Label(root, text="Notifications and Alerts", font=("Arial", 14)).pack(pady=10)

    # List files sorted newest-first
    files = sorted(os.listdir(NOTIF_DIR), reverse=True)
    if not files:
        tk.Label(root, text="(no notifications yet)", font=("Arial", 12)).pack(pady=5)
    else:
        for fname in files:
            tk.Label(root, text=fname, font=("Arial", 12)).pack(anchor="w", padx=20)

    tk.Button(root, text="Back", command=show_main_menu).pack(pady=20)
    
def menu_action(index):
    if index == 0:
        show_detecting_screen()
    elif index == 1:
        show_file_browser()
    elif index == 2:
        show_notification_screen()

show_main_menu()
root.mainloop()
