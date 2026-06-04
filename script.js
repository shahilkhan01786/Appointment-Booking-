const supabaseUrl = "https://whwbmujdddeuxbkouysv.supabase.co";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indod2JtdWpkZGRldXhia291eXN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA0NTMyODMsImV4cCI6MjA5NjAyOTI4M30.ucqPyEVwZwc4ga0D_UpKPp3fId2qE1irV5H-q6-cuZc";

const supabaseClient = supabase.createClient(
    supabaseUrl,
    supabaseKey
);

async function saveAppointment() {

    const name = document.getElementById("name").value;
    const phone = document.getElementById("phone").value;
    const time = document.getElementById("time").value;

    if (!name || !phone || !time) {
        alert("Please fill all fields");
        return;
    }

    const { data, error } = await supabaseClient
        .from("Appointment")
        .insert([
            {
                Customer_name: name,
                Phone: phone,
                Appointment_time: time
            }
        ]);

    if (error) {
        console.error(error);
        alert("Error: " + error.message);
        return;
    }
    await fetch("http://127.0.0.1:5000/book", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        name: name,
        phone: phone,
        Appointment_time: time
    })
});

    alert("Appointment booked successfully!");

    document.getElementById("name").value = "";
    document.getElementById("phone").value = "";
    document.getElementById("time").value = "";
}