import threading
import time
import serial
import can
import socket

UART_PORT = "/tmp/ttyV1"
CAN_CH = "vcan0"
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

class TargetEmulator:
    def __init__(self):
        self.running = True
        self.system_status = "IDLE"

    def uart_worker(self):
        """Handle serial communication for control and debug"""
        try:
            with serial.Serial(UART_PORT, 9600, timeout=1) as ser:
                while self.running:
                    if ser.in_waiting > 0:
                        raw_data = ser.readline().decode("utf-8").strip()
                        if raw_data == "GET_STATUS":
                            response = f"STATUS:{self.system_status}\n"
                            ser.write(response.encode())
        except Exception as e:
            print(f"UART Thread Error: {e}")

    def can_worker(self):
        """Handle CAN bus telemetry simulation"""
        try:
            bus = can.Bus(interface="socketcan", channel=CAN_CH)
            while self.running:
                msg = bus.recv(timeout=1.0)
                if msg:
                    self.system_status = "BUSY_RX"
        except Exception as e:
            print(f"CAN Thread Error: {e}")

    def udp_worker(self):
        """Handle Ethernet/UDP maintenance port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((UDP_IP, UDP_PORT))
            sock.settimeout(1.0)
            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    if data == b"PING":
                        sock.sendto(b"PONG", addr)
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"UDP Thread Error: {e}")

    def start(self):
        """Initialize and start all communication threads"""
        threads = [
            threading.Thread(target=self.uart_worker, daemon=True),
            threading.Thread(target=self.can_worker, daemon=True),
            threading.Thread(target=self.udp_worker, daemon=True),
        ]

        for t in threads:
            t.start()

        print("[INFO] Target Emulator active. Monitoring CAN, UART, and UDP...")
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False

if __name__ == "__main__":
    emulator = TargetEmulator()
    emulator.start()