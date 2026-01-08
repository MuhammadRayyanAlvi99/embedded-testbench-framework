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

    def _uart_worker(self):
        try:
            with serial.Serial(UART_PORT, 9600, timeout=0.1) as ser:
                ser.reset_input_buffer()  # Clear stale data from virtual PTY
                ser.reset_output_buffer()
                while self.running:
                    if ser.in_waiting > 0:
                        raw_data = ser.readline().decode("utf-8").strip()
                        if raw_data == "GET_STATUS":
                            ser.write(f"STATUS:{self.system_status}\n".encode())
                            ser.flush()
                    time.sleep(0.01)
        except Exception as e:
            print(f"[ERROR] UART: {e}")

    def _can_worker(self):
        try:
            with can.Bus(interface="socketcan", channel=CAN_CH) as bus:
                while self.running:
                    msg = bus.recv(timeout=0.1)  # Non-blocking with timeout
                    if msg:
                        self.system_status = "BUSY_RX"
        except Exception as e:
            print(f"[ERROR] CAN: {e}")

    def _udp_worker(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind((UDP_IP, UDP_PORT))
                sock.settimeout(1.0)  # Prevent CPU hogging
                while self.running:
                    try:
                        data, addr = sock.recvfrom(1024)
                        if data == b"PING":
                            sock.sendto(b"PONG", addr)
                    except socket.timeout:
                        continue
        except Exception as e:
            print(f"[ERROR] UDP: {e}")

    def start(self):
        threads = [
            threading.Thread(target=self._uart_worker, daemon=True),
            threading.Thread(target=self._can_worker, daemon=True),
            threading.Thread(target=self._udp_worker, daemon=True),
        ]

        for t in threads:
            t.start()

        print("[INFO] Target Emulator active (CAN, UART, UDP). Press Ctrl+C to stop.")
        try:
            while self.running:
                time.sleep(0.1)  # Prevent CPU hogging
        except KeyboardInterrupt:
            self.running = False
            print("\n[INFO] Stopping emulator...")


if __name__ == "__main__":
    emulator = TargetEmulator()
    emulator.start()
