from PySide6.QtGui import QImage, QColor
import os

path = "assets/logo.jpg"
if os.path.exists(path):
    img = QImage(path)
    if not img.isNull():
        # Get top-left pixel color
        pixel = img.pixel(0, 0)
        color = QColor(pixel)
        print(f"Color: {color.name()}")
    else:
        print("Failed to load image")
else:
    print("Logo not found")
