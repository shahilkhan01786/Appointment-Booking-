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
ACCOUNT_SID = "ACe09c495957ac286a5289122ad8904175"
AUTH_TOKEN = "de58779dc29f4ec9009db2064fd4fde5"
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
                Appointment_time = datetime.fromisoformat(r["Appointment_time"])

                if now >= Appointment_time - timedelta(hours=1):

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

                    supabase.table("Appointment") \
                        .update({"reminder_sent": True}) \
                        .eq("id", r["id"]) \
                        .execute()

        except Exception as e:
            print("Reminder Error:", e)

        time.sleep(60)

@app.route("/book", methods=["POST"])
def book():
    try:
        data = request.json

        name = data["name"]
        Phone = data["phone"]

        message = client.messages.create(
            from_=FROM_NUMBER,
            body=f"Appointment Confirmed for {name}",
            to=f"whatsapp:+91{Phone}"
        )

        print("Message SID:", message.sid)

        return jsonify({"success": True})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

    # Confirmation WhatsApp
    client.messages.create(
        from_=FROM_NUMBER,
        body=f"✅ Appointment Confirmed for {name} at {nice_time}",
        to=phone
    )

    # Save in Supabase
    supabase.table("Appointments").insert({
        "name": name,
        "Phone": phone,
        "Appointment_time": appointment_time.isoformat(),
        "reminder_time": reminder_time.isoformat(),
        "reminder_sent": False
    }).execute()

    return jsonify({
        "success": True,
        "message": "Appointment booked"
    })
threading.Thread(target=reminder_worker, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)