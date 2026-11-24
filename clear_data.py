import sqlite3
import os

DB_NAME = "vet_clinic.db"

if os.path.exists(DB_NAME):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Disable foreign keys to allow deleting in any order (though we should respect order)
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        tables = ["appointments", "treatments", "patients"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Cleared table: {table}")
            
        # Reset Auto-Increment Counters
        cursor.execute("DELETE FROM sqlite_sequence")
        print("Reset auto-increment counters.")
            
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        conn.close()
        print("All data cleared successfully.")
    except Exception as e:
        print(f"Error clearing data: {e}")
else:
    print(f"Database {DB_NAME} not found.")
