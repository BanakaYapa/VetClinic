import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="vet_clinic.db"):
        self.db_name = db_name
        self.connection = None
        self.initialize_db()

    def connect(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.db_name)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def initialize_db(self):
        """Creates tables if they don't exist."""
        conn = self.connect()
        cursor = conn.cursor()

        # Patients Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                breed TEXT,
                owner_name TEXT NOT NULL,
                contact_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Treatments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                diagnosis TEXT,
                treatment_details TEXT,
                cost REAL,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        """)

        # Appointments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT DEFAULT 'Scheduled',
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        """)

        # Complaints Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_name TEXT NOT NULL,
                patient_id INTEGER,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'Open',
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        """)

        # GCE Table (General Clinic Examination)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gce (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                date TEXT NOT NULL,
                temperature REAL,
                description TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        """)

        # Check for dob column
        cursor.execute("PRAGMA table_info(patients)")
        columns = [col[1] for col in cursor.fetchall()]
        if "dob" not in columns:
            cursor.execute("ALTER TABLE patients ADD COLUMN dob TEXT")
            print("Added dob column to patients table.")

        # Check for weight and age in treatments
        cursor.execute("PRAGMA table_info(treatments)")
        columns = [col[1] for col in cursor.fetchall()]
        if "weight" not in columns:
            cursor.execute("ALTER TABLE treatments ADD COLUMN weight REAL")
            print("Added weight column to treatments table.")
        if "age" not in columns:
            cursor.execute("ALTER TABLE treatments ADD COLUMN age TEXT")
            print("Added age column to treatments table.")

        conn.commit()
        print("Database initialized.")

    def populate_dummy_data(self):
        # ... (keep existing but empty/unused)
        pass

    def add_patient(self, name, species, breed, owner_name, contact_info, dob=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patients (name, species, breed, owner_name, contact_info, dob)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, species, breed, owner_name, contact_info, dob))
        conn.commit()
        return cursor.lastrowid

    def update_patient(self, patient_id, name, species, breed, owner_name, contact_info, dob):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patients 
            SET name=?, species=?, breed=?, owner_name=?, contact_info=?, dob=?
            WHERE id=?
        """, (name, species, breed, owner_name, contact_info, dob, patient_id))
        conn.commit()
        return cursor.rowcount > 0

    def get_all_patients(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY id")
        return cursor.fetchall()

    def search_patients(self, query):
        conn = self.connect()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT * FROM patients 
            WHERE name LIKE ? OR owner_name LIKE ?
            ORDER BY id
        """, (search_term, search_term))
        return cursor.fetchall()
    
    def get_patient(self, patient_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        return cursor.fetchone()

    def add_treatment(self, patient_id, date, diagnosis, treatment_details, cost, weight=None, age=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO treatments (patient_id, date, diagnosis, treatment_details, cost, weight, age)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, date, diagnosis, treatment_details, cost, weight, age))
        conn.commit()
        return cursor.lastrowid

    def get_patient_treatments(self, patient_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM treatments 
            WHERE patient_id = ? 
            ORDER BY date DESC
        """, (patient_id,))
        return cursor.fetchall()

    def get_all_treatments(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.*, p.name as patient_name 
            FROM treatments t
            JOIN patients p ON t.patient_id = p.id
            ORDER BY t.date DESC
        """)
        return cursor.fetchall()

    def clear_all_treatments(self):
        """Removes all records from the treatments table."""
        if not self.connection: return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM treatments")
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing treatments: {e}")
            return False

    def delete_treatment(self, treatment_id):
        """Deletes a single treatment record."""
        if not self.connection: return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM treatments WHERE id = ?", (treatment_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting treatment: {e}")
            return False

    def search_treatments(self, query):
        if not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            search_query = f"%{query}%"
            # Join with patients to filter by animal name only
            cursor.execute("""
                SELECT t.*, p.name as patient_name
                FROM treatments t
                JOIN patients p ON t.patient_id = p.id
                WHERE p.name LIKE ?
                ORDER BY t.date DESC
            """, (search_query,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error searching treatments: {e}")
            return []

    # --- Appointments ---
    def add_appointment(self, patient_id, title, date, time):
        if not self.connection:
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO appointments (patient_id, title, date, time)
                VALUES (?, ?, ?, ?)
            """, (patient_id, title, date, time))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding appointment: {e}")
            return False

    def get_appointments_by_date(self, date_str):
        if not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            # Join to get patient name as well
            cursor.execute("""
                SELECT a.id, a.patient_id, p.name as patient_name, a.title, a.date, a.time, a.status
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.id
                WHERE a.date = ?
                ORDER BY a.time ASC
            """, (date_str,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error fetching appointments: {e}")
            return []

    def update_appointment_status(self, appt_id, new_status):
        if not self.connection:
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE appointments
                SET status = ?
                WHERE id = ?
            """, (new_status, appt_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating appointment status: {e}")
            return False

    # --- Complaints ---
    def add_complaint(self, owner_name, patient_id, description, date):
        if not self.connection: return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO complaints (owner_name, patient_id, description, date)
                VALUES (?, ?, ?, ?)
            """, (owner_name, patient_id, description, date))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding complaint: {e}")
            return False

    def get_all_complaints(self):
        if not self.connection: return []
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT c.*, p.name as patient_name
                FROM complaints c
                LEFT JOIN patients p ON c.patient_id = p.id
                ORDER BY c.date DESC
            """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error fetching complaints: {e}")
            return []

    def update_complaint_status(self, complaint_id, new_status):
        if not self.connection: return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE complaints SET status = ? WHERE id = ?", (new_status, complaint_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating complaint: {e}")
            return False

    def delete_complaint(self, complaint_id):
        if not self.connection: return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting complaint: {e}")
            return False

    # --- Deletion ---
    def delete_appointment(self, appt_id):
        if not self.connection:
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM appointments WHERE id = ?", (appt_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting appointment: {e}")
            return False

    def delete_patient(self, patient_id):
        """Deletes a patient and associated clinical records (appointments, treatments, GCE).
        Unlinks any complaints associated with the patient so complaint history is preserved.
        """
        if not self.connection:
            return False
        try:
            cursor = self.connection.cursor()
            # 1. Delete Appointments
            cursor.execute("DELETE FROM appointments WHERE patient_id = ?", (patient_id,))
            # 2. Delete Treatments
            cursor.execute("DELETE FROM treatments WHERE patient_id = ?", (patient_id,))
            # 3. Delete GCE records
            cursor.execute("DELETE FROM gce WHERE patient_id = ?", (patient_id,))
            # 4. Unlink Complaints (keep owner complaint record without dangling patient_id)
            cursor.execute("UPDATE complaints SET patient_id = NULL WHERE patient_id = ?", (patient_id,))
            # 5. Delete Patient
            cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting patient: {e}")
            return False

    # --- GCE (General Clinic Examination) ---
    def add_gce(self, patient_id, date, temperature, description):
        if not self.connection: return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO gce (patient_id, date, temperature, description)
                VALUES (?, ?, ?, ?)
            """, (patient_id, date, temperature, description))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding GCE: {e}")
            return False

    def get_all_gce(self, search_query=None):
        if not self.connection: return []
        try:
            cursor = self.connection.cursor()
            if search_query:
                q = f"%{search_query}%"
                cursor.execute("""
                    SELECT g.*, p.name as patient_name
                    FROM gce g
                    JOIN patients p ON g.patient_id = p.id
                    WHERE p.name LIKE ?
                    ORDER BY g.date DESC
                """, (q,))
            else:
                cursor.execute("""
                    SELECT g.*, p.name as patient_name
                    FROM gce g
                    JOIN patients p ON g.patient_id = p.id
                    ORDER BY g.date DESC
                """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error fetching GCE: {e}")
            return []

    def delete_gce(self, gce_id):
        if not self.connection: return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM gce WHERE id = ?", (gce_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting GCE: {e}")
            return False

if __name__ == "__main__":
    # Test initialization
    db = DatabaseManager()
    db.close()
