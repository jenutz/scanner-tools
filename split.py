#!/bin/python3

"""
Simple PyQt5 tool to split images vertically by moving a seperator line.


- Use buttons or arrow keys to move the split line.
- Click to set line position.
- Press 'save', Enter, or 'S' to save split images.
- Loads next image automatically until done.

Usage: ./script.py image1.jpg image2.jpg ...
"""

import sys
import os
import time
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt5.QtGui import QPainter, QPixmap, QPen
from PyQt5.QtCore import Qt


class ImageCanvas(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.og_pixmap = QPixmap(image_path)
        self.pixmap = self.og_pixmap.scaled(
            1600, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.offset = self.pixmap.width() // 2
        self.step = 1
        self.setFixedSize(self.pixmap.size())
        self.timestamp = str(int(time.time()))


    def load_new_image(self, image_path):
        self.image_path = image_path
        self.og_pixmap = QPixmap(image_path)
        self.pixmap = self.og_pixmap.scaled(
            1600, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.update()


    def move_line_left(self):
        self.offset = max(0, self.offset - self.step)
        self.update()


    def move_line_right(self):
        self.offset = min(self.pixmap.width(), self.offset + self.step)
        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

        pen = QPen(Qt.red, 2)
        painter.setPen(pen)
        painter.drawLine(self.offset, 0, self.offset, self.pixmap.height())


    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        self.offset = x
        self.update()


    def save(self, event=None):
        ratio = self.og_pixmap.width() / self.pixmap.width()
        full_offset = int(ratio * self.offset)

        left_img = self.og_pixmap.copy(
            0, 0, full_offset, self.og_pixmap.height()
        )
        right_width = self.og_pixmap.width() - full_offset
        right_img = self.og_pixmap.copy(
            full_offset, 0, right_width, self.og_pixmap.height()
        )

        dir_name = f"splitted_{self.timestamp}"
        os.makedirs(dir_name, exist_ok=True)

        base_name = os.path.basename(self.image_path)
        name, ext = os.path.splitext(base_name)
        base_path = os.path.join(dir_name, name)

        left_img.save(base_path + "_left.jpg")
        right_img.save(base_path + "_right.jpg")

        print(
            f"Saved left and right images: {base_path}_left.jpg, {base_path}_right.jpg"
        )


class MainWindow(QWidget):
    def __init__(self, images):
        super().__init__()

        self.setWindowTitle("Split Image")

        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.setFocusPolicy(Qt.StrongFocus)

        self.canvas = ImageCanvas(images.pop())
        layout.addWidget(self.canvas)

        buttons = QHBoxLayout()
        left_btn = QPushButton("-")
        right_btn = QPushButton("+")
        save_btn = QPushButton("save")
        left_btn.clicked.connect(self.canvas.move_line_left)
        right_btn.clicked.connect(self.canvas.move_line_right)
        save_btn.clicked.connect(self.save)
        buttons.addWidget(left_btn)
        buttons.addWidget(right_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)
        self.resize(self.canvas.width(), self.canvas.height() + 40)


    def save(self, event=None):
        self.canvas.save()
        if images:
            self.canvas.load_new_image(images.pop())
        else:
            QApplication.quit()


    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_S):
            self.save()
        elif event.key() == Qt.Key_Left:
            self.canvas.move_line_left()
        elif event.key() == Qt.Key_Right:
            self.canvas.move_line_right()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if len(sys.argv) < 2:
        print("Usage: ./script.py image.jpg")
        sys.exit(1)

    images = sys.argv[1:]
    images.reverse()
    window = MainWindow(images)
    window.show()
    sys.exit(app.exec_())
