async function saveAppointment() {

    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const time = document.getElementById("time").value;

    if (!name || !phone || !time) {
        alert("Please fill all fields");
        return;
    }

    try {

        const response = await fetch("https://appointment-booking01.onrender.com", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                phone: phone,
                appointment_time: time
            })
        });

        const result = await response.json();

        if (result.success) {

            alert("Appointment booked successfully and WhatsApp message sent!");

            document.getElementById("name").value = "";
            document.getElementById("phone").value = "";
            document.getElementById("time").value = "";

        } else {

            alert("Error: " + result.error);
        }

    } catch (error) {

        console.error(error);
        alert("Backend connection error");
    }
}
