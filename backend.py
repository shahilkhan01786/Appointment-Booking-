from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from twilio.rest import Client
from supabase import create_client
from flask_cors import CORS
import threading
import time
from datetime import timezone
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
CORS(app)

# Twilio
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
FROM_NUMBER = "whatsapp:+14155238886"

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
def parse_time(time_str):
    time_str = time_str.replace("Z", "")

    if "+" in time_str:
        time_str = time_str.split("+")[0]

    return datetime.fromisoformat(time_str)


def reminder_worker():
    while True:
        try:
            now = datetime.utcnow() + timedelta(hours=5, minutes=30)

            appointments = supabase.table("Appointment") \
                .select("*") \
                .eq("reminder_sent", False) \
                .execute()

            for row in appointments.data:
                appointment_time = parse_time(row["Appointment_time"])
                time_left = appointment_time - now

                print("Checking:", row["Customer_name"])
                print("Time left:", time_left)

                # TEST: appointment se 2 minute pehle
                if timedelta(0) < time_left <= timedelta(minutes=2):

                    msg = f"""
⏰ Appointment Reminder

Hello {row['Customer_name']}

Your appointment is in 2 minutes.

Date & Time:
{appointment_time.strftime('%d-%m-%Y %I:%M %p')}
"""

                    try:
                        twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

                        twilio_client.messages.create(
                            from_=FROM_NUMBER,
                            to=f"whatsapp:+91{row['Phone']}",
                            body=msg
                        )

                        supabase.table("Appointment").update({
                            "reminder_sent": True
                        }).eq("id", row["id"]).execute()

                        print("Reminder Sent Successfully")

                    except Exception as e:
                        print("Twilio Reminder Error:", e)

        except Exception as e:
            print("Reminder Error:", e)

        time.sleep(30)


@app.route("/book", methods=["POST"])
def book():
    try:
        data = request.json

        name = data["name"]
        phone = data["phone"]
        appointment_time = data["appointment_time"]

        supabase.table("Appointment").insert({
            "Customer_name": name,
            "Phone": phone,
            "Appointment_time": appointment_time,
            "reminder_sent": False
        }).execute()

        dt = parse_time(appointment_time)

        confirmation_msg = f"""
✅ Appointment Confirmed

Name: {name}
Phone: {phone}

Appointment Date & Time:
{dt.strftime('%d-%m-%Y %I:%M %p')}
"""

        twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

        twilio_client.messages.create(
            from_=FROM_NUMBER,
            to=f"whatsapp:+91{phone}",
            body=confirmation_msg
        )

        return jsonify({"success": True})

    except Exception as e:
        print("Booking Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500


threading.Thread(target=reminder_worker, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)

