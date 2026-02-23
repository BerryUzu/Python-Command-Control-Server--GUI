import socket
import threading
import tkinter as tk


class CommandServer(object):
    def __init__(self, server_ip='0.0.0.0', server_port=1234, max_clients=5):
        """

        :param server_ip: localhost, unless specified differently in the creation of an instance
        :param server_port: 1234, unless specified differently in the creation of an instance
        :param max_clients: 5 connections, unless specified differently in the creation of an instance

        :self.clients: a list that contains the client objects
        :self.addresses: a list that contains the server IP addresses and remote ports
        :self.usernames: a dictionary; key: client socket object, value: username@hostname

        3 different lock variables; each for a different data structure to prevent race conditions

        """

        self.SERVER_IP = server_ip
        self.SERVER_PORT = server_port
        self.NUMBER_OF_CLIENTS = max_clients

        self.clients = []
        self.addresses = []
        self.usernames = {}

        self.clients_lock = threading.Lock()
        self.addresses_lock = threading.Lock()
        self.usernames_lock = threading.Lock()


        self.running = True
        self.server_socket = None

    def button_clicked(self, entry_widget, output_box, selected_client):
        """
        :param entry_widget: takes data from the entry_widget
        :param output_box: outputs the stdout or stderr to the output_box
        :param selected_client: The chosen client from clients (the endpoint user chose via the listbox)
        :return: None

        Retrieve the data from the entry prompt; if "cls" then deletes the entry and output_box fields; otherwise sends the command to the client and deletes the contents of the entry field

        """
        command = entry_widget.get().strip()
        if not command:
            return

        # CLS command
        if command == 'cls':
            output_box.config(state="normal")
            output_box.delete("1.0", tk.END)
            output_box.config(state="disabled")
            entry_widget.delete(0, "end")
            return

        try:
            selected_client.sendall(command.encode())
        except:
            return

        entry_widget.delete(0, "end")

    def handle_connections(self, listbox, output_box):
        """
        Creation of the server socket, listening and accepting connections.
        After a connection is established, using the locks we append to the data structures the provided data: username+hostname, client objects and addr

        After all of that the lambda function inserts the IP and remote port of the client to the listbox.

        The thread of the method receive_output runs here
        :param listbox:
        :param output_box:
        :return:
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.server_socket.listen(self.NUMBER_OF_CLIENTS)
        self.server_socket.settimeout(2)

        print(f"Server listening on {self.SERVER_IP}:{self.SERVER_PORT}...")

        while self.running:
            try:
                client_sock, addr = self.server_socket.accept() #accept connections
            except socket.timeout:
                continue # just go back to the top of the loop
            except OSError:
                break # this happens if server_socket is closed

            print(f"Connected to {addr}")

            try:
                username_and_hostname = client_sock.recv(2048).decode().strip() #Accept username and hostname
                output_box.after(0,lambda u=username_and_hostname, a=addr: self.insert_output(output_box, text=f"A new connection from [{u}]:{a}!\n"))
            except:
                client_sock.close()
                continue

            with self.clients_lock:
                self.clients.append(client_sock)

            with self.usernames_lock:
                self.usernames[client_sock] = username_and_hostname

            with self.addresses_lock:
                self.addresses.append(addr)

            display_text = f"{addr[0]}:{addr[1]}"
            listbox.after(0, lambda dt=display_text: listbox.insert(tk.END, dt))

            threading.Thread(
                target=self.receive_output,
                args=(client_sock, addr, username_and_hostname, output_box, listbox),
                daemon=True
            ).start()

    def shutdown(self):
        """
        Gracefully shuts down the server:
        - stops accepting new connections
        - closes all client sockets
        - closes the server socket

        Utilized by the on_close method from the CommandServerGUI class
        """
        print("Shutting down server...")

        self.running = False  # stop the main loop of handle_connections, so as to not accept any new connections at this time

        # Close all client connections
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()  #Remove all objects from the clients list

        # Close the main server socket
        try:
            if self.server_socket:
                self.server_socket.close()
        except:
            pass

    def receive_output(self, client, addr, username, output_box, client_listbox):
        """
        Receives command output or error output from the client and inserts it to the output box widget
        :param client: Client socket object
        :param addr: Remote client address
        :param username: contains username@hostname
        :param output_box: output_box
        :param client_listbox: client_listbox
        :return: None
        """

        def remove_client_from_listbox():
            for i in range(client_listbox.size()):
                if client_listbox.get(i) == f"{addr[0]}:{addr[1]}":
                    client_listbox.delete(i)
                    break

        while True:
            try:
                data = client.recv(4096)

                if not data: #No data (None); connection terminated; notifies via the output_box; Triggers typically when we enter the command "exit"
                    output_box.after(0, lambda u=username, a=addr: self.insert_output(output_box,text=f"You have disconnected from [{u}]:{a}\n"))

                    with self.clients_lock:
                        if client in self.clients:
                            self.clients.remove(client)

                    with self.usernames_lock:
                        self.usernames.pop(client, None)

                    with self.addresses_lock:
                        if addr in self.addresses:
                            self.addresses.remove(addr)

                    try:
                        client.close()
                    except:
                        pass

                    client_listbox.after(0, remove_client_from_listbox)
                    break

                message = f"[{username}]:{addr}> {data.decode(errors='ignore')}\n"   #Decoding the command output and inserting it to the output box
                output_box.after(
                    0,
                    lambda m=message: self.insert_output(output_box, m)
                )

            except (ConnectionResetError, OSError): #On exception errors (if the client script abruptly stopped: computer turned off or the script was stopped manually
                output_box.after(
                    0,
                    lambda u=username, a=addr: self.insert_output(
                        output_box,
                        text=f"Connection lost with [{u}]:{a}\n"
                    )
                )

                with self.clients_lock:
                    if client in self.clients:
                        self.clients.remove(client)

                with self.usernames_lock:
                    self.usernames.pop(client, None)

                with self.addresses_lock:
                    if addr in self.addresses:
                        self.addresses.remove(addr)

                try:
                    client.close()
                except:
                    pass

                client_listbox.after(0, remove_client_from_listbox)
                break

    def insert_output(self, output_box, text):
        """
        Inserts command output to the Output_box widget; called in "remove_client_from_listbox" method top notify if clients disconnected and to write command output
        :param output_box:
        :param text:
        :return:
        """
        output_box.config(state="normal")
        output_box.insert("end", text)
        output_box.config(state="disabled")
        output_box.see("end")