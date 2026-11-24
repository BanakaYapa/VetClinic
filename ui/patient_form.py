import qtawesome as qta
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QDialogButtonBox, QMessageBox, QDateEdit, QFrame, QLabel, QHBoxLayout)
from PySide6.QtCore import QRegularExpression, QDate, Qt, QSize
from PySide6.QtGui import QRegularExpressionValidator, QLinearGradient, QColor, QPalette

class PatientForm(QDialog):
    def __init__(self, parent=None, db_manager=None, patient_data=None):
        super().__init__(parent)
        self.db = db_manager
        self.patient_data = patient_data
        
        self.setWindowTitle("Edit Client" if patient_data else "Add New Client")
        self.setFixedWidth(500)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Main containing frame for drop shadow and styling
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

        # 1. Header with Gradient
        self.header = QFrame()
        self.header.setFixedHeight(100)
        self.header.setObjectName("HeaderFrame")
        self.header.setStyleSheet("""
            #HeaderFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #43A047, stop:1 #66BB6A);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon('fa5s.user-plus' if not patient_data else 'fa5s.user-edit', color='white').pixmap(QSize(40, 40)))
        header_layout.addWidget(icon_lbl)
        
        title_lbl = QLabel("Edit Client Details" if patient_data else "Register New Client")
        title_lbl.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        # Close button in header
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; color: white; font-size: 18px; border: none; 
            }
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

        # Modern Shared Stylesheet
        self.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #555;
                font-weight: 500;
            }
            QLineEdit, QDateEdit, QComboBox {
                background-color: #fcfcfc;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 12px;
                color: #333;
                font-size: 14px;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 2px solid #43A047;
                background-color: #fff;
            }
            
            /* QDateEdit & QCalendarWidget Styling */
            QDateEdit::drop-down {
                border: none;
                width: 30px;
                image: url(none); /* Remove default */
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #43A047;
                margin-right: 10px;
            }
            
            QCalendarWidget QWidget {
                alternate-background-color: #f2f2f2;
                background-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #43A047;
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
                selection-background-color: #43A047;
                selection-color: white;
                outline: 0;
            }
            QCalendarWidget QHeaderView {
                background-color: #f9f9f9;
            }

            /* QComboBox Styling */
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #43A047;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: #43A047;
                selection-color: white;
                outline: 0;
                border-radius: 8px;
            }
        """)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Buddy")
        self.species_input = QLineEdit()
        self.species_input.setPlaceholderText("e.g. Canine")
        self.breed_input = QLineEdit()
        self.breed_input.setPlaceholderText("e.g. Golden Retriever")
        
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setDate(QDate.currentDate())
        
        self.owner_input = QLineEdit()
        self.owner_input.setPlaceholderText("e.g. John Doe")
        
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("+91 98765 43210")
        phone_regex = QRegularExpression(r"^[0-9\+\-\s]*$")
        validator = QRegularExpressionValidator(phone_regex, self.contact_input)
        self.contact_input.setValidator(validator)

        form_layout.addRow("Pet Name", self.name_input)
        form_layout.addRow("Species", self.species_input)
        form_layout.addRow("Breed", self.breed_input)
        form_layout.addRow("Date of Birth", self.dob_input)
        form_layout.addRow("Owner Name", self.owner_input)
        form_layout.addRow("Contact Info", self.contact_input)

        if patient_data:
            self.name_input.setText(patient_data['name'])
            self.species_input.setText(patient_data['species'])
            self.breed_input.setText(patient_data['breed'])
            self.owner_input.setText(patient_data['owner_name'])
            self.contact_input.setText(patient_data['contact_info'])
            if patient_data.get('dob'):
                 self.dob_input.setDate(QDate.fromString(patient_data['dob'], "yyyy-MM-dd"))

        content_layout.addLayout(form_layout)
        
        # 3. Dynamic Footer Buttons
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
        
        self.save_btn = QPushButton("Update Profile" if patient_data else "Save Client")
        self.save_btn.setMinimumWidth(140)
        self.save_btn.clicked.connect(self.save_patient)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #43A047, stop:1 #66BB6A);
                color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #388E3C, stop:1 #4CAF50); }
            QPushButton:pressed { background: #2E7D32; }
        """)
        footer_layout.addWidget(self.save_btn)
        
        content_layout.addLayout(footer_layout)
        inner_layout.addWidget(content_widget)

    def save_patient(self):
        name = self.name_input.text().strip()
        species = self.species_input.text().strip()
        owner = self.owner_input.text().strip()
        dob = self.dob_input.date().toString("yyyy-MM-dd")

        if not name or not species or not owner:
            QMessageBox.warning(self, "Missing Fields", "Please provide a Name, Species, and Owner Name.")
            return

        try:
            if self.patient_data:
                self.db.update_patient(
                    patient_id=self.patient_data['id'],
                    name=name,
                    species=species,
                    breed=self.breed_input.text().strip(),
                    owner_name=owner,
                    contact_info=self.contact_input.text().strip(),
                    dob=dob
                )
            else:
                self.db.add_patient(
                    name=name,
                    species=species,
                    breed=self.breed_input.text().strip(),
                    owner_name=owner,
                    contact_info=self.contact_input.text().strip(),
                    dob=dob
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "System Error", f"An error occurred while saving: {e}")

from PySide6.QtWidgets import QPushButton, QWidget
