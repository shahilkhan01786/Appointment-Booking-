from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from twilio.rest import Client
from supabase import create_client
from flask_cors import CORS
import threading
import time
from datetime import timezone

app = Flask(__name__)
CORS(app)

# Twilio
ACCOUNT_SID = "AC83ebf5e4db18c42b498552f3c5460ac7"
AUTH_TOKEN = "385c25a647328759b4b478157fdc6b18"
FROM_NUMBER = "whatsapp:+14155238886"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Supabase
SUPABASE_URL = "https://whwbmujdddeuxbkouysv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indod2JtdWpkZGRldXhia291eXN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA0NTMyODMsImV4cCI6MjA5NjAyOTI4M30.ucqPyEVwZwc4ga0D_UpKPp3fId2qE1irV5H-q6-cuZc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
def reminder_worker():
    while True:
        try:
            now = datetime.now(timezone.utc)

            reminders = supabase.table("Appointment") \
                .select("*") \
                .eq("reminder_sent", False) \
                .execute()

            for r in reminders.data:
                Appointment_time = datetime.fromisoformat(r["Appointment_time"]).replace(tzinfo=timezone.utc)

                time_left = Appointment_time - now

                if timedelta(0) < time_left <= timedelta(hours=1):

                    message = f"""
⏰ Reminder

Your appointment is in 1 hour
Time: {Appointment_time}
"""

                    client.messages.create(
                        from_=FROM_NUMBER,
                        to=f"whatsapp:+91{r['Phone']}",
                        body=message
                    )

                    supabase.table("Appointment").update({
                        "reminder_sent": True
                    }).eq("id", r["id"]).execute()

        except Exception as e:
            print("Reminder Error:", e)

        time.sleep(60)


@app.route("/book", methods=["POST"])
def book():
    try:
        data = request.json

        name = data["name"]
        phone = data["phone"]

        appointment_time = datetime.now(timezone.utc) + timedelta(hours=2)
        reminder_time = appointment_time - timedelta(hours=1)

        supabase.table("Appointment").insert({
            "name": name,
            "Phone": phone,
            "Appointment_time": appointment_time.isoformat(),
            "reminder_time": reminder_time.isoformat(),
            "reminder_sent": False
        }).execute()

        client.messages.create(
            from_=FROM_NUMBER,
            body=f"Appointment Confirmed for {name}",
            to=f"whatsapp:+91{phone}"
        )

        return jsonify({"success": True})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
threading.Thread(target=reminder_worker, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)