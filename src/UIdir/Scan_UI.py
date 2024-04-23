import tkinter as tk
from tkinter import ttk
import time
from djitellopy import Tello
import sys
import cv2
from PIL import Image, ImageTk
import os
import numpy as np

demo = True  # Set to True to use the mock drone


class Scan_UI(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.grid_list = []
        self.create_UI()
        self.setup_image_display()

    def setup_image_display(self):
        placeholder = Image.new('RGB', (1000, 1000), 'gray')
        self.imgtk = ImageTk.PhotoImage(image=placeholder)

        self.image_label = tk.Label(self, image=self.imgtk)
        self.image_label.pack(side=tk.LEFT, expand=False, padx=10, pady=10)
        
        # self.image_label = tk.Label(
        #     self, text="Image Display Area", bg="gray", width=400, height=400
        # )
        # self.image_label.pack(side=tk.LEFT, expand=False, padx=10, pady=10)

    def create_UI(self):
        # instance of Drone Table class
        self.drone_table = DroneTable(self)

        # Top frame to hold text box and inputs
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Text box for logging
        self.output_log = tk.Text(top_frame, height=15, width=30)
        self.output_log.pack(side=tk.LEFT, padx=(10, 0), pady=(10, 0), fill=tk.Y)

        scrollbar = tk.Scrollbar(top_frame, command=self.output_log.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.output_log.config(yscrollcommand=scrollbar.set)

        sys.stdout = PrintRedirector(self.output_log)

        input_frame = tk.Frame(top_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.X, padx=(10, 0), pady=(10, 0))

        self.row_frame = tk.Frame(input_frame)
        self.row_frame.pack(pady=10)
        self.row_label = tk.Label(self.row_frame, text="Input number of rows:")
        self.row_label.pack(side=tk.LEFT)
        self.rowInput = tk.Entry(self.row_frame)
        self.rowInput.pack(side=tk.LEFT)

        self.column_frame = tk.Frame(input_frame)
        self.column_frame.pack(pady=10)
        self.column_label = tk.Label(self.column_frame, text="Input number of columns:")
        self.column_label.pack(side=tk.LEFT)
        self.columnInput = tk.Entry(self.column_frame)
        self.columnInput.pack(side=tk.LEFT)

        self.rowInput.focus_set()

        # Confirm and Clear buttons
        self.action_frame = tk.Frame(self)
        self.action_frame.pack(pady=10)
        self.confirm_button = tk.Button(
            self.action_frame, text="Confirm", command=self.drone_table.confirm_action
        )
        self.confirm_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = tk.Button(
            self.action_frame, text="Clear", command=self.drone_table.clear_action
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Frame for left side buttons and right side buttons
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.pack(pady=20)

        # put the "Scan" and "Hover" button on the left side
        self.left_frame = ttk.Frame(self.buttons_frame)
        self.left_frame.pack(side="left", expand=True, fill="both")

        # put the "Start" and "End" button on the middle
        self.middle_frame = ttk.Frame(self.buttons_frame)
        self.middle_frame.pack(side="left", expand=True, fill="both")

        # put the "Up", "Down" and "Next" button on the right side
        self.right_frame = ttk.Frame(self.buttons_frame)
        self.right_frame.pack(side="left", expand=True, fill="both")

        # Start and End Buttons
        self.button3 = ttk.Button(
            self.middle_frame,
            text="Start",
            command=lambda: self.drone_table.button_action("Start"),
        )
        self.button3.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        self.button4 = ttk.Button(
            self.middle_frame,
            text="End",
            command=lambda: self.drone_table.button_action("End"),
        )
        self.button4.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

        # A canvas for the grid
        self.canvas = tk.Canvas(self, width=300, height=300)
        self.canvas.pack(side=tk.LEFT, padx=20, pady=20)
        self.grid_list = []  # List to keep track of the rectangles
        self.grid_size = 30  # Each box will be 30x30 pixels
        for row in range(10):
            for col in range(10):
                rect = self.canvas.create_rectangle(
                    col * self.grid_size,
                    row * self.grid_size,
                    (col + 1) * self.grid_size,
                    (row + 1) * self.grid_size,
                    fill="white",
                )
                self.grid_list.append(rect)


class DroneTable:
    def __init__(self, Scan_UI):
        self.Scan_UI = Scan_UI
        self.rows = 10
        self.cols = 10
        self.interrupt = False
        self.current_row = 0
        self.current_col = 0
        self.direction = 1  # 1 for right, -1 for left
        self.previous_index = None
        self.scan_job = None
        if demo:
            self.drone = MockDrone(Scan_UI)  # Replace with Tello() for actual drone
        else:
            self.drone = Tello()

    def start_drone(self):
        self.drone.connect()
        self.drone.streamon()
        self.drone.takeoff()
        self.drone.move_up(20)
        self.drone.move_forward(40)

    def end_drone(self):
        self.drone.land()
        self.drone.streamoff()
        if self.scan_job:
            self.scan_job = None

    def capture_image(self):

        frame_read = self.drone.get_frame_read()
        dir_name = f"Scan_{time.strftime('%Y%m%d')}"
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        name = f"Screenshot_row{self.current_row}_col{self.current_col-1}_{time.strftime('H%M%S')}.png"
        new_file_path = os.path.join(
            os.path.join(
                os.getcwd(),
                f"Scan_{time.strftime('%Y%m%d')}",
                name,
            )
        )

        cv2.imwrite(new_file_path, frame_read.frame)

        image = Image.open(dir_name + "/" + name)
        resized_img = image.resize((1000, 1000), Image.LANCZOS)

        imgtk = ImageTk.PhotoImage(image=resized_img)
        self.Scan_UI.image_label.imgtk = imgtk
        self.Scan_UI.image_label.configure(image=imgtk)

    def confirm_action(self):
        try:
            # Retrieve the number of rows and columns from the input fields
            self.rows = int(self.Scan_UI.rowInput.get())
            self.cols = int(self.Scan_UI.columnInput.get())

            # Validate the input
            if self.rows < 1 or self.cols < 1 or self.rows > 10 or self.cols > 10:
                print("Invalid input. Rows and columns must be between 1 and 10.")
                if self.rows < 1 or self.rows > 10:
                    self.rows = 10
                if self.cols < 1 or self.cols > 10:
                    self.cols = 10
                return

            self.reset_grid()
            self.current_row = 0
            self.current_col = 0
            self.direction = 1
            self.previous_index = None

        except ValueError:
            print("Invalid input. Please enter a valid number of rows and columns.")

    def clear_action(self):
        self.Scan_UI.rowInput.delete(0, tk.END)
        self.Scan_UI.columnInput.delete(0, tk.END)
        self.Scan_UI.output_log.delete(1.0, tk.END)
        self.interrupt = False

        default_rows = default_cols = 10
        cell_width = self.Scan_UI.canvas.winfo_width() / default_cols
        cell_height = self.Scan_UI.canvas.winfo_height() / default_rows

        for row in range(default_rows):
            for col in range(default_cols):
                rect = self.Scan_UI.canvas.create_rectangle(
                    col * cell_width,
                    row * cell_height,
                    (col + 1) * cell_width,
                    (row + 1) * cell_height,
                    fill="white",
                )
                self.Scan_UI.grid_list.append(rect)
                
        self.Scan_UI.image_label.configure(image=self.Scan_UI.imgtk)

    def button_action(self, button_number):
        print(f"Button {button_number} pressed")

        if button_number == "Start":
            if not self.scan_job:
                print("Starting scan")
                self.reset_scan_state()
                self.scan_grid()
        elif button_number == "End":
            print("Ending")
            self.end_scan()  # Handle ending the scan

    def end_scan(self):
        self.interrupt = True
        if self.scan_job:
            self.scan_job = None
        self.end_drone()
        self.reset_grid()

    def reset_scan_state(self):
        self.interrupt = False
        self.current_row = 0
        self.current_col = 0
        self.direction = 1

    def reset_grid(self):
        self.Scan_UI.canvas.delete("all")
        self.Scan_UI.grid_list = []
        cell_width = self.Scan_UI.canvas.winfo_width() / self.cols
        cell_height = self.Scan_UI.canvas.winfo_height() / self.rows
        for row in range(self.rows):
            for col in range(self.cols):
                rect = self.Scan_UI.canvas.create_rectangle(
                    col * cell_width,
                    row * cell_height,
                    (col + 1) * cell_width,
                    (row + 1) * cell_height,
                    fill="white",
                )
                self.Scan_UI.grid_list.append(rect)

    def scan_grid(self):
        self.start_drone()
        if not self.scan_job:
            self._scan_next_square()

    def _scan_next_square(self):
        if self.interrupt:
            return
        index = self.current_row * self.cols + self.current_col
        if self.previous_index is not None:
            self.Scan_UI.canvas.itemconfig(
                self.Scan_UI.grid_list[self.previous_index], fill="green"
            )
        self.Scan_UI.canvas.itemconfig(self.Scan_UI.grid_list[index], fill="red")
        print(f"Scanning row {self.current_row}, col {self.current_col}")
        self.previous_index = index
        self.current_col += self.direction

        move_distance = 40
        if self.current_col < self.cols and self.current_col >= 0:
            self.drone.move_forward(move_distance)
            self.capture_image()

        if self.current_col >= self.cols or self.current_col < 0:
            self.rotate_drone(move_distance)
            self.current_row += 1
            self.direction *= -1
            self.current_col += self.direction
            if self.current_row >= self.rows:
                self.end_drone()
                return
        self.scan_job = self.Scan_UI.after(750, self._scan_next_square)

    def rotate_drone(self, move_distance=40):

        if self.current_col >= self.cols:
            self.drone.rotate_clockwise(90)
            self.drone.move_forward(move_distance)
            self.capture_image()
            self.drone.rotate_clockwise(90)

        else:
            self.drone.rotate_counter_clockwise(90)
            self.drone.move_forward(move_distance)
            self.capture_image()
            self.drone.rotate_counter_clockwise(90)


class PrintRedirector:
    """A class to redirect prints to the text widget."""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, str):
        self.text_widget.insert(tk.END, str + "\n")
        self.text_widget.see(tk.END)  # Auto-scrolls to the end

    def flush(self):
        pass


class MockFrame:
    def __init__(self, Scan_UI):
        self.frame = self.load_random_image(Scan_UI)

    def load_random_image(self, Scan_UI):
        dir_name = "farm_pics"
        if os.path.exists(dir_name) and os.listdir(dir_name):
            name = np.random.choice(os.listdir(dir_name))
            image_path = os.path.join(dir_name, name)
            image = Image.open(image_path)

            # Convert PIL image to an array suitable for cv2 operations
            image_array = np.array(image)  # Convert PIL image to numpy array

            # Optionally, convert from RGB (PIL) to BGR (OpenCV)
            if image_array.ndim == 3:  # Check if it's a color image
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

            return image_array
        else:
            print("Directory not found or empty, returning a black image")
            # Return a blank black image array as a placeholder
            return np.zeros((400, 400, 3), dtype=np.uint8)


class MockDrone:
    def __init__(self, Scan_UI):
        self.is_streaming = False
        self.battery_level = 100
        self.Scan_UI = Scan_UI  # Keep a reference to the UI for image updates
        self.mock_frame = MockFrame(self.Scan_UI)

    def connect(self):
        print("Connecting to drone... (simulated)")
        self.is_streaming = True

    def streamon(self):
        print("Starting video stream... (simulated)")
        self.is_streaming = True

    def takeoff(self):
        print("Drone taking off... (simulated)")

    def land(self):
        print("Drone landing... (simulated)")

    def move_forward(self, distance):
        print(f"Drone moving forward {distance}cm... (simulated)")
        self.get_frame_read()

    def move_up(self, distance):
        print(f"Drone moving up {distance}cm... (simulated)")

    def rotate_clockwise(self, degrees):
        print(f"Drone rotating clockwise {degrees} degrees... (simulated)")

    def rotate_counter_clockwise(self, degrees):
        print(f"Drone rotating counter-clockwise {degrees} degrees... (simulated)")

    def streamoff(self):
        print("Stopping video stream... (simulated)")
        self.is_streaming = False
    
    def set_video_direction(self, direction):
        print(f"Setting video direction to {direction}... (simulated)")

    def get_frame_read(self):
        self.mock_frame = MockFrame(self.Scan_UI)
        return self.mock_frame

    def capture_image(self):
        frame_read = self.get_frame_read()
        dir_name = "saved_images"
        os.makedirs(dir_name, exist_ok=True)  # Ensure directory exists
        file_name = "captured_image.jpg"
        new_file_path = os.path.join(dir_name, file_name)

        # Use cv2.imwrite to save the frame
        if hasattr(frame_read, "frame"):
            cv2.imwrite(new_file_path, frame_read.frame)
            print("Image saved successfully.")
        else:
            print("No frame data available to save.")
