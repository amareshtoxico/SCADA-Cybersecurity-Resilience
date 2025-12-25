import socket

def scada_server():
    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 12345))
        server_socket.listen(1)
        print("SCADA Server is listening...")

        conn, addr = server_socket.accept()
        print(f"Connected to: {addr}")

        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Server received: {data.decode()}")

        conn.close()

if __name__ == "__main__":
    scada_server()
