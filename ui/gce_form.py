import qtawesome as qta
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QMessageBox, QDateEdit, QTextEdit, QFrame, QLabel, QHBoxLayout, QPushButton, QWidget, QComboBox, QDoubleSpinBox)
from PySide6.QtCore import QDate, Qt, QSize

class GceForm(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db = db_manager
        
        self.setWindowTitle("General Clinic Examination")
        self.setFixedWidth(550)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Indigo theme for GCE
        self.primary_color = "#3F51B5"
        self.secondary_color = "#7986CB"

        # Main container
        self.container = QFrame(self)
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet(f"""
            #MainContainer {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #ddd;
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.container)
        
        inner_layout = QVBoxLayout(self.container)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        # 1. Header with Gradient (Indigo)
        self.header = QFrame()
        self.header.setFixedHeight(100)
        self.header.setObjectName("HeaderFrame")
        self.header.setStyleSheet(f"""
            #HeaderFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.primary_color}, stop:1 {self.secondary_color});
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
        """)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon('fa5s.stethoscope', color='white').pixmap(QSize(40, 40)))
        header_layout.addWidget(icon_lbl)
        
        title_lbl = QLabel("General Examination (GCE)")
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

        self.setStyleSheet(f"""
            QLabel {{ font-size: 13px; color: #555; font-weight: 500; }}
            QLineEdit, QTextEdit, QDateEdit, QComboBox, QDoubleSpinBox {{
                background-color: #fcfcfc;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 12px;
                color: #333;
                font-size: 14px;
            }}
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {self.primary_color};
                background-color: #fff;
            }}
            
            /* Stylish Calendar & Dropdowns */
            QDateEdit::drop-down, QComboBox::drop-down {{ border: none; width: 30px; }}
            QDateEdit::down-arrow, QComboBox::down-arrow {{
                image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid {self.primary_color}; margin-right: 10px;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{ background-color: {self.primary_color}; }}
        """)

        # Fields
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        self.patient_combo = QComboBox()
        self.patient_combo.addItem("Select Patient...", None)
        patients = self.db.get_all_patients()
        for p in patients:
            self.patient_combo.addItem(f"{p['name']} ({p['owner_name']})", p['id'])

        self.temp_input = QDoubleSpinBox()
        self.temp_input.setRange(30.0, 45.0)
        self.temp_input.setValue(38.0)
        self.temp_input.setSuffix(" °C")
        self.temp_input.setDecimals(1)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter physical findings, observations...")

        form_layout.addRow("Date", self.date_input)
        form_layout.addRow("Patient", self.patient_combo)
        form_layout.addRow("Temperature", self.temp_input)
        form_layout.addRow("Examinations", self.desc_input)

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
        
        self.save_btn = QPushButton("Save Examination")
        self.save_btn.setMinimumWidth(160)
        self.save_btn.clicked.connect(self.save_gce)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.primary_color}, stop:1 {self.secondary_color});
                color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)
        footer_layout.addWidget(self.save_btn)
        
        content_layout.addLayout(footer_layout)
        inner_layout.addWidget(content_widget)

    def save_gce(self):
        patient_id = self.patient_combo.currentData()
        date = self.date_input.date().toString("yyyy-MM-dd")
        temp = self.temp_input.value()
        desc = self.desc_input.toPlainText().strip()

        if patient_id is None:
            QMessageBox.warning(self, "Invalid Entry", "Please select a patient.")
            return
        
        if not desc:
            QMessageBox.warning(self, "Invalid Entry", "Please provide examination details.")
            return

        if self.db.add_gce(patient_id, date, temp, desc):
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save GCE record.")
