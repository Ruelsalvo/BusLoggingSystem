from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

app = Flask(__name__)

cred = credentials.Certificate("FILE NAME HERE")#SHOULD LOOK SOMETHING LIKE bussysqr-firebase-adminsdk-################.json
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def display_bus_logs():
    log_ref = db.collection("bus_logs")
    
    docs = log_ref.stream()
    
    logs = [doc.to_dict() for doc in docs]

    dates = sorted({log['Date'] for log in logs})

    return render_template('bus_logs.html', logs=logs, dates=dates, datetime=datetime)

if __name__ == '__main__':
    app.run(debug=True)
