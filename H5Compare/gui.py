import sys
import os
import subprocess
import re
from PyQt5 import QtWidgets, QtCore, QtGui

# Ensure parent folder is in sys.path so absolute imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

class HDF5ComparerGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("H5Compare")
        self.setFixedSize(900, 650)  # Prevent maximize
        self.setStyleSheet(self.dark_style())
        self.queue = []

        self.init_ui()

    def dark_style(self):
        return """
        QWidget {
            background-color: #121212;
            color: #ffffff;
            font-size: 14px;
        }
        QLineEdit, QTextEdit {
            background-color: #1e1e1e;
            border: 2px solid #333;
            border-radius: 8px;
            padding: 4px;
            color: #ffffff;
        }
        QPushButton {
            background-color: #3a3a3a;
            border-radius: 8px;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: #505050;
        }
        QProgressBar {
            border: 2px solid #333;
            border-radius: 8px;
            text-align: center;
            background-color: #1e1e1e;
        }
        QProgressBar::chunk {
            background-color: #3a9ad9;
            border-radius: 8px;
        }
        """

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Use a form layout for neat alignment
        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)  # <-- right-align labels

        self.local_input = QtWidgets.QLineEdit()
        self.local_browse = QtWidgets.QPushButton("Browse")
        self.local_browse.clicked.connect(self.browse_local)
        local_widget = QtWidgets.QHBoxLayout()
        local_widget.addWidget(self.local_input)
        local_widget.addWidget(self.local_browse)
        form_layout.addRow("Local Root Folder:", local_widget)

        self.remote_input = QtWidgets.QLineEdit()
        self.remote_browse = QtWidgets.QPushButton("Browse")
        self.remote_browse.clicked.connect(self.browse_remote)
        remote_widget = QtWidgets.QHBoxLayout()
        remote_widget.addWidget(self.remote_input)
        remote_widget.addWidget(self.remote_browse)
        form_layout.addRow("Remote Root Folder:", remote_widget)

        layout.addLayout(form_layout)

        # Start button
        self.start_btn = QtWidgets.QPushButton("Start Comparison")
        self.start_btn.clicked.connect(self.start_comparison)
        layout.addWidget(self.start_btn)

        # Progress bar
        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        # Log window
        self.log_window = QtWidgets.QTextEdit()
        self.log_window.setReadOnly(True)
        layout.addWidget(self.log_window)

        self.setLayout(layout)

    def browse_local(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Local Folder")
        if folder:
            self.local_input.setText(folder)

    def browse_remote(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Remote Folder")
        if folder:
            self.remote_input.setText(folder)

    def start_comparison(self):
        local_root = self.local_input.text()
        remote_root = self.remote_input.text()
        if not local_root or not remote_root:
            self.log("Please select both root folders.", "red")
            return

        self.start_btn.setDisabled(True)
        self.progress.setValue(0)
        self.progress.setFormat("0/0")

        # Run backend in separate thread
        self.thread = ComparisonThread(local_root, remote_root)
        self.thread.log_signal.connect(self.handle_log)
        self.thread.progress_signal.connect(self.handle_progress)
        self.thread.finished_signal.connect(self.comparison_finished)
        self.thread.start()

    def handle_log(self, msg):
        # Determine color based on log content
        if "[OK]" in msg:
            color = "#00ff00"
        elif "[DIFFERENT]" in msg:
            color = "#ffff00"
        elif "[MISSING" in msg or "[DIFFERENT SIZE]" in msg:
            color = "#ff5555"
        elif "Comparison finished" in msg:
            color = "#00ff00"
        else:
            color = "#ffffff"

        self.log_window.setTextColor(QtGui.QColor(color))
        self.log_window.append(msg)
        self.log_window.verticalScrollBar().setValue(
            self.log_window.verticalScrollBar().maximum()
        )

    def handle_progress(self, current, total):
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress.setValue(percentage)
            # Show both fraction and percentage
            self.progress.setFormat(f"[{current}/{total}] {percentage}%")
        else:
            self.progress.setValue(0)
            self.progress.setFormat("[0/0] 0%")

    def comparison_finished(self):
        self.start_btn.setEnabled(True)
        self.progress.setValue(100)

    def log(self, msg, color="#ffffff"):
        self.log_window.setTextColor(QtGui.QColor(color))
        self.log_window.append(msg)
        self.log_window.verticalScrollBar().setValue(
            self.log_window.verticalScrollBar().maximum()
        )

class ComparisonThread(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)
    progress_signal = QtCore.pyqtSignal(int, int)
    finished_signal = QtCore.pyqtSignal()

    def __init__(self, local_root, remote_root):
        super().__init__()
        self.local_root = local_root
        self.remote_root = remote_root

    def run(self):
        script_path = os.path.join(os.path.dirname(__file__), "main.py")

        # Precompute total number of HDF5 files
        total_files = 0
        for root in [self.local_root, self.remote_root]:
            for dirpath, _, filenames in os.walk(root):
                total_files += sum(1 for f in filenames if f.endswith(".h5"))

        if total_files == 0:
            self.log_signal.emit("No HDF5 files found in either folder.")
            self.finished_signal.emit()
            return

        completed_files = 0

        process = subprocess.Popen(
            [sys.executable, script_path, self.local_root, self.remote_root],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in process.stdout:
            line = line.strip()
            self.log_signal.emit(line)

            # Count files for progress
            if re.search(r"\[OK\]|\[DIFFERENT\]|\[MISSING|\[DIFFERENT SIZE\]", line):
                completed_files += 1
                self.progress_signal.emit(completed_files, total_files)

        process.wait()
        self.progress_signal.emit(total_files, total_files)
        self.finished_signal.emit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = HDF5ComparerGUI()
    gui.show()
    sys.exit(app.exec_())
