import os
from database import DatabaseManager

def test_workflow():
    db_path = "test_vet_clinic.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    print("Initializing Database...")
    db = DatabaseManager(db_path)
    
    print("Adding Patient 'Buddy'...")
    patient_id = db.add_patient("Buddy", "Dog", "Golden Retriever", "Alice", "555-1234")
    print(f"Patient added with ID: {patient_id}")
    
    print("Adding Treatment for 'Buddy'...")
    db.add_treatment(patient_id, "2023-10-27", "Checkup", "Routine vaccination", 85.0)
    print("Treatment added.")
    
    print("Verifying Data...")
    patient = db.get_patient(patient_id)
    assert patient['name'] == "Buddy"
    assert patient['species'] == "Dog"
    
    treatments = db.get_patient_treatments(patient_id)
    assert len(treatments) == 1
    assert treatments[0]['diagnosis'] == "Checkup"
    assert treatments[0]['cost'] == 85.0
    
    print("Verification Successful!")
    db.close()
    os.remove(db_path)

if __name__ == "__main__":
    test_workflow()
