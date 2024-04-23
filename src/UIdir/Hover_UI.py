import tkinter as tk
from tkinter import ttk
import time
from djitellopy import Tello
import queue
import sys
import cv2
from PIL import Image, ImageTk
import threading
import os
import numpy as np

demo = True  # Set to true to use the mock drone

class Hover_UI(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.create_UI()
        self.create_button_grid()
        self.setup_image_display()
        self.tello = Tello()

    def create_UI(self):
        # instance of Drone Table class
        self.drone_table = DroneTable(self)

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

        # Buttons
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

        self.button5 = ttk.Button(
            self.middle_frame,
            text="Up",
            command=lambda: self.drone_table.button_action("Up"),
        )
        self.button5.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        self.button6 = ttk.Button(
            self.middle_frame,
            text="Down",
            command=lambda: self.drone_table.button_action("Down"),
        )
        self.button6.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        self.button7 = ttk.Button(
            self.middle_frame,
            text="Next",
            command=lambda: self.drone_table.button_action("Next"),
        )
        self.button7.grid(row=0, column=2, padx=4, pady=4, sticky="ew")

        # A canvas for the grid

    def create_button_grid(self):
        self.canvas = tk.Canvas(self, width=300, height=300)
        self.canvas.pack(side=tk.LEFT, padx=20, pady=20)
        self.grid_list = []  # List to keep track of the buttons
        self.grid_size = 30  # Each box will be 30x30 pixels
        for row in range(10):
            for col in range(10):
                button = tk.Button(
                    self.canvas,
                    width=1,  # Adjust width as needed
                    height=1,  # Adjust height as needed
                    command=lambda row=row, col=col: self.drone_table.button_grid_action(
                        row, col
                    ),
                )

                self.canvas.create_window(
                    col * self.grid_size + self.grid_size // 2,
                    row * self.grid_size + self.grid_size // 2,
                    window=button,
                    anchor="c",
                )
                self.grid_list.append(button)

    def setup_image_display(self):
        self.image_label = tk.Label(
            self, text="Image Display Area", bg="black", width=400, height=400
        )
        self.image_label.pack(side=tk.LEFT, expand=False, padx=10, pady=10)


class DroneTable:
    def __init__(self, Hover_UI):
        self.Hover_UI = Hover_UI
        self.rows = 0
        self.cols = 0
        self.mode = None
        self.interrupt = False
        self.hover_job = None
        self.current_row = 0
        self.current_col = 0
        self.direction = 1  # 1 for right, -1 for left
        self.current_selection = False
        self.coordinates_queue = queue.Queue()
        self.color_change_done = threading.Event()  # Add this line
        if demo:
            self.drone = MockDrone()  # Replace with Tello() for actual drone
        else:
            self.drone = Tello()

    def start_drone(self):
        self.drone.connect()
        self.drone.takeoff()
        time.sleep(5)

    def end_drone(self):
        self.drone.send_command("command")
        self.drone.send_command("land")
        if self.hover_job:
            self.hover_job = None

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
        self.Hover_UI.image_label.imgtk = imgtk
        self.Hover_UI.image_label.configure(image=imgtk)

    def button_action(self, button_number):
        print(f"Button {button_number} pressed")

        if button_number == "Start":
            if not self.hover_job:
                print("starting hover")
                self.reset_hover_state()
                self.hover_grid()

        elif button_number == "End":
            print("Ending")
            self.interrupt = True
            self.current_row = 0
            self.current_col = 0

            for button in self.Hover_UI.grid_list:
                button.destroy()

                # Clear the grid list
            self.Hover_UI.grid_list.clear()

            # Create new buttons for the specified grid size
            for row in range(10):
                for col in range(10):
                    button = tk.Button(
                        self.Hover_UI.canvas,
                        width=1,  # Adjust width as needed
                        height=1,  # Adjust height as needed
                        command=lambda row=row, col=col: self.button_grid_action(
                            row, col
                        ),
                    )
                    self.Hover_UI.grid_list.append(button)

                    self.Hover_UI.canvas.create_window(
                        col * self.Hover_UI.grid_size + self.Hover_UI.grid_size // 2,
                        row * self.Hover_UI.grid_size + self.Hover_UI.grid_size // 2,
                        window=button,
                        anchor="c",
                    )

            if self.hover_job:
                self.scan_job = None
            self.end_drone()
            self.coordinates_queue = queue.Queue()
            self.interrupt = False

        elif button_number == "Up":
            print("Increasing height")
            self.Hover_UI.tello.drone.move_up(20)  # Move up by 20 cm

        elif button_number == "Down":
            print("Decreasing height")
            self.Hover_UI.drone.tello.move_down(20)  # Move down by 20 cm

        elif button_number == "Next":
            if not self.coordinates_queue.empty():
                print("Moving to Coordinate: " + str(self.coordinates_queue.queue[0]))
                self.current_selection = False
                self.color_change_done.wait()  # Add this line
                self.hover_grid()
            else:
                self.current_row = 0
                self.current_col = 0
                print("Enter a coordinate first")

    def reset_hover_state(self):
        self.interrupt = False
        self.current_row = 0
        self.current_col = 0
        self.direction = 1

    def button_grid_action(self, row, col):
        print("Recieved button grid press from Row: " + str(row) + " Col: " + str(col))
        self.Hover_UI.grid_list[row * 10 + col].configure(
            highlightthickness=0, highlightbackground="red"
        )
        self.coordinates_queue.put((row, col))
        print("Coordinates Queue: " + str(self.coordinates_queue.queue))

    def hover_grid(self):
        print(f"Going to location {self}, on a grid of size {self.rows}x{self.cols}")

        coordinates = self.coordinates_queue.get()
        row = coordinates[0]
        column = coordinates[1]

        self.current_selection = True
        self.threadaction = threading.Thread(
            target=self.change_button_color, args=(row, column), daemon=True
        )
        self.threadaction.start()

        row_diff = row - self.current_row
        col_diff = column - self.current_col

        # Move to the correct row
        for _ in range(abs(row_diff)):
            if row_diff > 0:
                # self.Hover_UI.tello.drone.move_forward(20)  # Move forward by 20 cm
                print("simulate forward movement")
            else:
                # self.Hover_UI.drone.tello.move_backward(20)  # Move backward by 20 cm
                print("simluate backward movement")

        # Rotate and move to the correct column
        # self.Hover_UI.drone.tello.rotate_cw(90)  # Rotate clockwise by 90 degrees
        print("simulate clockwise rotation")
        for _ in range(abs(col_diff)):
            if col_diff > 0:
                # self.Hover_UI.drone.tello.move_forward(20)  # Move forward by 20 cm
                print("simulate forward movement")
            else:
                # self.Hover_UI.drone.tellomove_backward(20)
                print("simulate backward movement")  # Move backward by 20 cm
        # self.Hover_UI.tellodrone.rotate_ccw(
        #    90
        # )   Rotate counter-clockwise by 90 degrees
        print("simulate counter-clockwise rotation")

        # Update the current position
        self.current_row = row
        self.current_col = column
        self.capture_image()

    def change_button_color(self, row, col):
        while self.current_selection:  # Check the condition variable in the while loop
            self.Hover_UI.grid_list[row * 10 + col].configure(
                highlightthickness=0, highlightbackground="green"
            )
            time.sleep(1)  # Wait for 1 second
            self.Hover_UI.grid_list[row * 10 + col].configure(
                highlightthickness=0, highlightbackground="cyan"
            )
            time.sleep(1)  # Wait for 1 second
            if self.current_col != col or self.current_row != row:
                break

        self.color_change_done.set()
        self.Hover_UI.grid_list[row * 10 + col].configure(
            highlightthickness=0, highlightbackground="green"
        )


class MockDrone:
    def __init__(self):
        self.is_streaming = False
        self.battery_level = 100

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

    def move_up(self, distance):
        print(f"Drone moving up {distance}cm... (simulated)")

    def rotate_clockwise(self, degrees):
        print(f"Drone rotating clockwise {degrees} degrees... (simulated)")

    def rotate_counter_clockwise(self, degrees):
        print(f"Drone rotating counter-clockwise {degrees} degrees... (simulated)")

    def streamoff(self):
        print("Stopping video stream... (simulated)")
        self.is_streaming = False

    def get_frame_read(self):
        return MockFrame()


class MockFrame:
    def __init__(self):
        # Load a sample image or just simulate a blank image
        self.frame = (
            cv2.imread("sample_image.jpg")
            if os.path.exists("sample_image.jpg")
            else np.random.randint(0, 256, (600, 800, 3), dtype=np.uint8)
        )
