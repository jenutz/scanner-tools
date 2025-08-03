#!/bin/python3

"""
PyQt GUI to control `hp-scan` with selectable DPI resolution.

This script provides a graphical interface to run the `hp-scan` command with
a chosen DPI. 
After scanning, the script stops media playback using `playerctl`. This is useful
for workflows like watching a show during scanning—so playback pauses while
you change the scanned document.

Purpose:
This app was created specifically to enable controlling hp-scan using the
mouse, allowing you to start scans without typing commands.

Usage:
    ./scan.py

Dependencies:
- PyQt5
- hp-scan (from HPLIP)
- playerctl (optional, to stop playback)
"""

import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QRadioButton, QButtonGroup, QLabel
)
from PyQt5.QtCore import QThread


class ScanThread(QThread):
    resolution = 600

    def run(self):
        scan_command = f"hp-scan --mode=color --resolution={self.resolution} --area=0,0,209.9,298.1 --units=mm --size=a4"
        subprocess.run(scan_command, shell=True)

        subprocess.run("playerctl stop", shell=True)

class ScriptRunnerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Run Scanner Script")
        self.layout = QVBoxLayout()

        self.res_label = QLabel("Select resolution (DPI):")
        self.layout.addWidget(self.res_label)

        self.radio_layout = QHBoxLayout()
        self.res_group = QButtonGroup(self)

        for res in [100, 300, 600, 1200]:
            btn = QRadioButton(str(res))
            self.radio_layout.addWidget(btn)
            self.res_group.addButton(btn, res)
            if res == 600:
                btn.setChecked(True)

        self.layout.addLayout(self.radio_layout)

        self.run_button = QPushButton("Run hp-scan")
        self.run_button.setMinimumHeight(60)
        self.set_button_style("green")
        self.run_button.clicked.connect(self.run_script)
        self.layout.addWidget(self.run_button)

        self.setLayout(self.layout)


    def set_button_style(self, color):
        if color == "green":
            self.run_button.setStyleSheet("background-color: green; color: white; font-size: 18px;")
        elif color == "red":
            self.run_button.setStyleSheet("background-color: red; color: white; font-size: 18px;")


    def run_script(self):
        self.set_button_style("red")
        self.run_button.setText("Running...")
        self.run_button.setDisabled(True)

        selected_id = self.res_group.checkedId()

        self.thread = ScanThread()
        self.thread.resolution = selected_id
        self.thread.finished.connect(self.on_finished)
        self.thread.start()


    def on_finished(self):
        self.set_button_style("green")
        self.run_button.setText("Run hp-scan")
        self.run_button.setDisabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScriptRunnerApp()
    window.resize(400, 200)
    window.show()
    sys.exit(app.exec_())

