from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QStackedWidget, QLabel, QFrame, QMenu, QWidgetAction, QMessageBox)
from PySide6.QtCore import Qt, QDate, QSize
import qtawesome as qta
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.patient_form import PatientForm
from ui.treatment_form import TreatmentForm
from ui.appointment_form import AppointmentForm
from ui.complaint_form import ComplaintForm
from ui.gce_form import GceForm
from ui.views import PatientListView, PatientDetailView, TreatmentListView, ComplaintListView, GceListView
from ui.schedule_view import ScheduleView
from ui.custom_dialogs import ConfirmationDialog
from ui.toast import Toast

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.setWindowTitle("Veterinary Clinic Management")
        self.resize(1200, 800)
        self.db = db_manager
        
        # Main Layout: Sidebar + Content
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.page_selected.connect(self.switch_page)
        main_layout.addWidget(self.sidebar)

        # 2. Right Side (Top Bar + Stacked Content)
        right_panel = QWidget()
        right_panel.setObjectName("MainContentPanel")
        
        # Watermark Style
        # Use ID selector to prevent cascading to children
        right_panel.setStyleSheet("""
            #MainContentPanel {
                background-color: #f4f7f6;
                background-image: url(assets/watermark_bg.png);
                background-position: center;
                background-repeat: no-repeat;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Top Bar
        self.setup_top_bar(right_layout)

        # Content Stack
        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack)
        
        # Page 1: Dashboard
        self.dashboard_page = Dashboard(self.db)
        self.stack.addWidget(self.dashboard_page)
        
        # Page 2: Clients (Split View: List + Details)
        self.clients_page = QWidget()
        self.setup_clients_page()
        self.stack.addWidget(self.clients_page)

        # Page 3: Treatments (Global List)
        self.treatments_page = TreatmentListView(self.db)
        self.treatments_page.treatments_changed.connect(self.dashboard_page.refresh)
        self.stack.addWidget(self.treatments_page)

        # Page 4: Schedule
        self.schedule_page = ScheduleView(self.db)
        self.schedule_page.appointments_changed.connect(self.dashboard_page.refresh)
        self.stack.addWidget(self.schedule_page)

        # Page 5+: Placeholders
        self.stack.addWidget(self.create_placeholder("Medicines"))
        self.stack.addWidget(self.create_placeholder("Inventory"))
        self.stack.addWidget(self.create_placeholder("Reports"))
        
        # Page 8: Complaints
        self.complaints_page = ComplaintListView(self.db)
        self.complaints_page.btn_add.clicked.connect(self.open_add_complaint)
        self.complaints_page.btn_resolve.clicked.connect(self.resolve_complaint)
        self.complaints_page.btn_delete.clicked.connect(self.delete_complaint)
        self.stack.addWidget(self.complaints_page)
        
        # Page 9: GCE
        self.gce_page = GceListView(self.db)
        self.gce_page.btn_add.clicked.connect(self.open_add_gce)
        self.gce_page.btn_delete.clicked.connect(self.delete_gce_record)
        self.stack.addWidget(self.gce_page)
        
        self.stack.addWidget(self.create_placeholder("Employees"))
        
        main_layout.addWidget(right_panel)
        
        # Default styling for dialogs (global override)
        self.apply_global_styles()

    def setup_top_bar(self, layout):
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("background-color: white; border-bottom: 1px solid #ddd;")
        
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(20, 0, 20, 0)
        
        # Hamburger / Title
        title = QLabel("Dashboard") # Dynamic based on page?
        title.setStyleSheet("font-size: 18px; color: #555; background: transparent;")
        self.lbl_page_title = title
        tb_layout.addWidget(title)
        
        tb_layout.addStretch()
        
        # Notification Actions (Bell)
        btn_notif = QPushButton("🔔")
        btn_notif.setCursor(Qt.PointingHandCursor)
        btn_notif.setStyleSheet("""
            QPushButton { border: none; font-size: 20px; color: #555; padding: 5px; }
            QPushButton:hover { color: #1976D2; }
        """)
        btn_notif.clicked.connect(self.show_notifications)
        tb_layout.addWidget(btn_notif)
        
        # Admin User with Dropdown
        btn_user = QPushButton("Admin")
        btn_user.setCursor(Qt.PointingHandCursor)
        btn_user.setStyleSheet("""
            QPushButton { 
                border: none; font-weight: bold; color: #333; padding: 5px 15px; border-radius: 12px;
                background-color: transparent;
            }
            QPushButton:hover { background-color: #f0f0f0; }
            QPushButton::menu-indicator { image: none; } /* Hide default arrow */
        """)
        
        # Create Dropdown Menu
        admin_menu = QMenu(self)
        admin_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        # Embed Stylish Button using QWidgetAction
        clear_cache_action = QWidgetAction(admin_menu)
        
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(5, 5, 5, 5)
        
        stylish_btn = QPushButton(" Clear Cache")
        stylish_btn.setIcon(qta.icon("fa5s.broom", color="#ff7961"))
        stylish_btn.setCursor(Qt.PointingHandCursor)
        stylish_btn.setStyleSheet("""
            QPushButton { 
                background-color: rgba(255, 121, 97, 0.1);
                border: 1px solid rgba(255, 121, 97, 0.3);
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                color: #ff7961;
            }
            QPushButton:hover {
                background-color: rgba(255, 121, 97, 0.2);
            }
        """)
        
        def on_clear_click():
            admin_menu.close()
            self.clear_cache()
            
        stylish_btn.clicked.connect(on_clear_click)
        btn_layout.addWidget(stylish_btn)
        
        clear_cache_action.setDefaultWidget(btn_container)
        admin_menu.addAction(clear_cache_action)
        
        btn_user.setMenu(admin_menu)
        tb_layout.addWidget(btn_user)

        layout.addWidget(top_bar)

    def show_notifications(self):
        today = QDate.currentDate().toString("yyyy-MM-dd")
        appts = self.db.get_appointments_by_date(today)
        scheduled_count = sum(1 for a in appts if a.get('status', 'Scheduled') == 'Scheduled')
        open_complaints = sum(1 for c in self.db.get_all_complaints() if c.get('status') != 'Resolved')

        parts = []
        if appts:
            parts.append(f"{len(appts)} appointment{'s' if len(appts) != 1 else ''} today ({scheduled_count} pending)")
        else:
            parts.append("No appointments scheduled today")

        if open_complaints:
            parts.append(f"{open_complaints} open complaint{'s' if open_complaints != 1 else ''}")

        Toast.show_message(self, " • ".join(parts), duration=4000)

    def show_admin_info(self):
        # User requested to remove alerts
        pass

    def setup_clients_page(self):
        layout = QVBoxLayout(self.clients_page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Top Actions Row
        actions_layout = QHBoxLayout()
        
        # Add Patient Button
        btn_add = QPushButton("+ Add New Client")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4CAF50, stop:1 #66BB6A);
                color: white; 
                padding: 10px 20px; 
                border-radius: 15px; 
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #43A047, stop:1 #57AC5C);
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        btn_add.clicked.connect(self.open_add_patient)
        actions_layout.addWidget(btn_add)
        
        # Add Treatment Button
        self.btn_add_treatment = QPushButton("+ Add Treatment")
        self.btn_add_treatment.setEnabled(False)
        self.btn_add_treatment.setCursor(Qt.PointingHandCursor)
        self.btn_add_treatment.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976D2, stop:1 #2196F3);
                color: white; 
                padding: 10px 20px; 
                border-radius: 15px; 
                font-weight: bold; 
                font-size: 14px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1565C0, stop:1 #1E88E5);
            }
            QPushButton:disabled { 
                background: #ccc; 
            }
        """)
        self.btn_add_treatment.clicked.connect(self.open_add_treatment)
        actions_layout.addWidget(self.btn_add_treatment)

        
        actions_layout.addStretch() # Push buttons to left
        layout.addLayout(actions_layout)

        # Patient List (Full Width)
        list_container = QWidget()
        # Transparent background for watermark visibility
        list_container.setStyleSheet("background-color: transparent; border-radius: 8px;")
        lc_layout = QVBoxLayout(list_container)
        
        self.patient_list = PatientListView(self.db)
        self.patient_list.patient_selected.connect(self.on_patient_selected)
        self.patient_list.table.setFocusPolicy(Qt.NoFocus)
        # Remove dark style for table to fit light theme
        self.patient_list.table.setStyleSheet("""
            QTableWidget { border: none; gridline-color: #eee; background-color: transparent; color: #333; outline: none; }
            QHeaderView::section { background-color: rgba(249, 249, 249, 0.8); border: none; padding: 10px; font-weight: bold; color: #555; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; }
            QTableWidget::item:selected { background-color: rgba(227, 242, 253, 0.8); color: #1976D2; }
        """)
        lc_layout.addWidget(self.patient_list)
        
        layout.addWidget(list_container)
        
        # Bottom Actions Row
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch() # Push to right
        
        # Edit Client Button
        self.btn_edit_client = QPushButton(" Edit Client")
        self.btn_edit_client.setIcon(qta.icon('fa5s.edit', color='white'))
        self.btn_edit_client.setIconSize(QSize(16, 16))
        self.btn_edit_client.setEnabled(False)
        self.btn_edit_client.setCursor(Qt.PointingHandCursor)
        self.btn_edit_client.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF9800, stop:1 #FFB74D);
                color: white; 
                padding: 10px 20px; 
                border-radius: 15px; 
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F57C00, stop:1 #FFA726);
            }
            QPushButton:disabled { 
                background: #ccc; 
            }
        """)
        self.btn_edit_client.clicked.connect(self.edit_current_client)
        bottom_layout.addWidget(self.btn_edit_client)

        # Delete Client Button
        self.btn_delete_client = QPushButton(" Delete Client")
        self.btn_delete_client.setIcon(qta.icon('fa5s.trash-alt', color='white'))
        self.btn_delete_client.setIconSize(QSize(16, 16))
        self.btn_delete_client.setEnabled(False) # Disabled by default
        self.btn_delete_client.setCursor(Qt.PointingHandCursor)
        self.btn_delete_client.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef5350, stop:1 #e53935);
                color: white; 
                padding: 10px 20px; 
                border-radius: 15px; 
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d32f2f, stop:1 #c62828);
            }
            QPushButton:disabled { 
                background: #ccc; 
            }
        """)
        self.btn_delete_client.clicked.connect(self.delete_current_client)
        bottom_layout.addWidget(self.btn_delete_client)
        
        layout.addLayout(bottom_layout)
        
        self.selected_patient_id = None

    def create_placeholder(self, text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        lbl = QLabel(f"{text} Page\n(Under Construction)")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 24px; color: #ccc; font-weight: bold;")
        layout.addWidget(lbl)
        return widget

    def switch_page(self, page_id):
        page_map = {
            "dashboard": 0,
            "clients": 1,
            "treatments": 2,
            "schedule": 3,
            "medicines": 4,
            "inventory": 5,
            "reports": 6,
            "complaints": 7,
            "gce": 8,
            "employees": 9
        }
        idx = page_map.get(page_id, 0)
        self.stack.setCurrentIndex(idx)
        
        # Determine Title
        titles = {
            "gce": "GCE",
            "dashboard": "Dashboard",
            "clients": "Clients",
            "treatments": "Treatments",
            "schedule": "Schedule",
            "medicines": "Medicines",
            "inventory": "Inventory",
            "reports": "Reports",
            "complaints": "Complaints",
            "employees": "Employees"
        }
        self.lbl_page_title.setText(titles.get(page_id, page_id.capitalize()))
        
        # Auto-refresh active page data
        if page_id == "dashboard":
            self.dashboard_page.refresh()
        elif page_id == "clients":
            self.patient_list.load_patients()
            self.selected_patient_id = None
            self.btn_add_treatment.setEnabled(False)
            self.btn_edit_client.setEnabled(False)
            self.btn_delete_client.setEnabled(False)
        elif page_id == "treatments":
            self.treatments_page.load_treatments()
        elif page_id == "schedule":
            self.schedule_page.load_appointments()
        elif page_id == "complaints":
            self.complaints_page.load_complaints()
        elif page_id == "gce":
            self.gce_page.load_gce()

    def open_add_patient(self):
        form = PatientForm(self, self.db)
        if form.exec():
            self.patient_list.load_patients()
            self.dashboard_page.refresh()
            Toast.show_message(self, "New client added successfully.")
            
    def edit_current_client(self):
        if not self.selected_patient_id:
            return
        
        patient = self.db.get_patient(self.selected_patient_id)
        if patient:
            form = PatientForm(self, self.db, patient_data=dict(patient))
            if form.exec():
                self.patient_list.load_patients()
                self.dashboard_page.refresh()
                self.selected_patient_id = None
                self.btn_add_treatment.setEnabled(False)
                self.btn_delete_client.setEnabled(False)
                self.btn_edit_client.setEnabled(False)
                Toast.show_message(self, "Client profile updated.")

    def open_add_treatment(self):
        if not self.selected_patient_id:
            return
        
        form = TreatmentForm(self, self.db, self.selected_patient_id)
        if form.exec():
            self.dashboard_page.refresh()
            Toast.show_message(self, "Treatment record saved.")

    def on_patient_selected(self, patient_id):
        self.selected_patient_id = patient_id
        self.btn_add_treatment.setEnabled(True)
        self.btn_edit_client.setEnabled(True)
        self.btn_delete_client.setEnabled(True)

    def delete_current_client(self):
        if not self.selected_patient_id:
            return
            
        dialog = ConfirmationDialog(self, "Confirm Delete", 
                                  "Are you sure you want to delete this client?\nThis will permanently delete profile, treatments, GCE exams, and appointments.")
        
        if dialog.exec():
            if self.db.delete_patient(self.selected_patient_id):
                self.patient_list.load_patients()
                self.dashboard_page.refresh()
                self.selected_patient_id = None
                self.btn_add_treatment.setEnabled(False)
                self.btn_edit_client.setEnabled(False)
                self.btn_delete_client.setEnabled(False)
                Toast.show_message(self, "Client deleted.")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete patient.")

    def open_add_complaint(self):
        form = ComplaintForm(self, self.db)
        if form.exec():
            self.complaints_page.load_complaints()
            Toast.show_message(self, "Complaint registered.")

    def resolve_complaint(self):
        selection = self.complaints_page.table.selectionModel().selectedRows()
        if not selection: return
        complaint_id = int(self.complaints_page.table.item(selection[0].row(), 0).text())
        if self.db.update_complaint_status(complaint_id, "Resolved"):
            self.complaints_page.load_complaints()
            Toast.show_message(self, "Complaint marked as resolved.")

    def delete_complaint(self):
        selection = self.complaints_page.table.selectionModel().selectedRows()
        if not selection: return
        
        dialog = ConfirmationDialog(self, "Confirm Delete", "Permanently delete this complaint record?")
        if dialog.exec():
            complaint_id = int(self.complaints_page.table.item(selection[0].row(), 0).text())
            if self.db.delete_complaint(complaint_id):
                self.complaints_page.load_complaints()
                Toast.show_message(self, "Complaint deleted.")

    def open_add_gce(self):
        form = GceForm(self, self.db)
        if form.exec():
            self.gce_page.load_gce()
            Toast.show_message(self, "GCE examination saved.")

    def delete_gce_record(self):
        selection = self.gce_page.table.selectionModel().selectedRows()
        if not selection: return
        
        dialog = ConfirmationDialog(self, "Confirm Delete", "Permanently delete this GCE record?")
        if dialog.exec():
            gce_id = int(self.gce_page.table.item(selection[0].row(), 0).text())
            if self.db.delete_gce(gce_id):
                self.gce_page.load_gce()
                Toast.show_message(self, "GCE record deleted.")

    def clear_cache(self):
        """Clears temporary files (e.g. __pycache__)."""
        dialog = ConfirmationDialog(self, "Clear App Cache", 
                                  "This will clear temporary files and session data.\n"
                                  "No patient or clinical records will be affected.\n\n"
                                  "Proceed?")
        
        if dialog.exec():
            import shutil
            import os
            
            cleared_count = 0
            # 1. Clear __pycache__ and .pyc files
            for root, dirs, files in os.walk("."):
                # Skip virtualenv and git internals
                dirs[:] = [d for d in dirs if d not in (".venv", "venv", ".git")]
                for d in list(dirs):
                    if d == "__pycache__":
                        shutil.rmtree(os.path.join(root, d))
                        dirs.remove(d)
                        cleared_count += 1
                for f in files:
                    if f.endswith(".pyc"):
                        try:
                            os.remove(os.path.join(root, f))
                            cleared_count += 1
                        except OSError:
                            pass
            
            Toast.show_message(self, f"Application cache ({cleared_count} items) cleared.")

    def apply_global_styles(self):
        # QDialog styles or other global adjustments if needed
        pass
