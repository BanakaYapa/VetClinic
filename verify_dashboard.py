import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDate
from database import DatabaseManager
from ui.dashboard import Dashboard

def verify_dashboard():
    # 1. Setup DB with today's appointment
    db_name = "test_dashboard.db"
    db = DatabaseManager(db_name)
    
    # Clean up appointments
    cursor = db.connection.cursor()
    cursor.execute("DELETE FROM appointments")
    db.connection.commit()
    
    today = QDate.currentDate().toString("yyyy-MM-dd")
    print(f"Adding appointment for today: {today}")
    db.add_appointment(0, "Dashboard Test", today, "14:00")
    
    # 2. Init UI
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    dashboard = Dashboard(db)
    
    # 3. Check layout content
    # The layout is dashboard.sched_layout
    count = dashboard.sched_layout.count()
    # Expect 1 item + stretch, or close to it.
    # Actually, verify if we can find the label with "Dashboard Test"
    
    found = False
    for i in range(count):
        item = dashboard.sched_layout.itemAt(i)
        widget = item.widget()
        if widget:
            # Check children labels
            labels = widget.findChildren(object) # find any children
            # Actually dashboard creates a QFrame 'row'
            # inside row there are labels.
            # Let's verify text in labels
            import PySide6.QtWidgets as QtWidgets
            if isinstance(widget, QtWidgets.QFrame):
                child_labels = widget.findChildren(QtWidgets.QLabel)
                for lbl in child_labels:
                    if "Dashboard Test" in lbl.text():
                        found = True
                        print(f"Found label with text: {lbl.text()}")
                        break
    
    if found:
        print("SUCCESS: Appointment found in Dashboard widget.")
    else:
        print("FAILURE: Appointment not found in Dashboard widget.")
        # Debug: print what IS there
        print(f"Widget count in layout: {count}")

    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    print("DB Content:", cursor.fetchall())

if __name__ == "__main__":
    verify_dashboard()
