import qtawesome as qta
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QDialogButtonBox, QMessageBox, QDateEdit, QTextEdit, 
                               QDoubleSpinBox, QFrame, QLabel, QHBoxLayout, QPushButton, QWidget)
from PySide6.QtCore import QDate, Qt, QSize

class TreatmentForm(QDialog):
    def __init__(self, parent=None, db_manager=None, patient_id=None):
        super().__init__(parent)
        self.db = db_manager
        self.patient_id = patient_id
        if not self.patient_id:
            raise ValueError("Patient ID is required for TreatmentForm")

        self.setWindowTitle("Add Treatment")
        self.setFixedWidth(550)
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

        # 1. Header with Gradient (Blue)
        self.header = QFrame()
        self.header.setFixedHeight(100)
        self.header.setObjectName("HeaderFrame")
        self.header.setStyleSheet("""
            #HeaderFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1976D2, stop:1 #2196F3);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon('fa5s.file-medical', color='white').pixmap(QSize(40, 40)))
        header_layout.addWidget(icon_lbl)
        
        title_lbl = QLabel("Record Treatment")
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
            QLineEdit, QTextEdit, QDateEdit, QDoubleSpinBox {
                background-color: #fcfcfc;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 12px;
                color: #333;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QDoubleSpinBox:focus {
                border: 2px solid #1976D2;
                background-color: #fff;
            }

            /* QDateEdit & QCalendarWidget Styling */
            QDateEdit::drop-down {
                border: none;
                width: 30px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #1976D2;
                margin-right: 10px;
            }
            
            QCalendarWidget QWidget {
                alternate-background-color: #f2f2f2;
                background-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #1976D2;
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
                selection-background-color: #1976D2;
                selection-color: white;
                outline: 0;
            }
            QCalendarWidget QHeaderView {
                background-color: #f9f9f9;
            }

            /* QDoubleSpinBox Styling (Up/Down Buttons) */
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background: #fcfcfc;
                border-left: 1px solid #e0e0e0;
                width: 25px;
            }
            QDoubleSpinBox::up-button { border-top-right-radius: 8px; }
            QDoubleSpinBox::down-button { border-bottom-right-radius: 8px; }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover { background: #f0f0f0; }
            
            QDoubleSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid #1976D2;
            }
            QDoubleSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #1976D2;
            }
        """)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        
        self.diagnosis_input = QLineEdit()
        self.diagnosis_input.setPlaceholderText("Enter diagnosis...")
        
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Current age of patient")
        
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0, 500.0)
        self.weight_input.setSuffix(" kg")
        self.weight_input.setDecimals(1)
        
        self.details_input = QTextEdit()
        self.details_input.setPlaceholderText("Treatment details and medications...")
        
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 99999.99)
        self.cost_input.setPrefix("Rs. ")
        
        form_layout.addRow("Date", self.date_input)
        form_layout.addRow("Diagnosis", self.diagnosis_input)
        form_layout.addRow("Patient Age", self.age_input)
        form_layout.addRow("Weight", self.weight_input)
        form_layout.addRow("Details", self.details_input)
        form_layout.addRow("Cost", self.cost_input)

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
        
        self.save_btn = QPushButton("Add Record")
        self.save_btn.setMinimumWidth(140)
        self.save_btn.clicked.connect(self.save_treatment)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976D2, stop:1 #2196F3);
                color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1565C0, stop:1 #1E88E5); }
        """)
        footer_layout.addWidget(self.save_btn)
        
        content_layout.addLayout(footer_layout)
        inner_layout.addWidget(content_widget)

    def save_treatment(self):
        diagnosis = self.diagnosis_input.text().strip()
        details = self.details_input.toPlainText().strip()
        age = self.age_input.text().strip()
        weight = self.weight_input.value()
        
        if not diagnosis:
             QMessageBox.warning(self, "Invalid Form", "Please provide a diagnosis.")
             return

        try:
            self.db.add_treatment(
                patient_id=self.patient_id,
                date=self.date_input.date().toString("yyyy-MM-dd"),
                diagnosis=diagnosis,
                treatment_details=details,
                cost=self.cost_input.value(),
                weight=weight if weight > 0 else None,
                age=age if age else None
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save record: {e}")
