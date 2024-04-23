import tkinter as tk
from tkinter import ttk
import time
from src.UIdir.Scan_UI import Scan_UI
from src.UIdir.Hover_UI import Hover_UI
import sys


class MainUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drone Table")
        self.geometry("1000x800")
        self.original_stdout = sys.stdout

        self.buttonFrame = tk.Frame(self)
        self.buttonFrame.pack(pady=20)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Function to reload canvas with modules suitable for "Scan" mode
        def scan_select():
            self.clear_canvas()
            self.load_scan_mode()

        # Function to reload canvas with modules suitable for "Hover" mode
        def hover_select():
            self.clear_canvas()
            self.load_hover_mode()

        self.R1 = tk.Radiobutton(
            self.buttonFrame, text="Scan", value=2, command=scan_select
        )
        self.R1.pack(side=tk.LEFT, padx=10)
        self.R1.select()

        self.R2 = tk.Radiobutton(
            self.buttonFrame, text="Hover", value=1, command=hover_select
        )
        self.R2.pack(side=tk.LEFT, padx=10)

        self.canvas = tk.Frame()
        # Defalt mode (Scan)
        self.HoverUI = None
        self.load_scan_mode()

    def clear_canvas(self):
        # Method to clear canvas content (if needed)
        sys.stdout = self.original_stdout
        if self.ScanUI:
            self.ScanUI.destroy()
        if self.HoverUI:
            self.HoverUI.destroy()

    def load_scan_mode(self):
        # Method to load canvas with modules suitable for "Scan" mode
        # Example: self.grid_maker = Grid_Maker(self)
        #          self.grid_maker.pack()
        print("Loading Scan mode")
        self.ScanUI = Scan_UI(self)
        self.ScanUI.pack()

    def load_hover_mode(self):
        # Method to load canvas with modules suitable for "Hover" mode
        # Example: self.buttons = Button_Panel(self)
        #          self.buttons.pack()
        print("Loading Hover mode")
        self.HoverUI = Hover_UI(self)
        self.HoverUI.pack()

    def on_close(self):
        print("Closing application...")
        sys.stdout = self.original_stdout
        self.destroy()


if __name__ == "__main__":
    app = MainUI()
    app.mainloop()
