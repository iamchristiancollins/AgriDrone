import tkinter as tk
from tkinter import ttk
import time


class DroneTable:
    def __init__(self):
        self.rows = 0
        self.cols = 0
        self.mode = None
        self.interrupt = False

    def confirm_action(self):
        try:
            # Retrieve the number of rows and columns from the input fields
            self.rows = int(rowInput.get())
            self.cols = int(columnInput.get())

            # Validate the input
            if self.rows < 1 or self.cols < 1 or self.rows > 10 or self.cols > 10:
                print("Rows and columns must be between 1 and 10.")
                return

            # Reset all cells to white before coloring the specified grid
            for rect in grid_list:
                canvas.itemconfig(rect, fill="white")

            # Color the specified grid cells
            for row in range(self.rows):
                for col in range(self.cols):
                    box_index = row * 10 + col
                    canvas.itemconfig(grid_list[box_index], fill="gray")

        except ValueError:
            print("Please enter valid integers for rows and columns.")

    def clear_action(self):
        # Clear input fields
        rowInput.delete(0, tk.END)
        columnInput.delete(0, tk.END)

        # Reset the grid colors to white for all cells
        for rect in grid_list:
            canvas.itemconfig(rect, fill="white")

    def button_action(self, button_number):
        print(f"Button {button_number} pressed")
        if button_number == "Scan":
            self.mode = "Scan"

        elif button_number == "Hover":
            self.mode = "Hover"
            print("Hovering")

        elif button_number == "Start":
            print("Starting")
            if self.mode == "Scan":
                print("Scanning")
                self.scan_grid()
                DTO = dto() 
                DTO.send_data(queue)

            elif self.mode == "Hover":
                print("Hovering")

        elif button_number == "End":
            print("Ending")
            self.mode = None
            self.interrupt = True

            # Reset user-defined grid cells to gray
            for row in range(self.rows):
                for col in range(self.cols):
                    box_index = row * 10 + col
                    canvas.itemconfig(grid_list[box_index], fill="gray")

            # Return the starting position to the first area in the grid
            if self.rows > 0 and self.cols > 0:
                box_index = 0  # Index of the first area in the grid
                canvas.itemconfig(grid_list[box_index], fill="red")

        elif button_number == "Up":
            print("Moving Up")

        elif button_number == "Down":
            print("Moving Down")

        elif button_number == "Next":
            print("Moving to Next Location")

    def scan_grid(self):
        print(f"Scanning grid of size {self.rows}x{self.cols}")
        previous_box_index = None
        for row in range(self.rows):
            if row % 2 == 0:  # Even row number
                range_cols = range(self.cols)
            else:  # Odd row number
                range_cols = reversed(range(self.cols))
            for col in range_cols:
                if self.interrupt:
                    self.interrupt = False
                    return
                box_index = row * 10 + col
                if previous_box_index is not None:
                    canvas.itemconfig(grid_list[previous_box_index], fill="green")
                canvas.itemconfig(grid_list[box_index], fill="red")
                root.update()  # Update the UI
                time.sleep(1)  # Wait for a second
                previous_box_index = box_index


# Create an instance of the class
drone_table = DroneTable()

root = tk.Tk()
root.title("Drone Table")  # window name
root.geometry("1000x800")  # Window size
# setting background (using an image)
bg_image = tk.PhotoImage(file="image.png")

# Create a label to display the image, and make it cover the entire window
bg_label = tk.Label(root, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Setup row input
row_frame = tk.Frame(root)
row_frame.pack(pady=10)
row_label = tk.Label(row_frame, text="Input number of rows:")
row_label.pack(side=tk.LEFT)
rowInput = tk.Entry(row_frame)
rowInput.pack(side=tk.LEFT)

# Setup column input
column_frame = tk.Frame(root)
column_frame.pack(pady=10)
column_label = tk.Label(column_frame, text="Input number of columns:")
column_label.pack(side=tk.LEFT)
columnInput = tk.Entry(column_frame)
columnInput.pack(side=tk.LEFT)

# Confirm and Clear buttons
action_frame = tk.Frame(root)
action_frame.pack(pady=10)
confirm_button = tk.Button(
    action_frame, text="Confirm", command=drone_table.confirm_action
)
confirm_button.pack(side=tk.LEFT, padx=5)
clear_button = tk.Button(action_frame, text="Clear", command=drone_table.clear_action)
clear_button.pack(side=tk.LEFT, padx=5)

# Frame for left side buttons and right side buttons
buttons_frame = ttk.Frame(root)
buttons_frame.pack(pady=20)

# put the "Scan" and "Hover" button on the left side
left_frame = ttk.Frame(buttons_frame)
left_frame.pack(side="left", expand=True, fill="both")

# put the "Start" and "End" button on the middle
middle_frame = ttk.Frame(buttons_frame)
middle_frame.pack(side="left", expand=True, fill="both")

# put the "Up", "Down" and "Next" button on the right side
right_frame = ttk.Frame(buttons_frame)
right_frame.pack(side="left", expand=True, fill="both")

# Define buttons with a lambda function to pass the button number/name
button1 = ttk.Button(
    left_frame, text="Scan", command=lambda: drone_table.button_action("Scan")
)
button1.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

button2 = ttk.Button(
    left_frame, text="Hover", command=lambda: drone_table.button_action("Hover")
)
button2.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

button3 = ttk.Button(
    middle_frame, text="Start", command=lambda: drone_table.button_action("Start")
)
button3.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

button4 = ttk.Button(
    middle_frame, text="End", command=lambda: drone_table.button_action("End")
)
button4.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

button5 = ttk.Button(
    right_frame, text="Up", command=lambda: drone_table.button_action("Up")
)
button5.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

button6 = ttk.Button(
    right_frame, text="Down", command=lambda: drone_table.button_action("Down")
)
button6.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

button7 = ttk.Button(
    right_frame, text="Next", command=lambda: drone_table.button_action("Next")
)
button7.grid(row=2, column=0, padx=4, pady=4, sticky="ew")

# A canvas for the grid
canvas = tk.Canvas(root, width=300, height=300)
canvas.pack(side=tk.LEFT, padx=20, pady=20)
grid_list = []  # List to keep track of the rectangles
grid_size = 30  # Each box will be 30x30 pixels
for row in range(10):
    for col in range(10):
        rect = canvas.create_rectangle(
            col * grid_size,
            row * grid_size,
            (col + 1) * grid_size,
            (row + 1) * grid_size,
            fill="white",
        )
        grid_list.append(rect)

# Placeholder for video display area
video_display_label = tk.Label(
    root, text="Video Display Area", bg="white", width=70, height=30
)
video_display_label.pack(side=tk.LEFT)

root.mainloop()