from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect,
    QWidget, QFormLayout, QScrollArea,
    QSizePolicy
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta


class ConfirmationDialog(QDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 250)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Main Container
        container = QFrame()
        container.setObjectName("ConfirmContainer")
        container.setStyleSheet("""
            #ConfirmContainer {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #eee;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(Qt.gray)
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3F51B5, stop:1 #5C6BC0);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_lbl = QLabel(title)
        header_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(header_lbl)
        container_layout.addWidget(header)
        
        # Content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("font-size: 14px; color: #333; background: transparent;")
        msg_lbl.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(msg_lbl)
        container_layout.addWidget(content)
        
        # Buttons
        btns = QFrame()
        btns_layout = QHBoxLayout(btns)
        btns_layout.setContentsMargins(20, 0, 20, 20)
        btns_layout.setSpacing(15)
        
        btn_no = QPushButton("Cancel")
        btn_no.clicked.connect(self.reject)
        btn_no.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5; color: #666; padding: 10px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #eee; }
        """)
        
        btn_yes = QPushButton("Confirm")
        btn_yes.clicked.connect(self.accept)
        btn_yes.setStyleSheet("""
            QPushButton {
                background-color: #3F51B5; color: white; padding: 10px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #303F9F; }
        """)
        
        btns_layout.addWidget(btn_no)
        btns_layout.addWidget(btn_yes)
        container_layout.addWidget(btns)
        
        layout.addWidget(container)





class RecordDetailsDialog(QDialog):
    def __init__(self, parent, title, data_dict, icon_name='fa5s.info-circle'):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(700)

        # ─── Main layout ─────────────────────────────────────────────
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ─── Container with shadow ───────────────────────────────────
        self.container = QFrame()
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #ddd;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(Qt.gray)
        self.container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # ─── Header ──────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3F51B5, stop:1 #5C6BC0);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 0, 25, 0)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(icon_name, color='white').pixmap(QSize(30, 30)))
        header_layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background: transparent;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 18px;
                border: none;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
                border-radius: 15px;
            }
        """)
        header_layout.addWidget(close_btn)

        container_layout.addWidget(header)

        # ─── Scroll area ─────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white;")

        form_layout = QFormLayout(content_widget)
        form_layout.setContentsMargins(25, 20, 25, 30)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignTop)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # ─── Populate fields ─────────────────────────────────────────
        for label_text, value in data_dict.items():
            # Label (key)
            key_lbl = QLabel(f"{label_text}")
            key_lbl.setStyleSheet("""
                font-size: 13px;
                font-weight: bold;
                color: #555;
                padding-top: 8px;
            """)
            key_lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)

            value_str = str(value) if value is not None else "—"

            # Use QLabel for all fields for a "normal" appearance
            val_widget = QLabel(value_str)
            val_widget.setWordWrap(True)
            val_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            val_widget.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #222;
                    padding: 4px 10px;
                    background-color: #fcfcfc;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    min-height: 24px;
                }
            """)
            val_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            form_layout.addRow(key_lbl, val_widget)

        scroll.setWidget(content_widget)
        container_layout.addWidget(scroll)

        # ─── Footer ──────────────────────────────────────────────────
        footer = QFrame()
        footer.setFixedHeight(70)
        footer.setStyleSheet("""
            background-color: #f9f9f9;
            border-bottom-left-radius: 12px;
            border-bottom-right-radius: 12px;
            border-top: 1px solid #eee;
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 0, 20, 0)

        btn_close = QPushButton("Close")
        btn_close.setMinimumWidth(140)
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3F51B5;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
        """)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_close)

        container_layout.addWidget(footer)

        main_layout.addWidget(self.container)

        # Reasonable size constraints
        self.setMinimumHeight(340)
        self.setMaximumHeight(780)