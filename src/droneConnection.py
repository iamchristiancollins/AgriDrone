import socket
import threading
import numpy as np
import cv2
import PIL.Image, PIL.ImageTk
from djitellopy import Tello



class DroneConnection:
    def __init__(self, video_callback=None):
        self.host = ''
        self.port = 9000
        self.locaddr = (self.host, self.port)
        self.tello_address = ('192.168.10.1', 8889)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.locaddr)
        
        self.video_port = 11111
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_socket.bind(('', self.video_port))
        
        self.running = True
        
        self.recvThread = threading.Thread(target=self.recv)
        self.recvThread.daemon = True
        self.recvThread.start()
        
        self.video_thread = threading.Thread(target=self.video_recv)
        self.video_thread.daemon = True
        self.video_thread.start()
        

    def send_command(self, command):
        try:
            self.sock.sendto(command.encode('utf-8'), self.tello_address)
            print(f"Sent command: {command}")
        except Exception as e:
            print(f"Failed to send command {command}: {e}")

    def recv(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(1518)
                print(data.decode('utf-8'))
            except Exception as e:
                if self.running:
                    print("Reception error:", e)
                break
            
            
    def video_recv(self):
        """ Handle incoming video stream data. """
        while self.running:
            try:
                data, _ = self.video_socket.recvfrom(2048)  #  _ is used to ignore the sender’s address which is not needed.
                frame = self.decode_video_stream(data)
                if frame is not None:
                    self.video_frame_handler(frame)
            except Exception as e:
                print("Video reception error:", e)
                break
            
            
    def decode_video_stream(self, data):
        """ Decode video stream data and return a frame. """
        try:
            video_packet = np.frombuffer(data, dtype=np.uint8) # convert raw bytes into numpy array of unsigned 8-bit integers
            frame = cv2.imdecode(video_packet, cv2.IMREAD_COLOR) # decode into image frame
            return frame
        except Exception as e:
            print("Failed to decode video frame:", e)
            return None
        
        
    def video_frame_handler(self, frame):
        """ Process or display the decoded frame. Placeholder for custom handling. """
        if self.video_callback:
            self.video_callback(frame)
        
    def update_ui(self, frame):
        image = PIL.ImageTk.PhotoImage(image=frame)
        self.video_label.configure(image=image)
        self.video_label.image = image

    def close(self):
        self.running = False
        self.sock.close()
        self.recvThread.join()
        
    
    def check_status(self):
        self.send_command('battery?')

        
        



# #
# # Tello Python3 Control Demo (Edited)
# #
# # http://www.ryzerobotics.com/
# #
# # 1/1/2018


# import threading 
# import socket
# import sys
# import time


# # You do not need to make any edits to this program to 
# # connect to the drone. This will work for all of them.
# #
# # I left a brief guide to getting a drone connected at the bottom of the 
# # program to help if you are having any issues.
# #
# # Feel free to implement this in your software.



# # Inputting the local address. You do not need to change this.
# host = ''
# port = 9000
# locaddr = (host,port) 


# # Creating the socket that will connect to the drone.
# droneSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# # Saving of the drones IP/UDP Port Numbers. Commands are will be sent to this port.
# tello_address = ('192.168.10.1', 8889)


# # Connecting our socket to the drone:
# droneSocket.bind(locaddr)

# # From this point on, your program can communicate and send commands to your drone.
# # A few different commands will be printed when the program is run.


# print ('\r\n\r\nTello Python3 Demo.\r\n')
# print ('Tello commands:\ncommand takeoff land flip forward back left right\nup down cw ccw speed speed?\r\n')
# print ('To put the drone into sdk mode, send the following input: command \r\n')
# print ('To sever the connection, send the following input: end \r\n')

# def recv():
#     count = 0
    
#     while True: 

#         try:
#             data, server = droneSocket.recvfrom(1518)
#             print(data.decode(encoding="utf-8"))

#         except Exception:
#             print ('\nExit . . .\n')
#             break


# recvThread = threading.Thread(target=recv)
# recvThread.start()

# while True: 
#     try:
#         msg = input("");

#         if not msg:
#             break  

#         if 'end' in msg:
#             print ('...')
#             droneSocket.close()  
#             break

#         msg = msg.encode(encoding="utf-8") 
#         sent = droneSocket.sendto(msg, tello_address)

#     except KeyboardInterrupt:
#         print ('\n . . .\n')
#         droneSocket.close()  
#         break




# # To connect the program to a tello drone:

# # 1.
# # The Tello drone has two unique identifiers, located underneath the battery.
# # The WIFI SSID is the only one you need to look for.
# #
# # It will look something like:
# # WIFI: TELLO-58A55
# #
# # Make note of your drones WIFI SSID. You will connect your computer to this later. 


# # 2. 
# # On the side of the drone there is a small button. 
# # Press it once and the drone will turn on, starting a series of blinking lights on the
# # front of the drone.
# #
# # The lights indicate the current state of the drone, you can reference page 6 of
# # the user manual to determine their meaning.
# # 
# # If the drone is charged then it should settle on a yellow blinking light. 
# # In this state, you can connect to the drone.


# # 3. 
# # You will need to connect the computer running the program to the drone, 
# # the same way you would connect your computer to a wifi network.
# #
# # Open up your WIFI settings and if your drone is on and outputting a signal, 
# # the WIFI SSID (e.g. TELLO-58A55) will appear, as though it were any other WIFI network.
# # 
# # Connect to this signal.


# # 4. 
# # At this point, you can run this program to connect to the drone.
# #
# # Once running, this 
# # To put the drone into SDK mode, send it: "command".
# #
# # This allows the drone to accept other commands.
# #
# # You can find the full list of commands the drones can accept
# # on the Tello SDK user guide
# # 
# # To sever your connection, send "end".