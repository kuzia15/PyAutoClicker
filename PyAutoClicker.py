import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import keyboard
import pyautogui
import sys
from pynput import mouse

class PyAutoClicker:
    def __init__(self, penis):
        self.root = penis
        self.root.title("PyAutoClicker")
        self.root.geometry("400x420")
        self.root.resizable(False, False)

        self.running = False
        self.click_thread = None
        self.click_type = "left"
        self.use_fixed_position = False
        self.click_position = None
        self.interval = {"mins": 0, "secs": 0, "ms": 100}
        self.hotkey = "F6"

        self.build_gui()
        self.start_hotkey_listener()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def build_gui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)

        self.build_click_frame(main_frame)
        self.build_interval_frame(main_frame)
        self.build_position_frame(main_frame)
        self.build_hotkey_frame(main_frame)
        self.build_buttons(main_frame)
        self.build_status_bar(main_frame)

    def build_click_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Mouse Button")
        frame.pack(fill='x', pady=5)

        self.click_var = tk.StringVar(value=self.click_type)
        ttk.Radiobutton(frame, text="Left Click", variable=self.click_var, value="left").grid(row=0,column=0,padx=5,pady=2)
        ttk.Radiobutton(frame, text="Right Click", variable=self.click_var, value="right").grid(row=0,column=1,padx=5,pady=2)
        ttk.Radiobutton(frame, text="Double Click", variable=self.click_var, value="double").grid(row=0,column=2,padx=5,pady=2)

    def build_interval_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Click Interval")
        frame.pack(fill='x', pady=5)

        ttk.Label(frame, text="mins:").grid(row=0,column=0)
        self.mins_var = tk.IntVar(value=self.interval["mins"])
        ttk.Spinbox(frame, from_=0, to=59, width=5, textvariable=self.mins_var).grid(row=0,column=1)

        ttk.Label(frame, text="secs:").grid(row=0,column=2)
        self.secs_var = tk.IntVar(value=self.interval["secs"])
        ttk.Spinbox(frame, from_=0, to=59, width=5, textvariable=self.secs_var).grid(row=0,column=3)

        ttk.Label(frame, text="ms:").grid(row=0,column=4)
        self.ms_var = tk.IntVar(value=self.interval["ms"])
        ttk.Spinbox(frame, from_=0, to=999, width=5, textvariable=self.ms_var).grid(row=0,column=5)

    def build_position_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Click Position")
        frame.pack(fill='x', pady=5)

        self.position_var = tk.BooleanVar(value=self.use_fixed_position)
        ttk.Checkbutton(frame, text="Use fixed position", variable=self.position_var, command=self.toggle_position).grid(row=0,column=0,columnspan=2, sticky='w', pady=5)

        ttk.Label(frame, text="X:").grid(row=1,column=0)
        self.x_var = tk.StringVar()
        self.x_entry = ttk.Entry(frame, textvariable=self.x_var, width=8, state='disabled')
        self.x_entry.grid(row=1,column=1)

        ttk.Label(frame, text="Y:").grid(row=1,column=2)
        self.y_var = tk.StringVar()
        self.y_entry = ttk.Entry(frame, textvariable=self.y_var, width=8, state='disabled')
        self.y_entry.grid(row=1,column=3)

        ttk.Button(frame, text="Pick Location", command=self.pick_position).grid(row=1,column=4, padx=5)

    def build_hotkey_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Hotkey Control")
        frame.pack(fill='x', pady=5)

        ttk.Label(frame, text="Toggle Hotkey:").grid(row=0,column=0)
        self.hotkey_var = tk.StringVar(value=self.hotkey)
        hotkey_combo = ttk.Combobox(frame, textvariable=self.hotkey_var, width=5, state='readonly')
        hotkey_combo['values'] = ('F6','F7','F8','F9','F10','F11','F12')
        hotkey_combo.grid(row=0,column=1, padx=5, pady=5)

    def build_buttons(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=10)

        self.start_btn = ttk.Button(frame, text="Start Clicking", command=self.start_clicking, width=15)
        self.start_btn.pack(side='left', padx=10)

        self.stop_btn = ttk.Button(frame, text="Stop Clicking", command=self.stop_clicking, width=15, state='disabled')
        self.stop_btn.pack(side='right', padx=10)

    def build_status_bar(self, parent):
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(parent, textvariable=self.status_var, relief='sunken', anchor='center').pack(fill='x', pady=5, ipady=3)

    def toggle_position(self):
        state = 'normal' if self.position_var.get() else 'disabled'
        self.x_entry.config(state=state)
        self.y_entry.config(state=state)
        self.x_var.set("")
        self.y_var.set("")

    def pick_position(self):
        self.status_var.set("Click on desired position...")
        self.root.withdraw()

        def on_click(x, y, button, pressed):
            if pressed:
                self.click_position = (x, y)
                self.x_var.set(str(x))
                self.y_var.set(str(y))
                listener.stop()
                self.root.deiconify()
                self.status_var.set(f"Position set: {x}, {y}")

        listener = mouse.Listener(on_click=on_click)
        listener.start()

    def start_clicking(self):
        if self.running: return

        self.click_type = self.click_var.get()
        self.use_fixed_position = self.position_var.get()
        self.hotkey = self.hotkey_var.get()
        self.interval = {"mins": self.mins_var.get(),"secs": self.secs_var.get(),"ms": self.ms_var.get()}
        total_seconds = self.interval["mins"]*60 + self.interval["secs"] + self.interval["ms"]/1000

        if total_seconds <= 0:
            messagebox.showerror("Error","Interval must be >0")
            return

        if self.use_fixed_position:
            try:
                self.click_position = (int(self.x_var.get()), int(self.y_var.get()))
            except:
                messagebox.showerror("Error","Invalid coordinates")
                return

        self.running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        status = f"Clicking ({self.click_type}) every "
        if self.interval["mins"]>0: status += f"{self.interval['mins']}m "
        if self.interval["secs"]>0: status += f"{self.interval['secs']}s "
        if self.interval["ms"]>0: status += f"{self.interval['ms']}ms"
        if self.use_fixed_position: status += f" at {self.click_position}"
        self.status_var.set(status)

        self.click_thread = threading.Thread(target=self.click_loop, args=(total_seconds,), daemon=True)
        self.click_thread.start()

    def stop_clicking(self):
        if not self.running: return
        self.running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_var.set("Clicking stopped")

    def click_loop(self, interval):
        while self.running:
            try:
                if self.use_fixed_position and self.click_position:
                    pyautogui.moveTo(*self.click_position)
                if self.click_type=="left": pyautogui.click()
                elif self.click_type=="right": pyautogui.click(button='right')
                elif self.click_type=="double": pyautogui.doubleClick()
                time.sleep(interval)
            except: self.running=False; break

    def start_hotkey_listener(self):
        threading.Thread(target=self.hotkey_loop, daemon=True).start()

    def hotkey_loop(self):
        while True:
            try:
                if keyboard.is_pressed(self.hotkey):
                    self.stop_clicking() if self.running else self.start_clicking()
                    time.sleep(0.5)
                time.sleep(0.01)
            except: break

    def close_app(self):
        self.running = False
        self.root.destroy()
        sys.exit()


if __name__=="__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', font=('Arial',10), padding=5)
    style.configure('TLabel', font=('Arial',9))
    style.configure('TLabelFrame', font=('Arial',10,'bold'))
    style.configure('TCombobox', font=('Arial',9))
    PyAutoClicker(root)
    root.mainloop()