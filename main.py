import cv2
import pandas as pd
from pyzbar import pyzbar
from datetime import datetime
import os
import time

current_date_for_file = datetime.now().strftime("%d-%m-%Y")
log_file = f'buslog-{current_date_for_file}.csv'

bus_file = 'buses.csv'

cooldown_time = 5
last_scan_times = {}  

if not os.path.exists(bus_file):
    print(f"{bus_file} not found. Creating with default values.")
    
    bus_data = pd.DataFrame({
        'BusNo': [str(i) for i in range(1, 11)],
        'BusLicense': [str(i) for i in range(1, 11)],
        'Status': ['out'] * 10,
        'BusType': ['GMA']*10
    })
    
    bus_data.to_csv(bus_file, index=False)
else:
    bus_data = pd.read_csv(bus_file)
    bus_data['BusLicense'] = bus_data['BusLicense'].astype(str) 

if not os.path.exists(log_file):
    print(f"{log_file} not found. Creating with headers.")
    log_data = pd.DataFrame(columns=['BusNo', 'BusLicense', 'Status', 'Time', 'Date'])
    log_data.to_csv(log_file, index=False)

message = ""
color = (255, 255, 255) 

def log_bus_Status(BusNo, BusLicense, log_Status):
    global message, color 
    

    BusLicense = str(BusLicense)
    
    bus = bus_data[bus_data['BusLicense'] == BusLicense]
    
    if not bus.empty:
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%d/%m/%y")
        
        new_log = pd.DataFrame([[BusNo, BusLicense, log_Status, current_time, current_date]], columns=['BusNo', 'BusLicense', 'Status', 'Time', 'Date'])
        new_log.to_csv(log_file, mode='a', header=False, index=False) 
        
        bus_data.loc[bus_data['BusLicense'] == BusLicense, 'Status'] = log_Status
        bus_data.to_csv(bus_file, index=False)
        
        message = f"Logged Bus {BusLicense} as {log_Status} at {current_time}, {current_date}."
        color = (0, 255, 0)
        print(message)
    else:
        message = f"Bus with ID {BusLicense} not found."
        color = (0, 0, 255)
        print(message)

def process_qr_code(decoded_data):
    global last_scan_times
    
    try:
        print(f"Raw decoded data: {decoded_data}")
        
        details = dict(item.split(': ') for item in decoded_data.split(', '))
        
        BusLicense = details['BusLicense'].strip()
        BusNo = details['BusNo'].strip()
        
        print(f"Parsed BusLicense: {BusLicense}")
        
        current_time = time.time()
        last_scan_time = last_scan_times.get(BusLicense, 0)
        
        if current_time - last_scan_time < cooldown_time:
            print(f"Cooldown active for Bus {BusLicense}. Please wait a few seconds before the next scan.")
            return

        current_Status = bus_data.loc[bus_data['BusLicense'] == BusLicense, 'Status'].values[0]
        new_Status = 'in' if current_Status == 'out' else 'out'
        
        log_bus_Status(BusNo, BusLicense, new_Status)
        
        last_scan_times[BusLicense] = current_time
    
    except Exception as e:
        message = f"Error processing QR code: {e}"
        color = (0, 0, 255)
        print(message)

def decode_qr_codes(frame):
    qr_codes = pyzbar.decode(frame)
    for qr_code in qr_codes:
        qr_data = qr_code.data.decode('utf-8')
        print(f"Decoded QR code data: {qr_data}")
        process_qr_code(qr_data)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    decode_qr_codes(frame)

    if message:
        cv2.putText(frame, message, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
    
    cv2.imshow('QR Code Bus Logger', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\nFinal Bus Log:")
log_data = pd.read_csv(log_file)
print(log_data)

os.system("python uploader.py")