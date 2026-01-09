import sys
import time
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from data_manager import get_due_tasks, mark_done, snooze_task
# Snooze duration in Minutes
SNOOZE_MINUTES = 30 

class WorkerSignals(QObject):
    trigger = pyqtSignal(str, int)

class RembleOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.task_id = None
        self.initUI()

    def initUI(self):
        # Set window to stay on top, no frame, tool window
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Position: Center-ish (adjust 100, 100 if needed)
        self.setGeometry(100, 100, 450, 300)
        
        # Styling: Dark mode, green text, aggressive borders
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #00FF00;
                border: 3px solid #00FF00;
                border-radius: 15px;
                font-family: Consolas, monospace;
            }
            QLabel {
                border: none;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton {
                background-color: #333;
                border: 1px solid #00FF00;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #000;
            }
        """)

        layout = QVBoxLayout()
        
        # HEADER
        header = QLabel("🚨 REMBLE ENFORCEMENT 🚨")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #FF0000; font-size: 20px; border-bottom: 1px solid #333;")
        layout.addWidget(header)

        # TASK TEXT
        self.label = QLabel("Loading...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        # BUTTONS
        btn_layout = QVBoxLayout()
        
        self.btn_done = QPushButton("✅ I HAVE DONE THIS")
        self.btn_done.clicked.connect(self.mark_as_done)
        btn_layout.addWidget(self.btn_done)
        
        self.btn_snooze = QPushButton(f"⏳ I AM DOING IT (Hide {SNOOZE_MINUTES}m)")
        self.btn_snooze.clicked.connect(self.snooze)
        btn_layout.addWidget(self.btn_snooze)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def show_reminder(self, text, t_id):
        # FIX: flickering/resetting issue.
        # If the window is already open and showing THIS task, do nothing.
        if self.isVisible() and self.task_id == t_id:
            return

        self.task_id = t_id
        self.label.setText(f"{text}")
        
        if not self.isVisible():
            self.showNormal()
            self.activateWindow()
            # Force window to top aggressively
            self.raise_()

    def mark_as_done(self):
        if self.task_id:
            print(f"Marking ID {self.task_id} as DONE.")
            mark_done(self.task_id)
        self.hide()
        # Reset ID so next task triggers a fresh popup
        self.task_id = None 

    def snooze(self):
        if self.task_id:
            print(f"Snoozing ID {self.task_id} for {SNOOZE_MINUTES} minutes.")
            # This writes to DB so get_due_tasks() ignores it for 30 mins
            snooze_task(self.task_id, SNOOZE_MINUTES)
        
        self.hide()
        # Reset ID so the window is ready for the next task (if any)
        self.task_id = None

def daemon_loop(signals):
    print("Daemon ACTIVE. Waiting for tasks...")
    while True:
        tasks = get_due_tasks() # Returns list sorted by time (earliest first)
        
        if tasks:
            # CRITICAL FIX: Only pick the FIRST (Oldest) task.
            # Ignore the rest until this one is cleared.
            current_task = tasks[0]
            
            # Send signal to GUI
            signals.trigger.emit(current_task['task'], current_task['id'])
            
            # Wait 3 seconds before checking again.
            # If you haven't clicked done, tasks[0] is still the same task.
            # The GUI 'show_reminder' function handles ignoring the repeat signal.
            time.sleep(3) 
        else:
            # Relax if nothing is due
            time.sleep(10)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RembleOverlay()
    
    signals = WorkerSignals()
    signals.trigger.connect(window.show_reminder)

    # Run check loop in background thread
    t = threading.Thread(target=daemon_loop, args=(signals,), daemon=True)
    t.start()

    sys.exit(app.exec())