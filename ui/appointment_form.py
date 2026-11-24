import qtawesome as qta
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QDateEdit, QTimeEdit, QComboBox, QPushButton, 
                               QHBoxLayout, QLabel, QMessageBox, QFrame, QWidget)
from PySide6.QtCore import QDate, QTime, Qt, QSize

class AppointmentForm(QDialog):
    def __init__(self, parent, db_manager, selected_date=None):
        super().__init__(parent)
        self.db = db_manager
        
        self.setWindowTitle("Schedule Appointment")
        self.setFixedWidth(500)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Main container
        self.container = QFrame(self)
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #ddd;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.container)
        
        inner_layout = QVBoxLayout(self.container)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        # 1. Header with Gradient (Teal)
        self.header = QFrame()
        self.header.setFixedHeight(100)
        self.header.setObjectName("HeaderFrame")
        self.header.setStyleSheet("""
            #HeaderFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00897B, stop:1 #26A69A);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon('fa5s.calendar-check', color='white').pixmap(QSize(40, 40)))
        header_layout.addWidget(icon_lbl)
        
        title_lbl = QLabel("Schedule Appointment")
        title_lbl.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton { background: transparent; color: white; font-size: 18px; border: none; }
            QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 15px; }
        """)
        header_layout.addWidget(close_btn)
        
        inner_layout.addWidget(self.header)

        # 2. Content Area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(15)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.setStyleSheet("""
            QLabel { font-size: 13px; color: #555; font-weight: 500; }
            QLineEdit, QDateEdit, QTimeEdit, QComboBox {
                background-color: #fcfcfc;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 12px;
                color: #333;
                font-size: 14px;
            }
            QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {
                border: 2px solid #00897B;
                background-color: #fff;
            }

            /* QDateEdit/QTimeEdit & QCalendarWidget Styling */
            QDateEdit::drop-down, QTimeEdit::drop-down {
                border: none;
                width: 30px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #00897B;
                margin-right: 10px;
            }
            
            QCalendarWidget QWidget {
                alternate-background-color: #f2f2f2;
                background-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #00897B;
            }
            QCalendarWidget QToolButton {
                color: white;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 5px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #333;
                selection-background-color: #00897B;
                selection-color: white;
                outline: 0;
            }
            QCalendarWidget QHeaderView {
                background-color: #f9f9f9;
            }

            /* QTimeEdit Up/Down Buttons */
            QTimeEdit::up-button, QTimeEdit::down-button {
                background: #fcfcfc;
                border-left: 1px solid #e0e0e0;
                width: 25px;
            }
            QTimeEdit::up-button { border-top-right-radius: 8px; }
            QTimeEdit::down-button { border-bottom-right-radius: 8px; }
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover { background: #f0f0f0; }

            QTimeEdit::up-arrow { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 4px solid #00897B; }
            QTimeEdit::down-arrow { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 4px solid #00897B; }

            /* QComboBox Styling */
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #00897B;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: #00897B;
                selection-color: white;
                outline: 0;
                border-radius: 8px;
            }
        """)

        # Patient Selection
        self.patient_combo = QComboBox()
        self.patient_combo.addItem("General Event (No Patient)", None)
        patients = self.db.get_all_patients()
        for p in patients:
            self.patient_combo.addItem(f"{p['name']} ({p['species']})", p['id'])
        
        # Title / Reason
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Vaccination, Surgery, Meeting")
        
        # Date & Time
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        if selected_date:
            self.date_input.setDate(selected_date)
            
        self.time_input = QTimeEdit(QTime.currentTime())
        self.time_input.setMinimumWidth(150)
        
        form_layout.addRow("Patient", self.patient_combo)
        form_layout.addRow("Reason", self.title_input)
        form_layout.addRow("Date", self.date_input)
        form_layout.addRow("Time", self.time_input)
        
        content_layout.addLayout(form_layout)
        
        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 10, 0, 0)
        footer_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #ddd; padding: 10px 20px; border-radius: 8px; font-weight: bold; color: #666;
            }
            QPushButton:hover { background: #f5f5f5; }
        """)
        footer_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Schedule")
        self.save_btn.setMinimumWidth(140)
        self.save_btn.clicked.connect(self.save_appointment)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00897B, stop:1 #26A69A);
                color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00695C, stop:1 #00897B); }
        """)
        footer_layout.addWidget(self.save_btn)
        
        content_layout.addLayout(footer_layout)
        inner_layout.addWidget(content_widget)

    def save_appointment(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Invalid Entry", "Please provide a reason for the appointment.")
            return
            
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm")
        patient_id = self.patient_combo.currentData()
        
        self.db.add_appointment(patient_id, title, date, time)
        self.accept()
