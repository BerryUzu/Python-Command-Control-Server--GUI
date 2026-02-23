import tkinter as tk
import threading
from Final_Project_Commanding_Server import CommandServer  # Imported the class CommandServer


class CommandServerGUI(object):
    """
    The GUI code using Tkinter
    """
    def __init__(self, root, server):
        """
        The __init__ function defines internal class variables and executes 4 methods that comprise the GUI elements

        :param root: tk.Tk()- The main application window
        :param server: The instance of the class CommandServer()
        """

        self.root = root
        self.server = server
        self.root.title("Commanding Server")
        self.root.geometry("900x500")
        self.root.iconbitmap(r"Puppeteer.ico")

        self.setup_main_layout()
        self.create_frames()
        self.create_widgets()
        self.place_widgets()

        # Bind the X button to trigger graceful shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_close) #Instead of just closing the mainloop() it triggers the self.on_close method

    def setup_main_layout(self):
        """
        The setup_main_layout function sets up the main window layout in case of a resize
        :return: None
        """
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def create_frames(self):
        """
        The create_frames function creates the frames where different widgets reside
        :self.top_frame: A child frame of the main frame tk.Tk(); contains the Entry and button widgets
        :self.body_frame: A child frame of the main frame tk.Tk(); contains the two frames: self.left_frame and self.right_frame
        :self.left_frame: A child frame of the self.body_frame; contains listbox of clients
        :self.right_frame: A child frame of the self.body_frame; contains text (output box for commands)
        :return: None
        """
        self.top_frame = tk.Frame(self.root)
        self.top_frame.grid(row=0, column=0, sticky="ew")

        self.body_frame = tk.Frame(self.root)
        self.body_frame.grid(row=1, column=0, sticky="nsew")

        self.body_frame.grid_rowconfigure(0, weight=1)
        self.body_frame.grid_columnconfigure(1, weight=1)

        self.left_frame = tk.Frame(self.body_frame, width=200)
        self.left_frame.grid(row=0, column=0, sticky="ns")
        self.left_frame.grid_propagate(False)

        self.right_frame = tk.Frame(self.body_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

    def create_widgets(self):
        """
        The creation of the various widgets.
        :self.command_entry: The Entry prompt for the user to fill his commands
        :self.execute_button: executes the "self.execute_command" method
        :self.client_listbox: The list of connected clients
        :self.client_scrollbar: The scrollbar of the listbox
        :self.output_text: The command output displayed in the "self.output_text" widget; the user may not enter data in this field manually
        :self.output_scrollbar: The scrollbar of the "self.output_text" widget

        .set()-The .set() method adjusts the scrollbar slider position.
        .yview()- The .yview() method changes the vertical view of the widget.

        These two methods are used to tie the scrollbar to its related widget.

        The pattern is:

        widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=widget.yview)

        :return:
        """
        self.command_entry = tk.Entry(self.top_frame, font=("Arial", 14))
        self.execute_button = tk.Button(
            self.top_frame, text="Execute", width=12, command=self.execute_command
        )

        self.client_listbox = tk.Listbox(self.left_frame)
        self.client_scrollbar = tk.Scrollbar(self.left_frame, orient="vertical")

        self.client_listbox.config(yscrollcommand=self.client_scrollbar.set)
        self.client_scrollbar.config(command=self.client_listbox.yview)

        self.output_text = tk.Text(self.right_frame, state="disabled", wrap="word")
        self.output_scrollbar = tk.Scrollbar(self.right_frame, orient="vertical")

        self.output_text.config(yscrollcommand=self.output_scrollbar.set)
        self.output_scrollbar.config(command=self.output_text.yview)

    def place_widgets(self):

        """
        The place_widgets function positions the widgets and specifies directions of extension of the widgets
        :return:
        """

        self.top_frame.grid_columnconfigure(0, weight=1)

        self.command_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.execute_button.grid(row=0, column=1, padx=10, pady=10)

        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.client_listbox.grid(row=0, column=0, sticky="nsew")
        self.client_scrollbar.grid(row=0, column=1, sticky="ns")

        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.output_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.output_scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

    def execute_command(self):
        """
        The method utilized by the button press.
        The purpose of this method is to synchronize the index of the listbox with the index of the clients list under the class CommandServer()
        Since the list clients and the listbox self.client_listbox have values appended and removed from them almost simultaneously the index values will always match.
        :return: None
        """
        selection = self.client_listbox.curselection() #curselection is a method that returns all integers that represent the index value of each object.
        if not selection:
            return

        index = selection[0] #since the user may only choose one object each time the tuple will always contain a single integer value and we select it using the index 0
        selected_client = self.server.clients[index]
        self.server.button_clicked(self.command_entry, self.output_text, selected_client) #selected_client parameter represents the chosen client from the listbox

    def on_close(self):
        """
        Runs when the user clicks the X to close the GUI window:
        - gracefully shuts down server sockets
        - closes the GUI
        """
        self.server.shutdown()  # <-- The shutdown() method from CommandServer() class
        self.root.destroy()  # destroy() built-in method in the Python Tkinter library is a universal widget method used to permanently remove a widget (or an entire window and its children) from the display and free the memory it uses


if __name__ == "__main__":
    root = tk.Tk()
    server = CommandServer()  #The instance of the imported class CommandServer()
    app = CommandServerGUI(root,server) #Using the main GUI window (root) and the instance of CommandServer() (server) for synchronization

    threading.Thread(target=server.handle_connections, args=(app.client_listbox, app.output_text), daemon=True).start()

    root.mainloop()