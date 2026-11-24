from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QGroupBox, QStackedWidget)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
import qtawesome as qta
from ui.custom_dialogs import RecordDetailsDialog, ConfirmationDialog

class PatientListView(QWidget):
    patient_selected = Signal(int) # Emits patient_id

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Name or Owner...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #ddd;
                border-radius: 20px;
                background-color: white;
                font-size: 14px;
                color: #333;
            }
            QLineEdit:focus { border: 2px solid #3F51B5; }
        """)
        self.search_input.textChanged.connect(self.load_patients)
        search_layout.addWidget(self.search_input)
        
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#888'))
        self.refresh_btn.setIconSize(QSize(16, 16))
        self.refresh_btn.setToolTip("Refresh List")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; padding: 6px; }
            QPushButton:hover { background-color: #f0f0f0; border-radius: 4px; }
        """)
        self.refresh_btn.clicked.connect(self.load_patients)
        search_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Species", "Breed", "DOB", "Owner", "Contact"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.verticalHeader().setMinimumSectionSize(30)
        # Apply light theme style with transparency for watermark
        self.table.setStyleSheet("""
            QTableWidget { border: none; gridline-color: #eee; background-color: transparent; color: #333; }
            QHeaderView::section { background-color: rgba(249, 249, 249, 0.8); border: none; padding: 10px; font-weight: bold; color: #555; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; }
        """)
        self.table.cellClicked.connect(self.on_row_click)
        layout.addWidget(self.table)
        
        self.load_patients()

    def load_patients(self):
        query = self.search_input.text().strip()
        if query:
            patients = self.db.search_patients(query)
        else:
            patients = self.db.get_all_patients()
        
        self.table.setRowCount(0)
        for row_idx, patient in enumerate(patients):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(patient['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(patient['name']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(patient['species']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(patient['breed']))
            
            # Use 'keys()' check or try/except if column might not strictly exist in Row object immediately?
            # It should exist.
            dob_val = patient['dob'] if 'dob' in patient.keys() and patient['dob'] else "-"
            self.table.setItem(row_idx, 4, QTableWidgetItem(dob_val))
            
            self.table.setItem(row_idx, 5, QTableWidgetItem(patient['owner_name']))
            self.table.setItem(row_idx, 6, QTableWidgetItem(patient['contact_info']))
        
    def on_row_click(self, row, col):
        patient_id = int(self.table.item(row, 0).text())
        self.patient_selected.emit(patient_id)

class TreatmentListView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Global Treatment History")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Animal Name...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(300)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #ddd;
                border-radius: 20px;
                background-color: white;
                font-size: 14px;
                color: #333;
            }
            QLineEdit:focus { border: 2px solid #3F51B5; }
        """)
        self.search_input.textChanged.connect(self.load_treatments)
        header_layout.addWidget(self.search_input)
        
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#888'))
        self.refresh_btn.setIconSize(QSize(16, 16))
        self.refresh_btn.setToolTip("Refresh List")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; padding: 6px; }
            QPushButton:hover { background-color: #f0f0f0; border-radius: 4px; }
        """)
        self.refresh_btn.clicked.connect(self.load_treatments)
        header_layout.addWidget(self.refresh_btn)
        
        self.btn_view = QPushButton("View Details")
        self.btn_view.setIcon(qta.icon('fa5s.eye', color='white'))
        self.btn_view.setCursor(Qt.PointingHandCursor)
        self.btn_view.setEnabled(False)
        self.btn_view.setStyleSheet("""
            QPushButton {
                background-color: #3F51B5; color: white; padding: 8px 16px; border-radius: 15px; font-weight: bold;
            }
            QPushButton:disabled { background-color: #ccc; }
            QPushButton:hover { background-color: #303F9F; }
        """)
        self.btn_view.clicked.connect(self.on_view_details)
        header_layout.addWidget(self.btn_view)

        self.btn_delete = QPushButton("Delete Record")
        self.btn_delete.setIcon(qta.icon('fa5s.trash-alt', color='#ef5350'))
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setEnabled(False)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: transparent; border: 1px solid #ef5350; color: #ef5350; 
                padding: 7px 15px; border-radius: 15px; font-weight: bold;
            }
            QPushButton:disabled { border-color: #ccc; color: #ccc; }
            QPushButton:hover { background-color: rgba(239, 83, 80, 0.1); }
        """)
        self.btn_delete.clicked.connect(self.on_delete_record)
        header_layout.addWidget(self.btn_delete)
        
        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Patient", "Age", "Weight", "Diagnosis", "Details", "Cost"])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.verticalHeader().setMinimumSectionSize(30)
        # Apply light theme style with transparency for watermark
        self.table.setStyleSheet("""
            QTableWidget { border: none; gridline-color: #eee; background-color: transparent; color: #333; outline: none; }
            QHeaderView::section { background-color: rgba(249, 249, 249, 0.8); border: none; padding: 10px; font-weight: bold; color: #555; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; }
        """)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.cellDoubleClicked.connect(self.on_view_details)
        layout.addWidget(self.table)
        
        self.load_treatments()

    def load_treatments(self):
        query = self.search_input.text().strip()
        if query:
            treatments = self.db.search_treatments(query)
        else:
            treatments = self.db.get_all_treatments()

        self.table.setRowCount(0)
        for row, t in enumerate(treatments):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(t['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(t['date']))
            self.table.setItem(row, 2, QTableWidgetItem(t['patient_name']))
            self.table.setItem(row, 3, QTableWidgetItem(t['age'] if t['age'] else "-"))
            weight_str = f"{t['weight']} kg" if t['weight'] else "-"
            self.table.setItem(row, 4, QTableWidgetItem(weight_str))
            self.table.setItem(row, 5, QTableWidgetItem(t['diagnosis']))
            self.table.setItem(row, 6, QTableWidgetItem(t['treatment_details']))
            self.table.setItem(row, 7, QTableWidgetItem(f"Rs. {t['cost']:.2f}"))

    def on_selection_changed(self):
        has_selection = len(self.table.selectionModel().selectedRows()) > 0
        self.btn_view.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)

    def on_view_details(self, row=None, col=None):
        if row is None or isinstance(row, bool):
            row = self.table.currentRow()
            if row == -1: return
        
        data = {
            "Date": self.table.item(row, 1).text(),
            "Patient": self.table.item(row, 2).text(),
            "Age": self.table.item(row, 3).text(),
            "Weight": self.table.item(row, 4).text(),
            "Diagnosis": self.table.item(row, 5).text(),
            "Treatment Details": self.table.item(row, 6).text(),
            "Cost": self.table.item(row, 7).text()
        }
        
        dlg = RecordDetailsDialog(self, "Treatment Details", data, icon_name='fa5s.stethoscope')
        dlg.exec()

    def on_delete_record(self):
        row = self.table.currentRow()
        if row == -1: return
        
        treatment_id = int(self.table.item(row, 0).text())
        dialog = ConfirmationDialog(self, "Delete Record", "Are you sure you want to delete this specific treatment record?")
        
        if dialog.exec():
            if self.db.delete_treatment(treatment_id):
                self.load_treatments()

class PatientDetailView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_patient = None
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        # Page 0: Empty Placeholder
        self.placeholder_page = QLabel("Select a patient to view details")
        self.placeholder_page.setAlignment(Qt.AlignCenter)
        self.placeholder_page.setStyleSheet("color: #777; font-size: 16px;")
        self.stack.addWidget(self.placeholder_page)
        
        # Page 1: Details Content
        self.details_page = QWidget()
        details_layout = QVBoxLayout(self.details_page)
        details_layout.setContentsMargins(10, 10, 10, 10)
        
        # Info Group
        self.info_group = QGroupBox("Patient Details")
        info_layout = QFormLayout()
        self.lbl_name = QLabel("-")
        self.lbl_species = QLabel("-")
        self.lbl_breed = QLabel("-")
        self.lbl_owner = QLabel("-")
        self.lbl_contact = QLabel("-")
        
        info_layout.addRow("Name:", self.lbl_name)
        info_layout.addRow("Species:", self.lbl_species)
        info_layout.addRow("Breed:", self.lbl_breed)
        info_layout.addRow("Owner:", self.lbl_owner)
        info_layout.addRow("Contact:", self.lbl_contact)
        self.info_group.setLayout(info_layout)
        details_layout.addWidget(self.info_group)

        # History Table
        self.history_group = QGroupBox("Treatment History")
        history_layout = QVBoxLayout()
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["Date", "Age", "Weight", "Diagnosis", "Details", "Cost"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setWordWrap(True)
        self.history_table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.history_table.verticalHeader().setMinimumSectionSize(30)
        history_layout.addWidget(self.history_table)
        self.history_group.setLayout(history_layout)
        details_layout.addWidget(self.history_group)
        
        self.stack.addWidget(self.details_page)
        self.stack.setCurrentIndex(0)

    def load_patient(self, patient_id):
        self.current_patient = self.db.get_patient(patient_id)
        if not self.current_patient:
            return 

        self.lbl_name.setText(self.current_patient['name'])
        self.lbl_species.setText(self.current_patient['species'])
        self.lbl_breed.setText(self.current_patient['breed'])
        self.lbl_owner.setText(self.current_patient['owner_name'])
        self.lbl_contact.setText(self.current_patient['contact_info'])

        self.load_history(patient_id)
        self.stack.setCurrentIndex(1)

    def load_history(self, patient_id):
        treatments = self.db.get_patient_treatments(patient_id)
        self.history_table.setRowCount(0)
        for row, t in enumerate(treatments):
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(t['date']))
            self.history_table.setItem(row, 1, QTableWidgetItem(t['age'] if t['age'] else "-"))
            weight_str = f"{t['weight']} kg" if t['weight'] else "-"
            self.history_table.setItem(row, 2, QTableWidgetItem(weight_str))
            self.history_table.setItem(row, 3, QTableWidgetItem(t['diagnosis']))
            self.history_table.setItem(row, 4, QTableWidgetItem(t['treatment_details']))
            self.history_table.setItem(row, 5, QTableWidgetItem(f"Rs. {t['cost']:.2f}"))

class ComplaintListView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header Row
        header_layout = QHBoxLayout()
        header_lbl = QLabel("Complaint Management")
        header_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        header_layout.addWidget(header_lbl)
        header_layout.addStretch()
        
        self.btn_add = QPushButton("+ Register Complaint")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E65100, stop:1 #FF9800);
                color: white; padding: 10px 20px; border-radius: 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #EF6C00; }
        """)
        header_layout.addWidget(self.btn_add)

        self.btn_view = QPushButton("View Details")
        self.btn_view.setIcon(qta.icon('fa5s.eye', color='white'))
        self.btn_view.setCursor(Qt.PointingHandCursor)
        self.btn_view.setEnabled(False)
        self.btn_view.setStyleSheet("""
            QPushButton {
                background-color: #3F51B5; color: white; padding: 10px 20px; border-radius: 15px; font-weight: bold;
            }
            QPushButton:disabled { background-color: #ccc; }
            QPushButton:hover { background-color: #303F9F; }
        """)
        self.btn_view.clicked.connect(self.on_view_details)
        header_layout.addWidget(self.btn_view)

        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Customer", "Pet", "Date", "Status", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.verticalHeader().setMinimumSectionSize(30)
        self.table.setStyleSheet("""
            QTableWidget { border: none; gridline-color: #eee; background-color: transparent; color: #333; }
            QHeaderView::section { background-color: rgba(249, 249, 249, 0.8); border: none; padding: 10px; font-weight: bold; color: #555; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; }
        """)
        layout.addWidget(self.table)
        
        # Bottom Actions
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.btn_resolve = QPushButton("Mark Resolved")
        self.btn_resolve.setEnabled(False)
        self.btn_resolve.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:disabled { background-color: #ccc; }
        """)
        bottom_layout.addWidget(self.btn_resolve)
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setEnabled(False)
        self.btn_delete.setStyleSheet("""
            QPushButton { background-color: #f44336; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:disabled { background-color: #ccc; }
        """)
        bottom_layout.addWidget(self.btn_delete)
        
        layout.addLayout(bottom_layout)
        
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.cellDoubleClicked.connect(self.on_view_details)
        self.load_complaints()

    def load_complaints(self):
        complaints = self.db.get_all_complaints()
        self.table.setRowCount(0)
        for row, c in enumerate(complaints):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(c['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(c['owner_name']))
            self.table.setItem(row, 2, QTableWidgetItem(c['patient_name'] if c['patient_name'] else "N/A"))
            self.table.setItem(row, 3, QTableWidgetItem(c['date']))
            
            status_item = QTableWidgetItem(c['status'])
            if c['status'] == 'Resolved':
                status_item.setForeground(Qt.darkGreen)
            else:
                status_item.setForeground(Qt.red)
            self.table.setItem(row, 4, status_item)
            
            self.table.setItem(row, 5, QTableWidgetItem(c['description']))

    def on_selection_changed(self):
        has_selection = len(self.table.selectionModel().selectedRows()) > 0
        self.btn_resolve.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)
        self.btn_view.setEnabled(has_selection)

    def on_view_details(self, row=None, col=None):
        if row is None or isinstance(row, bool):
            row = self.table.currentRow()
            if row == -1: return
        
        data = {
            "ID": self.table.item(row, 0).text(),
            "Customer": self.table.item(row, 1).text(),
            "Pet": self.table.item(row, 2).text(),
            "Date": self.table.item(row, 3).text(),
            "Status": self.table.item(row, 4).text(),
            "Description": self.table.item(row, 5).text()
        }
        
        dlg = RecordDetailsDialog(self, "Complaint Details", data, icon_name='fa5s.exclamation-circle')
        dlg.exec()

class GceListView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Header Row
        header_layout = QHBoxLayout()
        header_lbl = QLabel("General Clinic Examination (GCE)")
        header_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        header_layout.addWidget(header_lbl)
        header_layout.addStretch()
        
        self.btn_add = QPushButton("+ New Examination")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3F51B5, stop:1 #7986CB);
                color: white; padding: 10px 20px; border-radius: 15px; font-weight: bold;
            }
            QPushButton:hover { opacity: 0.9; }
        """)
        header_layout.addWidget(self.btn_add)

        self.btn_view = QPushButton("View Details")
        self.btn_view.setIcon(qta.icon('fa5s.eye', color='white'))
        self.btn_view.setCursor(Qt.PointingHandCursor)
        self.btn_view.setEnabled(False)
        self.btn_view.setStyleSheet("""
            QPushButton {
                background-color: #3F51B5; color: white; padding: 10px 20px; border-radius: 15px; font-weight: bold;
            }
            QPushButton:disabled { background-color: #ccc; }
            QPushButton:hover { background-color: #303F9F; }
        """)
        self.btn_view.clicked.connect(self.on_view_details)
        header_layout.addWidget(self.btn_view)

        layout.addLayout(header_layout)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Patient Name...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(300)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #ddd;
                border-radius: 20px;
                background-color: white;
            }
            QLineEdit:focus { border: 2px solid #3F51B5; }
        """)
        self.search_input.textChanged.connect(self.load_gce)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Patient", "Temp (°C)", "Examination Details"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.verticalHeader().setMinimumSectionSize(30)
        self.table.setStyleSheet("""
            QTableWidget { border: none; gridline-color: #eee; background-color: transparent; }
            QHeaderView::section { background-color: #f9f9f9; border: none; padding: 10px; font-weight: bold; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; }
        """)
        layout.addWidget(self.table)
        
        # Bottom Actions
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setEnabled(False)
        self.btn_delete.setStyleSheet("""
            QPushButton { background-color: #f44336; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:disabled { background-color: #ccc; }
        """)
        bottom_layout.addWidget(self.btn_delete)
        layout.addLayout(bottom_layout)
        
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.cellDoubleClicked.connect(self.on_view_details)
        self.load_gce()

    def load_gce(self):
        query = self.search_input.text().strip()
        records = self.db.get_all_gce(query if query else None)
        self.table.setRowCount(0)
        for row, r in enumerate(records):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(r['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(r['date']))
            self.table.setItem(row, 2, QTableWidgetItem(r['patient_name']))
            
            temp_item = QTableWidgetItem(f"{r['temperature']}°C")
            # Color code temperature
            if r['temperature'] > 39.5: temp_item.setForeground(Qt.red)
            elif r['temperature'] < 37.5: temp_item.setForeground(Qt.blue)
            else: temp_item.setForeground(Qt.darkGreen)
            
            self.table.setItem(row, 3, temp_item)
            self.table.setItem(row, 4, QTableWidgetItem(r['description']))

    def on_selection_changed(self):
        has_selection = len(self.table.selectionModel().selectedRows()) > 0
        self.btn_delete.setEnabled(has_selection)
        self.btn_view.setEnabled(has_selection)

    def on_view_details(self, row=None, col=None):
        if row is None or isinstance(row, bool):
            row = self.table.currentRow()
            if row == -1: return
        
        data = {
            "ID": self.table.item(row, 0).text(),
            "Date": self.table.item(row, 1).text(),
            "Patient": self.table.item(row, 2).text(),
            "Temperature": self.table.item(row, 3).text(),
            "Examination Details": self.table.item(row, 4).text()
        }
        
        dlg = RecordDetailsDialog(self, "Examination Details", data, icon_name='fa5s.notes-medical')
        dlg.exec()

from PySide6.QtWidgets import QFormLayout
