import serial
import csv
import time
from datetime import datetime
import os

# Adjust the COM port and baud rate as per your setup
SERIAL_PORT = 'COM3'  # e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux
BAUD_RATE = 115200

CSV_FILE = "C:/Users/Santhosh/OneDrive/Desktop/MAJnew/AI_1/disaster_data_2.1.csv"

headers = [
    "timestamp", "accel_x", "accel_y", "accel_z", "gasLevel", "gasLeakDetected",
    "fireDetected", "floodingDetected", "distanceToWater", "earthquakeDetected",
    "earthquakeMagnitude", "flowRate"
]

def collect_serial_data():
    file_exists = os.path.exists(CSV_FILE)
    
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser, open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not file_exists or os.stat(CSV_FILE).st_size == 0:
            writer.writerow(headers)  # Write headers only if file is new or empty
        
        print("Collecting data... Press Ctrl+C to stop.")
        try:
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line.count(',') == len(headers) - 2:  # -2 since Arduino doesn't send timestamp
                    row_data = line.split(',')
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # e.g., 2025-04-18 13:37:24.123
                    row = [timestamp] + row_data
                    writer.writerow(row)
                    print(row)
        except KeyboardInterrupt:
            print("Data collection stopped.")

if __name__ == "__main__":
    collect_serial_data()
