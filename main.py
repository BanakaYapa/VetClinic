import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from database import DatabaseManager
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # 1. Force Fusion style for cross-platform consistency
    app.setStyle("Fusion")
    
    # 2. Enforce Static Light Palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f4f7f6"))      # Background
    palette.setColor(QPalette.WindowText, QColor("#333333"))  # Text
    palette.setColor(QPalette.Base, QColor("#ffffff"))        # Entry backgrounds
    palette.setColor(QPalette.AlternateBase, QColor("#f9f9f9"))
    palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipText, QColor("#333333"))
    palette.setColor(QPalette.Text, QColor("#333333"))        # Input text
    palette.setColor(QPalette.Button, QColor("#ffffff"))      # Button backgrounds
    palette.setColor(QPalette.ButtonText, QColor("#333333"))  # Button text
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor("#1976D2"))
    palette.setColor(QPalette.Highlight, QColor("#1976D2"))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    
    app.setPalette(palette)
    
    # Initialize Database
    db_manager = DatabaseManager()
    
    # Show Main Window
    window = MainWindow(db_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
