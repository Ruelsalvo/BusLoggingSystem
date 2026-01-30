import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

cred = credentials.Certificate("FILE NAME HERE")#SHOULD LOOK LIKE bussysqr-firebase-adminsdk-################.json
firebase_admin.initialize_app(cred)
db = firestore.client()

current_date_for_file = datetime.now().strftime("%d-%m-%Y")
log_file = f'buslog-{current_date_for_file}.csv'

if not os.path.exists(log_file):
    print(f"Log file '{log_file}' not found.")
else:
    log_data = pd.read_csv(log_file)
    
    log_ref = db.collection("bus_logs")

    for index, row in log_data.iterrows():
        BusLicense = row['BusLicense']
        BusNo = row['BusNo']
        status = row['Status']
        time_logged = row['Time']
        date_logged = row['Date']
        
        log_ref.add({
            "BusNo":BusNo,
            "BusLicense": BusLicense,
            "Status": status,
            "Time": time_logged,
            "Date": date_logged,
            "DataTime": datetime.now().strftime("%H:%M:%S")
        })
        
        print(f"Uploaded log for Bus {BusLicense}: Status = {status}, Time = {time_logged}, Date = {date_logged}")

    print("All data from CSV has been uploaded to Firebase.")
