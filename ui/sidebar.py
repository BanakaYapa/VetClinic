from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QSpacerItem, QSizePolicy, QHBoxLayout)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon, QFont, QPixmap
import qtawesome as qta

class Sidebar(QWidget):
    page_selected = Signal(str) # Emits page name (e.g., "dashboard", "clients")

    def __init__(self):
        super().__init__()
        self.setFixedWidth(250)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a; 
                color: #ffffff;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 15px 20px;
                font-size: 14px;
                color: #a0a0a0;
            }
            QPushButton:hover {
                background-color: #333333;
                color: white;
            }
            QPushButton:checked {
                background-color: #e53935; /* Red accent like screenshot */
                color: white;
                border-left: 4px solid #ff7961;
            }
            QLabel {
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(220)
        header.setStyleSheet("background-color: #000000;")
        header_main_layout = QVBoxLayout(header)
        header_main_layout.setContentsMargins(10, 20, 10, 10)
        
        # Branding (Logo + Name)
        branding = QWidget()
        branding_layout = QVBoxLayout(branding)
        branding_layout.setContentsMargins(0, 0, 0, 0)
        branding_layout.setSpacing(5)
        branding_layout.setAlignment(Qt.AlignCenter)
        
        # Logo
        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_path = "assets/logo.jpg" 
        import os
        if os.path.exists(logo_path):
             pixmap = QPixmap(logo_path)
             # Scale to fit (Bigger now)
             pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
             logo_lbl.setPixmap(pixmap)
        else:
             logo_lbl.setText("Logo")
        
        # Hospital Name
        name_lbl = QLabel("VET VIBE")
        # Using the blue color from the logo roughly
        name_lbl.setStyleSheet("font-size: 24px; font-weight: 900; color: #00ADEF; letter-spacing: 1px;")
        name_lbl.setAlignment(Qt.AlignCenter)
        
        tagline_lbl = QLabel("ANIMAL HOSPITAL")
        tagline_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #888; letter-spacing: 2px;")
        tagline_lbl.setAlignment(Qt.AlignCenter)
        
        branding_layout.addWidget(logo_lbl)
        branding_layout.addWidget(name_lbl)
        branding_layout.addWidget(tagline_lbl)
        
        header_main_layout.addWidget(branding)
        
        # User Name
        user_lbl = QLabel("Dr. Thiyangi Madushika")
        user_lbl.setAlignment(Qt.AlignCenter)
        user_lbl.setStyleSheet("font-size: 12px; color: #666; margin-top: 5px;")
        header_main_layout.addWidget(user_lbl)

        layout.addWidget(header)

        # 2. Navigation
        self.btn_group = []
        
        self.add_nav_button(layout, "Dashboard", "dashboard", "fa5s.tachometer-alt", checked=True)
        self.add_nav_button(layout, "Clients", "clients", "fa5s.users")
        self.add_nav_button(layout, "Treatments", "treatments", "fa5s.stethoscope")
        #self.add_nav_button(layout, "Medicines", "medicines", "fa5s.medkit")
        #self.add_nav_button(layout, "Inventory", "inventory", "fa5s.cubes")
        #self.add_nav_button(layout, "Reports", "reports", "fa5s.chart-bar")
        self.add_nav_button(layout, "Schedule", "schedule", "fa5s.calendar-alt")
        self.add_nav_button(layout, "Complaints", "complaints", "fa5s.exclamation-circle")
        self.add_nav_button(layout, "GCE", "gce", "fa5s.stethoscope")
        
        # Spacer to push everything up
        layout.addStretch()
        
        self.add_nav_button(layout, "Employees", "employees", "fa5s.id-card")

        # Footer
        footer_lbl = QLabel("Ver 1.0")
        footer_lbl.setAlignment(Qt.AlignCenter)
        footer_lbl.setStyleSheet("color: #444; padding: 10px;")
        layout.addWidget(footer_lbl)

    def add_nav_button(self, layout, text, page_id, icon_name, checked=False):
        icon = qta.icon(icon_name, color="#a0a0a0")
        btn = QPushButton(text)
        btn.setIcon(icon)
        btn.setIconSize(QSize(20, 20))
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setProperty("page_id", page_id)
        btn.clicked.connect(lambda: self.on_btn_clicked(btn))
        
        # Helper to change icon color on check state
        # Note: Dynamic icon coloring in PySide pushbuttons via QSS is tricky, 
        # so for now we stick to a static color or simple switch.
        
        layout.addWidget(btn)
        self.btn_group.append(btn)

    def on_btn_clicked(self, clicked_btn):
        for btn in self.btn_group:
            btn.setChecked(False)
        clicked_btn.setChecked(True)
        self.page_selected.emit(clicked_btn.property("page_id"))
