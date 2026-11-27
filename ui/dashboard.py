from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QGridLayout, QFrame, QGraphicsDropShadowEffect, QPushButton)
from PySide6.QtCore import Qt, QTimer, QDate, QTime, QSize
from PySide6.QtGui import QColor
import qtawesome as qta

class StatCard(QFrame):
    def __init__(self, title, value, subtitle, color):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border-left: 6px solid {color};
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        self.setMinimumWidth(200)
        
        # Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Value
        self.lbl_value = QLabel(str(value))
        self.lbl_value.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")
        layout.addWidget(self.lbl_value)
        
        # Title
        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        layout.addWidget(lbl_title)
        
        # Subtitle
        if subtitle:
            lbl_sub = QLabel(subtitle)
            lbl_sub.setStyleSheet("font-size: 12px; color: #999;")
            layout.addWidget(lbl_sub)

    def set_value(self, value):
        self.lbl_value.setText(str(value))

class ClockCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #D32F2F, stop:1 #C2185B);
                border-radius: 12px;
                color: white;
            }
            QLabel { background: transparent; }
        """)
        
        # Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        
        self.time_lbl = QLabel()
        self.time_lbl.setAlignment(Qt.AlignCenter)
        self.time_lbl.setStyleSheet("font-size: 48px; font-weight: bold;")
        
        self.date_lbl = QLabel()
        self.date_lbl.setAlignment(Qt.AlignCenter)
        self.date_lbl.setStyleSheet("font-size: 16px;")
        
        layout.addWidget(self.time_lbl)
        layout.addWidget(self.date_lbl)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        now = QTime.currentTime()
        self.time_lbl.setText(now.toString("HH:mm"))
        self.date_lbl.setText(QDate.currentDate().toString("dddd, MMMM d, yyyy"))

class Dashboard(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # HEADER
        header = QLabel("Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(header)
        
        # CARDS ROW
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        # Count Queries
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT count(*) FROM treatments")
        treatment_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM patients")
        patient_count = cursor.fetchone()[0]
        
        self.card_treatments = StatCard("Treatments", treatment_count, "Total records", "#1976D2")
        self.card_clients = StatCard("Clients", patient_count, "On your system", "#212121")
        self.card_clock = ClockCard()
        
        cards_layout.addWidget(self.card_clients)
        cards_layout.addWidget(self.card_treatments)
        cards_layout.addWidget(self.card_clock)
        
        layout.addLayout(cards_layout)
        
        # MAIN CONTENT AREA (Placeholder for Schedule/Graph)
        layout.addSpacing(20)
        
        # Activities Header
        act_header_layout = QHBoxLayout()
        
        sched_lbl = QLabel("Today's Activities")
        sched_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #555;")
        act_header_layout.addWidget(sched_lbl)
        
        act_header_layout.addStretch()
        
        refresh_btn = QPushButton()
        refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#888'))
        refresh_btn.setIconSize(QSize(16, 16))
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setToolTip("Refresh Activities")
        refresh_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; }
            QPushButton:hover { background-color: #f0f0f0; border-radius: 12px; }
        """)
        refresh_btn.clicked.connect(self.load_appointments)
        act_header_layout.addWidget(refresh_btn)
        
        layout.addLayout(act_header_layout)
        
        # Schedule Box
        self.schedule_box = QFrame()
        # Semi-transparent for watermark
        self.schedule_box.setStyleSheet("background-color: rgba(255, 255, 255, 0.6); border-radius: 8px; border: 1px solid #ddd;")
        self.schedule_box.setMinimumHeight(300)
        
        self.sched_layout = QVBoxLayout(self.schedule_box)
        layout.addWidget(self.schedule_box)
        
        layout.addStretch()
        
        # Initial Load
        self.load_appointments()

    def load_appointments(self):
        # Clear existing items
        while self.sched_layout.count():
            item = self.sched_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        today = QDate.currentDate().toString("yyyy-MM-dd")
        appointments = self.db.get_appointments_by_date(today)
        
        if not appointments:
            msg = QLabel("No appointments scheduled for today.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("color: #888; font-size: 14px;")
            self.sched_layout.addWidget(msg)
            self.sched_layout.addStretch()
        else:
            for appt in appointments:
                # Create a simple row widget
                row = QFrame()
                row.setStyleSheet("background-color: #f9f9f9; border-radius: 6px;")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(15, 10, 15, 10)
                
                # Time
                time_lbl = QLabel(appt['time'])
                time_lbl.setStyleSheet("font-weight: bold; color: #1976D2; min-width: 50px;")
                
                # Info
                info_text = f"{appt['title']}"
                if appt.get('patient_name'):
                    info_text += f" ({appt['patient_name']})"
                    
                info_lbl = QLabel(info_text)
                info_lbl.setStyleSheet("font-size: 14px; color: #333; font-weight: 500;")
                
                # Status
                status = appt.get('status', 'Scheduled')
                status_colors = {
                    'Completed': '#4CAF50',
                    'Cancelled': '#e53935',
                    'Scheduled': '#FF9800',
                }
                status_color = status_colors.get(status, '#FF9800')
                status_lbl = QLabel(status)
                status_lbl.setStyleSheet(f"font-size: 11px; color: white; background-color: {status_color}; padding: 4px 8px; border-radius: 10px;")
                
                row_layout.addWidget(time_lbl)
                row_layout.addWidget(info_lbl, 1) # Stretch
                row_layout.addWidget(status_lbl)
                
                self.sched_layout.addWidget(row)
            
            self.sched_layout.addStretch()

    def refresh(self):
        # Refresh counts
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT count(*) FROM treatments")
        treatment_count = cursor.fetchone()[0]
        self.card_treatments.set_value(treatment_count)

        cursor.execute("SELECT count(*) FROM patients")
        patient_count = cursor.fetchone()[0]
        self.card_clients.set_value(patient_count)
        
        # Refresh schedule
        self.load_appointments()
