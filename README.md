# Python-Command-Control-Server--GUI
A multithreaded client-server application built in Python that allows a GUI-based server to send commands to connected clients and display their output in real time.


(I) Features:
- Multiple client support
- Real-time command execution
- Thread-safe GUI updates
- Automatic connection/disconnection detection
- Clean shutdown handling
- Structured locking to prevent race conditions


(II) Architecture Overview:

1️) Server GUI Script:

- Built with Tkinter
- Displays connected clients
- Sends commands to selected client
- Displays client output
- Uses after() to safely update GUI from worker threads

2️) Server Backend (Networking Layer):

- Listens for incoming client connections
- Manages connected clients
- Spawns a thread per client to receive output
- Uses thread locks for shared data structures

3️) Client Script:

- Connects to the server using provided IP and port
- Sends username@hostname upon connection
- Executes received commands
- Sends command output back to server


(III) Requirements:

- Python 3.10+ recommended
- Tkinter (usually included with Python)


(IV) Setup Instructions

- In the client script change the variable to your desired server IP or domain name
- OPTIONAL: The scripts work on port 1234 and with a total of 5 clients by default; if you want to change any of these parameters, follow this guideline:

(1) In the client script change SERVER_PORT to your desired server port

(2) In "Final Project-GUI" under the variable "server" (under __main__) add the proper parameters (instead of: server = CommandServer(); make it: server = CommandServer("10.0.0.1",9993,10), for example).

- Run "Final Project-GUI" on the server device
- Run "Final_Project_Client" on the client device/s


(V) How to use?
- All commands are acceptable depending on the OS
- To clean the command output and entry field type "cls", select any client and press "Execute"
- To disconnect a client, select it, write the command "exit" followed by the "Execute" button


* Commands must be written exactly as shown (case-sensitive).



Disclaimer:
This project is for educational purposes only.
I do not take responsibility for any misuse.


FYI: The commands and output are sent over the network in a NON-ENCRYPTED channel, you have been warned.
