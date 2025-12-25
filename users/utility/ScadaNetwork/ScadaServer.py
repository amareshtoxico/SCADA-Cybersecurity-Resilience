import socket
import threading
import time
import random
import hashlib


# SCADA server simulation
class SCADAServer:
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port

    def start_server(self):
        # Start listening for incoming data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print('SCADA server is running...')
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_connection, args=(conn, addr)).start()

    def handle_connection(self, conn, addr):
        with conn:
            print(f'Connected by {addr}')
            data = conn.recv(1024)
            if data:
                self.process_data(data.decode('utf-8'))

    def process_data(self, data):
        # Separate the message and the checksum
        message, received_checksum = data.rsplit('|', 1)
        calculated_checksum = hashlib.md5(message.encode()).hexdigest()
        print(f"Calcu={calculated_checksum} Received={received_checksum}")
        if calculated_checksum == received_checksum:
            pass
            # print(f"Valid data received: {message}")
        else:
            print(f"WARNING: Message tampered! {message}")


# Run the simulation
if __name__ == "__main__":
    # Create SCADA server
    scada_server = SCADAServer()

    # Start SCADA server in a thread
    server_thread = threading.Thread(target=scada_server.start_server)
    server_thread.start()
