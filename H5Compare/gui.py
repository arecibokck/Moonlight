import sys, os
from queue import Queue
from PyQt5 import QtWidgets, QtCore, QtGui

# Ensure parent folder is in sys.path so absolute imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from H5Compare import abort_flag  # <-- shared abort flag
from H5Compare.main import run_comparison  # <-- run_comparison in same process

class HDF5ComparerGUI(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("H5Compare")
        self.setFixedSize(900, 650)
        self.setStyleSheet(self.dark_style())
        self.aborted = False
        self.init_ui()

    def dark_style(self):
        return """
        QWidget { background-color: #121212; color: #ffffff; font-size: 14px; }
        QLineEdit, QTextEdit { background-color: #1e1e1e; border: 2px solid #333; border-radius: 8px; padding: 4px; color: #ffffff; }
        QPushButton { background-color: #3a3a3a; border-radius: 8px; padding: 6px; }
        QPushButton:hover { background-color: #505050; }
        QPushButton:disabled { background-color: #2a2a2a; color: #777777; }
        QProgressBar { border: 2px solid #333; border-radius: 8px; text-align: center; background-color: #1e1e1e; }
        QProgressBar::chunk { background-color: #3a9ad9; border-radius: 8px; }
        """

    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

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

        self.start_btn = QtWidgets.QPushButton("Start Comparison")
        self.start_btn.setStyleSheet("background-color:#008000; color:white;")
        self.start_btn.clicked.connect(self.start_comparison)
        layout.addWidget(self.start_btn)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        self.log_window = QtWidgets.QTextEdit()
        self.log_window.setReadOnly(True)
        layout.addWidget(self.log_window)

    def browse_local(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Local Folder")
        if folder:
            self.local_input.setText(folder)

    def browse_remote(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Remote Folder")
        if folder:
            self.remote_input.setText(folder)

    def start_comparison(self):
        if self.start_btn.text() == "Start Comparison":
            local_root = self.local_input.text()
            remote_root = self.remote_input.text()
            if not local_root or not remote_root:
                self.log("Please select both root folders.", "red")
                return

            self.progress.setValue(0)
            self.progress.setFormat("0/0")
            self.aborted = False

            # Start backend thread (run in same memory space)
            self.thread = ComparisonThread(local_root, remote_root)
            self.thread.log_signal.connect(self.handle_log)
            self.thread.progress_signal.connect(self.handle_progress)  # <-- connect progress
            self.thread.finished_signal.connect(self.comparison_finished)
            self.thread.start()

            self.start_btn.setText("Stop Comparison")
            self.start_btn.setStyleSheet("background-color:#aa3333; color:white;")
        else:
            if self.thread and self.thread.isRunning():
                self.thread.abort()
                self.aborted = True
                self.log("Stopping comparison...", "#ffff00")
                self.start_btn.setEnabled(False)

    def handle_log(self, msg):
        if "[OK]" in msg:
            color = "#00ff00"
        elif "[DIFFERENT]" in msg:
            color = "#ffff00"
        elif "[MISSING" in msg or "[DIFFERENT SIZE]" in msg:
            color = "#ff5555"
        elif "Comparison finished" in msg:
            color = "#00ff00"
        elif "mismatch" in msg.lower() or "aborting" in msg.lower():
            color = "#ff0000"
        else:
            color = "#ffffff"

        self.log_window.setTextColor(QtGui.QColor(color))
        self.log_window.append(msg)
        self.log_window.verticalScrollBar().setValue(
            self.log_window.verticalScrollBar().maximum()
        )

    def handle_progress(self, completed, total):
        if total > 0:
            percentage = int((completed / total) * 100)
            self.progress.setValue(percentage)
            self.progress.setFormat(f"[{completed}/{total}] {percentage}%")
        else:
            self.progress.setValue(0)
            self.progress.setFormat("[0/0] 0%")

    def comparison_finished(self):
        self.start_btn.setEnabled(True)
        self.start_btn.setStyleSheet("background-color:#008000; color:white;")
        self.start_btn.setText("Start Comparison")
        if self.aborted:
            self.log("Comparison aborted by user.", "#ff0000")
        else:
            self.progress.setValue(100)

    def log(self, msg, color="#ffffff"):
        self.log_window.setTextColor(QtGui.QColor(color))
        self.log_window.append(msg)
        self.log_window.verticalScrollBar().setValue(
            self.log_window.verticalScrollBar().maximum()
        )

class ComparisonThread(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)
    progress_signal = QtCore.pyqtSignal(int, int)  # <-- emit completed files
    finished_signal = QtCore.pyqtSignal()

    def __init__(self, local_root, remote_root):
        super().__init__()
        self.local_root = local_root
        self.remote_root = remote_root
        self.completed_files = 0
        self.total_files = 0

    def abort(self):
        abort_flag.ABORT = True

    def run(self):
        abort_flag.ABORT = False

        # Pre-count total files for progress
        import H5Compare.utils as utils
        local_files = utils.collect_h5_files(self.local_root)
        remote_files = utils.collect_h5_files(self.remote_root)
        self.total_files = len(set(local_files.keys()) | set(remote_files.keys()))

        import H5Compare.main as main_module
        original_queue_class = main_module.Queue

        class SignalQueue(original_queue_class):
            def put(self_inner, item):
                super().put(item)
                line = str(item).strip()
                if line:
                    self_inner.thread.log_signal.emit(line)
                    # Increment progress only for actual comparison results
                    if any(tag in line for tag in ["[OK]", "[DIFFERENT]", "[MISSING", "[DIFFERENT SIZE]"]):
                        self_inner.thread.completed_files += 1
                        self_inner.thread.progress_signal.emit(
                            self_inner.thread.completed_files, self_inner.thread.total_files
                        )

        main_module.Queue = SignalQueue
        main_module.Queue.thread = self  # give access to log_signal

        try:
            run_comparison(self.local_root, self.remote_root)
        finally:
            main_module.Queue = original_queue_class

        self.finished_signal.emit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "h5_icon.ico")
    icon = QtGui.QIcon(icon_path)
    app.setWindowIcon(icon)

    gui = HDF5ComparerGUI()
    gui.setWindowIcon(icon)
    gui.show()
    sys.exit(app.exec_())
