from database import DatabaseManager
import os

def test_separation():
    print("Testing Separation Logic...")
    db = DatabaseManager() # Uses existing vet_clinic.db if present
    
    # Ensure there are treatments
    treatments = db.get_all_treatments()
    print(f"Found {len(treatments)} total treatments.")
    
    if len(treatments) > 0:
        first = treatments[0]
        print(f"Sample Treatment: {first['date']} - {first['patient_name']} - {first['diagnosis']}")
        assert 'patient_name' in first.keys()
    
    print("get_all_treatments() passed.")

if __name__ == "__main__":
    test_separation()
