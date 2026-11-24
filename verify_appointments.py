from database import DatabaseManager

def verify_appointments():
    print("Initializing Database...")
    db = DatabaseManager("test_vet_clinic_appointments.db")
    
    # 1. Add a dummy patient
    print("Adding dummy patient...")
    patient_id = db.add_patient("Mittens", "Cat", "Persian", "Alice", "555-0101")
    print(f"Patient added with ID: {patient_id}")
    
    # 2. Add an appointment
    print("Adding appointment...")
    success = db.add_appointment(patient_id, "Vaccination", "2023-11-15", "10:00")
    if success:
        print("Appointment added successfully.")
    else:
        print("Failed to add appointment.")
        return

    # 3. Get appointments
    print("Fetching appointments...")
    appointments = db.get_appointments_by_date("2023-11-15")
    if len(appointments) == 1:
        appt = appointments[0]
        print(f"Found appointment: {appt['title']} for patient ID {appt['patient_id']} at {appt['time']}")
    else:
        print(f"Error: Expected 1 appointment, found {len(appointments)}")

    # 4. Update status
    print("Updating appointment status...")
    # Assuming the first appointment has ID 1
    db.update_appointment_status(1, "Completed")
    
    # Verify update
    updated_appts = db.get_appointments_by_date("2023-11-15")
    if updated_appts[0]['status'] == "Completed":
        print("Status update verified.")
    else:
        print(f"Status update failed. Current status: {updated_appts[0]['status']}")

    print("\nVerification Complete.")

if __name__ == "__main__":
    verify_appointments()
