from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup

class Toast(QLabel):
    def __init__(self, parent, text, duration=3000):
        # Always parent to the top-level window for consistent positioning
        main_window = parent.window() if parent else None
        super().__init__(main_window)
        
        # Add a symbol/icon to the text for style
        stylish_text = f"🔔  {text}"
        self.setText(stylish_text)
        
        # Style ("Stylish Gradient & Glassy")
        self.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c3e50, stop:1 #4ca1af);
                color: white;
                padding: 15px 20px;
                border-radius: 12px;
                font-size: 14px;
                font-family: "Segoe UI", sans-serif;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        
        self.setWordWrap(True)
        self.setMaximumWidth(350) 
        self.adjustSize()
        
        # Overlay inside the top-level window (Bottom Right)
        self.setAttribute(Qt.WA_TransparentForMouseEvents) 
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # Initial Opacity
        self.graphics_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.graphics_effect)
        self.graphics_effect.setOpacity(0) # Start invisible
        
        # Calculate Position relative to main_window
        host = main_window if main_window else parent
        parent_rect = host.rect()
        margin_x = 20
        margin_y = 30
        
        # Target Position (Bottom Right)
        target_x = parent_rect.width() - self.width() - margin_x
        target_y = parent_rect.height() - self.height() - margin_y
        
        # Start Position (Right Side Off-Screen)
        start_x = parent_rect.width() + 20 
        
        self.move(start_x, target_y)
        self.raise_()
        self.show()
        
        # Animation Group (Slide In From Right)
        self.anim_group = QParallelAnimationGroup(self)
        
        # 1. Slide Left (pos)
        anim_pos = QPropertyAnimation(self, b"pos")
        anim_pos.setDuration(400)
        anim_pos.setStartValue(QPoint(start_x, target_y))
        anim_pos.setEndValue(QPoint(target_x, target_y))
        anim_pos.setEasingCurve(QEasingCurve.OutCubic) 
        self.anim_group.addAnimation(anim_pos)
        
        # 2. Fade In
        anim_fade = QPropertyAnimation(self.graphics_effect, b"opacity")
        anim_fade.setDuration(350)
        anim_fade.setStartValue(0)
        anim_fade.setEndValue(1)
        self.anim_group.addAnimation(anim_fade)
        
        self.anim_group.start()
        
        # One-shot Timer to Fade Out
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)
        self.timer.start(duration)
        
    def fade_out(self):
        # Slide out to right
        parent_width = self.parent().width() if self.parent() else self.x() + self.width()
        self.anim_group_out = QParallelAnimationGroup(self)
        
        anim_pos = QPropertyAnimation(self, b"pos")
        anim_pos.setDuration(400)
        anim_pos.setStartValue(self.pos())
        anim_pos.setEndValue(QPoint(parent_width + 20, self.pos().y()))
        anim_pos.setEasingCurve(QEasingCurve.InCubic)
        self.anim_group_out.addAnimation(anim_pos)

        anim_fade = QPropertyAnimation(self.graphics_effect, b"opacity")
        anim_fade.setDuration(400)
        anim_fade.setStartValue(1)
        anim_fade.setEndValue(0)
        self.anim_group_out.addAnimation(anim_fade)
        
        self.anim_group_out.finished.connect(self.close)
        self.anim_group_out.start()

    @staticmethod
    def show_message(parent, text, duration=3000):
        # Helper to create and forget
        return Toast(parent, text, duration)
