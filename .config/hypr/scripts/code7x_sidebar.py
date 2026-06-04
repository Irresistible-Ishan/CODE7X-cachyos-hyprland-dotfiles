import sys
import os
import json
import subprocess
import signal
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QScrollArea, QLabel, QFrame, 
                             QStackedWidget, QLineEdit, QSizePolicy)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QImage
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal

# --- CONFIG ---
NOTES_FILE = os.path.expanduser("~/.config/code7x_notes.json")
COLOR_BG = "#0a0a12"
COLOR_SURFACE = "#16161e"
COLOR_ACCENT = "#00ffff"
COLOR_ACCENT_DIM = "#003333"
COLOR_PINK = "#ff0066"

class NoteItem(QFrame):
    delete_requested = pyqtSignal(str)
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.setFixedHeight(50)
        self.setStyleSheet(f"""
            NoteItem {{ background: {COLOR_SURFACE}; border: 1px solid {COLOR_ACCENT_DIM}; border-radius: 5px; margin: 2px; }}
            NoteItem:hover {{ border: 1px solid {COLOR_ACCENT}; background: #1a1a2e; }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.label = QLabel(text)
        self.label.setStyleSheet("color: white; font-size: 11px;")
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        
        self.del_btn = QPushButton("✕")
        self.del_btn.setFixedSize(24, 24)
        self.del_btn.setStyleSheet(f"background: transparent; color: {COLOR_PINK}; font-weight: bold; border: none;")
        self.del_btn.clicked.connect(lambda: self.delete_requested.emit(self.text))
        self.del_btn.hide()
        layout.addWidget(self.del_btn)

    def enterEvent(self, event):
        self.del_btn.show()
    def leaveEvent(self, event):
        self.del_btn.hide()

class ClipboardItem(QFrame):
    def __init__(self, item_id, content, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.content = content
        self.setFixedHeight(80)
        self.setStyleSheet(f"background: {COLOR_SURFACE}; border: 1px solid {COLOR_ACCENT_DIM}; border-radius: 5px; margin: 2px;")
        
        layout = QVBoxLayout(self)
        self.label = QLabel(content[:100] + "..." if len(content)>100 else content)
        self.label.setStyleSheet("color: #aaa; font-size: 10px;")
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        subprocess.run(f"cliphist decode {self.item_id} | wl-copy", shell=True)

class SidebarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("Code7xSidebar")
        
        self.resize(380, 900)
        screen = QApplication.primaryScreen().size()
        self.move(screen.width() - 390, 60)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QFrame()
        self.container.setStyleSheet(f"background: {COLOR_BG}f2; border-left: 2px solid {COLOR_ACCENT};")
        self.layout.addWidget(self.container)
        
        self.c_layout = QVBoxLayout(self.container)
        
        # --- INPUT AREA ---
        input_label = QLabel(" 󰎚 NEURAL_FEED_INPUT ")
        input_label.setStyleSheet(f"color: {COLOR_ACCENT}; font-weight: bold; font-size: 10px; margin-top: 10px;")
        self.c_layout.addWidget(input_label)
        
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("TYPE_AND_ENTER...")
        self.note_input.setStyleSheet(f"background: #050505; border: 1px solid {COLOR_ACCENT_DIM}; color: white; padding: 12px; border-radius: 5px;")
        self.note_input.returnPressed.connect(self.add_note)
        self.c_layout.addWidget(self.note_input)
        
        # --- TABS ---
        tab_layout = QHBoxLayout()
        self.btn_notes = QPushButton("NOTES")
        self.btn_clip = QPushButton("CLIPBOARD")
        for b in [self.btn_notes, self.btn_clip]:
            b.setStyleSheet(f"background: {COLOR_SURFACE}; color: {COLOR_ACCENT}; padding: 10px; font-weight: bold; border: 1px solid {COLOR_ACCENT_DIM};")
            tab_layout.addWidget(b)
        self.btn_notes.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_clip.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.c_layout.addLayout(tab_layout)
        
        self.stack = QStackedWidget()
        self.c_layout.addWidget(self.stack)
        
        # Pages
        self.page_notes = QWidget()
        self.n_layout = QVBoxLayout(self.page_notes)
        self.n_scroll = QScrollArea()
        self.n_scroll.setWidgetResizable(True)
        self.n_scroll.setStyleSheet("background: transparent; border: none;")
        self.n_list_widget = QWidget()
        self.n_list_layout = QVBoxLayout(self.n_list_widget)
        self.n_list_layout.addStretch()
        self.n_scroll.setWidget(self.n_list_widget)
        self.n_layout.addWidget(self.n_scroll)
        self.stack.addWidget(self.page_notes)
        
        self.page_clip = QWidget()
        self.cl_layout = QVBoxLayout(self.page_clip)
        self.cl_scroll = QScrollArea()
        self.cl_scroll.setWidgetResizable(True)
        self.cl_scroll.setStyleSheet("background: transparent; border: none;")
        self.cl_list_widget = QWidget()
        self.cl_list_layout = QVBoxLayout(self.cl_list_widget)
        self.cl_list_layout.addStretch()
        self.cl_scroll.setWidget(self.cl_list_widget)
        self.cl_layout.addWidget(self.cl_scroll)
        self.stack.addWidget(self.page_clip)
        
        self.last_notes_mtime = 0
        self.last_clip_data = ""
        self.is_foreground = False
        
        self.update_content()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_content)
        self.timer.start(1000)

    def add_note(self):
        text = self.note_input.text().strip()
        if text:
            if not os.path.exists(NOTES_FILE):
                with open(NOTES_FILE, 'w') as f: json.dump([], f)
            with open(NOTES_FILE, 'r') as f: notes = json.load(f)
            notes.append(text)
            with open(NOTES_FILE, 'w') as f: json.dump(notes, f)
            self.note_input.clear()
            self.load_notes()

    def load_notes(self):
        try:
            if not os.path.exists(NOTES_FILE): return
            with open(NOTES_FILE, 'r') as f: notes = json.load(f)
            for i in reversed(range(self.n_list_layout.count() - 1)):
                self.n_list_layout.itemAt(i).widget().setParent(None)
            for n in notes:
                item = NoteItem(n)
                item.delete_requested.connect(self.delete_note)
                self.n_list_layout.insertWidget(0, item)
        except: pass

    def delete_note(self, text):
        try:
            with open(NOTES_FILE, 'r') as f: notes = json.load(f)
            if text in notes: notes.remove(text)
            with open(NOTES_FILE, 'w') as f: json.dump(notes, f)
            self.load_notes()
        except: pass

    def update_content(self):
        if os.path.exists(NOTES_FILE):
            mtime = os.path.getmtime(NOTES_FILE)
            if mtime > self.last_notes_mtime:
                self.last_notes_mtime = mtime
                self.load_notes()
        try:
            current_clip = subprocess.check_output(["cliphist", "list"]).decode()
            if current_clip != self.last_clip_data:
                self.last_clip_data = current_clip
                for i in reversed(range(self.cl_list_layout.count() - 1)):
                    self.cl_list_layout.itemAt(i).widget().setParent(None)
                for line in current_clip.splitlines()[:20]:
                    if '\t' in line:
                        parts = line.split('\t')
                        self.cl_list_layout.insertWidget(self.cl_list_layout.count()-1, ClipboardItem(parts[0], parts[1]))
        except: pass

    def toggle_layer(self):
        self.is_foreground = not self.is_foreground
        if self.is_foreground:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            # We need to tell Hyprland to bring it forward
            os.system("hyprctl dispatch alterzorder 1 class:Code7xSidebar")
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
            os.system("hyprctl dispatch alterzorder -1 class:Code7xSidebar")
        self.show()

    def focus_input(self):
        self.show()
        self.raise_()
        self.note_input.setFocus()

def handle_sig1(sig, frame):
    window.focus_input()

def handle_sig2(sig, frame):
    window.toggle_layer()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Code7xSidebar")
    window = SidebarWidget()
    signal.signal(signal.SIGUSR1, handle_sig1)
    signal.signal(signal.SIGUSR2, handle_sig2)
    window.show()
    sys.exit(app.exec())
