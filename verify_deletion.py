from database import DatabaseManager
import os

def verify_deletion():
    db_name = "test_vet_clinic_delete.db"
    # Start fresh
    if os.path.exists(db_name):
        os.remove(db_name)
        
    print("Initializing Database...")
    db = DatabaseManager(db_name)
    
    # 1. Add Patient & Data
    print("Adding patient 'To Delete'...")
    pid = db.add_patient("To Delete", "Dog", "Pug", "Owner", "Tel")
    
    print("Adding treatment...")
    db.add_treatment(pid, "2023-01-01", "Diag", "Details", 100)
    
    print("Adding appointment...")
    db.add_appointment(pid, "Appt", "2023-01-01", "10:00")
    
    # Verify existence
    assert len(db.get_all_patients()) == 1 + 5 # 1 new + 5 dummy
    assert len(db.get_patient_treatments(pid)) == 1
    assert len(db.get_appointments_by_date("2023-01-01")) == 1
    
    # 2. Delete Appointment
    print("Testing Appointment Deletion...")
    appt = db.get_appointments_by_date("2023-01-01")[0]
    db.delete_appointment(appt['id'])
    assert len(db.get_appointments_by_date("2023-01-01")) == 0
    print("Appointment deleted successfully.")
    
    # 3. Add Appt back for Cascade Test
    db.add_appointment(pid, "Appt 2", "2023-01-01", "11:00")
    
    # 4. Delete Patient (Cascade)
    print("Testing Patient Cascade Deletion...")
    db.delete_patient(pid)
    
    # Verify
    assert db.get_patient(pid) is None
    assert len(db.get_patient_treatments(pid)) == 0
    assert len(db.get_appointments_by_date("2023-01-01")) == 0
    
    print("Patient and cascade data deleted successfully.")
    print("Verification Complete.")

if __name__ == "__main__":
    verify_deletion()
