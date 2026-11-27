from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget, 
                               QListWidget, QListWidgetItem, QLabel, QPushButton, 
                               QSplitter, QFrame, QMessageBox, QComboBox)
from PySide6.QtCore import Qt, QDate, QLocale, Signal
from PySide6.QtGui import QColor, QFont, QIcon
import qtawesome as qta
from ui.appointment_form import AppointmentForm
from ui.custom_dialogs import ConfirmationDialog


class StylishCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGridVisible(False)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader) # Remove week numbers
        self.setNavigationBarVisible(False)
        
        # Base style (the rest is handled by paintCell or parent stylesheet)
        self.setStyleSheet("""
            QCalendarWidget { border: none; background-color: white; }
            QCalendarWidget QWidget { alternate-background-color: white; }
            QAbstractItemView {
                color: #333;
                background-color: white;
                selection-background-color: transparent; /* We handle selection paint */
                selection-color: #333;
                outline: 0;
                border: none;
            }
        """)

    def paintCell(self, painter, rect, date):
        # Only paint dates in the current month
        if date.month() != self.monthShown() or date.year() != self.yearShown():
            return # Skip painting (blank)

        painter.save()
        painter.setRenderHint(painter.RenderHint.Antialiasing)

        # Draw Selection (Custom Rounded Rect/Circle)
        if date == self.selectedDate():
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#1976D2"))
            # IDK, maybe a rounded rect matches the theme better than a circle
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 4, 4)
            painter.setPen(QColor("white")) # Text color for selected
        else:
            painter.setPen(QColor("#333")) # Normal text color

        # Draw Day Number
        # Centered text
        painter.drawText(rect, Qt.AlignCenter, str(date.day()))
        
        painter.restore()

class AppointmentWidget(QFrame):
    STATUS_COLORS = {
        "Scheduled": "#FF9800",
        "Completed": "#4CAF50",
        "Cancelled": "#e53935",
    }

    def __init__(self, appt_data, delete_callback, status_callback):
        super().__init__()
        self.appt_id = appt_data['id']
        self.status_callback = status_callback

        # Semi-transparent white to show watermark but keep readability
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0.7); border-radius: 6px; border: 1px solid #e0e0e0;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Details
        info_layout = QVBoxLayout()
        title_lbl = QLabel(f"{appt_data['time']} - {appt_data['title']}")
        title_lbl.setStyleSheet("font-weight: bold; color: #333; font-size: 14px; border: none;")
        
        patient_name = appt_data['patient_name'] if appt_data.get('patient_name') else "General Event"
        u_subtitle = QLabel(f"Patient: {patient_name}")
        u_subtitle.setStyleSheet("color: #666; font-size: 12px; border: none;")
        
        info_layout.addWidget(title_lbl)
        info_layout.addWidget(u_subtitle)
        layout.addLayout(info_layout)
        
        layout.addStretch()

        # Status Selector
        current_status = appt_data.get('status') or 'Scheduled'
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Scheduled", "Completed", "Cancelled"])
        if current_status in self.STATUS_COLORS:
            self.status_combo.setCurrentText(current_status)
        self.status_combo.setCursor(Qt.PointingHandCursor)
        self._apply_status_style(current_status)
        self.status_combo.currentTextChanged.connect(self._on_status_changed)
        layout.addWidget(self.status_combo)
        
        # Delete Button
        del_btn = QPushButton()
        del_btn.setIcon(qta.icon('fa5s.trash-alt', color='#D32F2F'))
        del_btn.setToolTip("Delete Appointment")
        del_btn.setFixedSize(32, 32)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ffebee;
            }
        """)
        del_btn.clicked.connect(lambda: delete_callback(self.appt_id))
        layout.addWidget(del_btn)

    def _apply_status_style(self, status):
        color = self.STATUS_COLORS.get(status, "#FF9800")
        self.status_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {color};
                color: white;
                font-size: 11px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                padding: 4px 10px;
                min-width: 90px;
            }}
            QComboBox::drop-down {{ border: none; width: 18px; }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
                margin-right: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: #333;
                selection-background-color: #1976D2;
                selection-color: white;
                border: 1px solid #ddd;
            }}
        """)

    def _on_status_changed(self, new_status):
        self._apply_status_style(new_status)
        self.status_callback(self.appt_id, new_status)

class ScheduleView(QWidget):
    appointments_changed = Signal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left: Calendar
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Custom Navigation
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 10)
        
        # Month Combo
        self.month_combo = QComboBox()
        self.month_combo.addItems([QLocale().monthName(i) for i in range(1, 13)])
        self.month_combo.setCursor(Qt.PointingHandCursor)
        self.month_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                color: #333;
                min-width: 100px;
                selection-background-color: white; 
                selection-color: #333;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #666; margin-right: 10px; }
            
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333;
                selection-background-color: #1976D2;
                selection-color: white;
                outline: 0;
            }
        """)
        self.month_combo.currentIndexChanged.connect(self.update_calendar_page)
        nav_layout.addWidget(self.month_combo)
        
        # Year Combo (Upcoming Years Only)
        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        self.year_combo.addItems([str(y) for y in range(current_year, current_year + 11)])
        self.year_combo.setCursor(Qt.PointingHandCursor)
        self.year_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                color: #333;
                min-width: 80px;
                selection-background-color: white;
                selection-color: #333;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #666; margin-right: 10px; }
            
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333;
                selection-background-color: #1976D2;
                selection-color: white;
                outline: 0;
            }
        """)
        self.year_combo.currentIndexChanged.connect(self.update_calendar_page)
        nav_layout.addWidget(self.year_combo)
        
        nav_layout.addStretch()
        
        # Today Button
        btn_today = QPushButton("Today")
        btn_today.setCursor(Qt.PointingHandCursor)
        btn_today.setStyleSheet("""
            QPushButton { background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 4px; padding: 5px 10px; color: #333; }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        btn_today.clicked.connect(self.go_to_today)
        nav_layout.addWidget(btn_today)
        
        left_layout.addLayout(nav_layout)
        
        self.calendar = StylishCalendar()
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.currentPageChanged.connect(self.on_page_changed)
        
        left_layout.addWidget(self.calendar)
        
        # Legend or Info
        help_lbl = QLabel("Select a date to view or add appointments.")
        help_lbl.setStyleSheet("color: #777; font-style: italic; margin-top: 10px;")
        left_layout.addWidget(help_lbl)
        
        left_layout.addStretch()
        layout.addWidget(left_panel, stretch=1)
        
        # Right: Agenda List
        right_panel = QFrame()
        # Transparent for watermark
        right_panel.setStyleSheet("background-color: transparent; border-radius: 8px; border: 1px solid #eee;")
        right_layout = QVBoxLayout(right_panel)
        
        # Header
        header_layout = QHBoxLayout()
        self.date_label = QLabel("Appointments for Today")
        self.date_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; border: none;")
        header_layout.addWidget(self.date_label)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("+ Add Appointment")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
             QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976D2, stop:1 #2196F3);
                color: white; 
                padding: 8px 16px; 
                border-radius: 15px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1565C0, stop:1 #1E88E5);
            }
        """)
        add_btn.clicked.connect(self.open_add_appointment)
        header_layout.addWidget(add_btn)
        
        right_layout.addLayout(header_layout)
        
        # List
        self.appt_list = QListWidget()
        self.appt_list.setStyleSheet("""
            QListWidget { border: none; background: transparent; }
            QListWidget::item { \
                background: transparent; \
                padding: 5px; \
            }
            QListWidget::item:hover { background: transparent; }
        """)
        self.appt_list.setFocusPolicy(Qt.NoFocus)
        self.appt_list.setSpacing(10)
        right_layout.addWidget(self.appt_list)
        
        layout.addWidget(right_panel, stretch=1)
        
        # Initial Load
        self.selected_date = QDate.currentDate()
        self.calendar.setSelectedDate(self.selected_date)
        
        # Sync combos with initial date
        self.on_page_changed(self.selected_date.year(), self.selected_date.month())
        
        self.load_appointments()

    def update_calendar_page(self):
        month = self.month_combo.currentIndex() + 1
        year_str = self.year_combo.currentText()
        if not year_str: return
        year = int(year_str)
        self.calendar.setCurrentPage(year, month)

    def on_page_changed(self, year, month):
        # Update combos without triggering update_calendar_page recursively
        self.month_combo.blockSignals(True)
        self.year_combo.blockSignals(True)
        
        self.month_combo.setCurrentIndex(month - 1)
        
        # Handle year combo
        idx = self.year_combo.findText(str(year))
        if idx != -1:
            self.year_combo.setCurrentIndex(idx)
        else:
            # If year is out of range of our combo, maybe add it or just ignore?
            # Creating "Upcoming only" implies we might not support navigating back too far,
            # but calendar allows it. For consistency, let's just leave it if not found 
            # or add it dynamically? 
            # User requirement: "only allowing to select upcoming years".
            # So if user navigates back via keyboard, we might just show nothing in combo or reset.
            pass
            
        self.month_combo.blockSignals(False)
        self.year_combo.blockSignals(False)

    def go_to_today(self):
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        self.on_page_changed(today.year(), today.month()) # Force header update
        self.on_date_selected(today)

    def on_date_selected(self, date):
        self.selected_date = date
        self.date_label.setText(f"Appointments for {date.toString('MMM d, yyyy')}")
        self.load_appointments()

    def load_appointments(self):
        self.appt_list.clear()
        date_str = self.selected_date.toString("yyyy-MM-dd")
        appointments = self.db.get_appointments_by_date(date_str)
        
        if not appointments:
            item = QListWidgetItem("No appointments scheduled.")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.NoItemFlags) # Non-selectable
            self.appt_list.addItem(item)
            return

        for appt in appointments:
            # Create list item
            item = QListWidgetItem(self.appt_list)
            # Create widget
            widget = AppointmentWidget(appt, self.delete_appointment, self.update_appointment_status)
            item.setSizeHint(widget.sizeHint())
            self.appt_list.setItemWidget(item, widget)

    def open_add_appointment(self):
        form = AppointmentForm(self, self.db, self.selected_date)
        if form.exec():
            self.load_appointments()
            self.appointments_changed.emit()

    def update_appointment_status(self, appt_id, new_status):
        if self.db.update_appointment_status(appt_id, new_status):
            self.appointments_changed.emit()
        else:
            QMessageBox.critical(self, "Error", "Failed to update appointment status.")
            self.load_appointments()

    def delete_appointment(self, appt_id):
        dialog = ConfirmationDialog(self, "Confirm Delete", 
                                  "Are you sure you want to delete this appointment?")
        
        if dialog.exec():
            if self.db.delete_appointment(appt_id):
                self.load_appointments()
                self.appointments_changed.emit()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete appointment.")
