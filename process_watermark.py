from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
import sys

def create_watermark():
    # We need a QAplication instance for QImage/QPainter operations in some environments
    app = QApplication(sys.argv)
    
    input_path = "assets/watermark.jpg"
    output_path = "assets/watermark_bg.png"
    
    # Load
    original = QImage(input_path)
    if original.isNull():
        print(f"Failed to load image from {input_path}")
        return

    # Helper to calculate new size (keep aspect ratio, max width 1000 for 'big' watermark)
    target_width = 1000
    if original.width() > target_width:
        original = original.scaledToWidth(target_width, Qt.SmoothTransformation)

    # Create destination image (ARGB32 for transparency)
    final_img = QImage(original.size(), QImage.Format_ARGB32)
    final_img.fill(Qt.transparent)

    # Painter
    painter = QPainter(final_img)
    # Set opacity to be very subtle (10%)
    painter.setOpacity(0.10) 
    painter.drawImage(0, 0, original)
    painter.end()

    # Save
    final_img.save(output_path)
    print(f"Saved faint watermark to {output_path}")

if __name__ == "__main__":
    create_watermark()
