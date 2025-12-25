import socket
import threading
import time
import random
import hashlib


# Sensor simulation
class Sensor:
    def __init__(self, sensor_id, min_value, max_value):
        self.sensor_id = sensor_id
        self.min_value = min_value
        self.max_value = max_value

    def read_data(self):
        return random.uniform(self.min_value, self.max_value)


# RTU/PLC simulation
class RTU:
    def __init__(self, rtu_id, sensors, proxy_ip='127.0.0.1', proxy_port=8001):
        self.rtu_id = rtu_id
        self.sensors = sensors
        self.proxy_ip = proxy_ip  # Now sends data to attacker's proxy
        self.proxy_port = proxy_port

    def send_data(self):
        while True:
            sensor_data = {}
            for sensor in self.sensors:
                sensor_data[sensor.sensor_id] = sensor.read_data()
            message = f'RTU-{self.rtu_id}: {sensor_data}'
            checksum = hashlib.md5(message.encode()).hexdigest()  # Message integrity checksum
            message_with_checksum = f'{message}|{checksum}'
            self._transmit_to_proxy(message_with_checksum)
            time.sleep(2)  # Send data every 2 seconds

    def _transmit_to_proxy(self, message):
        # Simulate communication with the attacker proxy (man-in-the-middle)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.proxy_ip, self.proxy_port))  # Connect to attacker (proxy)
            s.sendall(message.encode('utf-8'))


if __name__ == "__main__":
    # Create sensors
    sensor1 = Sensor(sensor_id="TempSensor1", min_value=20.0, max_value=100.0)
    sensor2 = Sensor(sensor_id="PressureSensor1", min_value=1.0, max_value=10.0)

    # Create RTU with sensors
    rtu = RTU(rtu_id="001", sensors=[sensor1, sensor2])

    # Start RTU in a thread
    rtu_thread = threading.Thread(target=rtu.send_data)
    rtu_thread.start()
