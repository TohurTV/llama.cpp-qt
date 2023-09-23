#!/usr/bin/env python3
import sys
import subprocess
import threading
import os
import re
import time  # Import the time module
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QSpinBox, QVBoxLayout, QWidget, \
    QLineEdit, QHBoxLayout, QPlainTextEdit, QCheckBox, QTabWidget, QWidget, QFormLayout
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import configparser


class ServerRunner(QObject):
    started = pyqtSignal()
    stopped = pyqtSignal()
    output_received = pyqtSignal(str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self.process = None

    def run_server(self):
        self.process = subprocess.Popen(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        self.started.emit()

        while True:
            line = self.process.stdout.readline()
            if not line:
                break
            self.output_received.emit(line)

        self.process.wait()
        self.stopped.emit()


class ModelChooser(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.model_entry = QLineEdit()
        self.model_entry.setPlaceholderText('Select Model...')
        self.model_button = QPushButton('Select Model', self)
        self.model_button.clicked.connect(self.select_model)

        self.layout.addWidget(self.model_entry)
        self.layout.addWidget(self.model_button)
        self.setLayout(self.layout)

    def select_model(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Model Files (*.gguf);;All Files (*)')
        model_path, _ = file_dialog.getOpenFileName(self, 'Select Model', '', options=options)
        if model_path:
            self.model_entry.setText(model_path)


class LlamaServerWrapper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.server_runner = None
        self.api_process = None
        self.load_settings()  # Load saved settings when the application starts

    def initUI(self):
        self.setWindowTitle('LLama.cpp QT')
        self.setGeometry(100, 100, 400, 250)

        self.tab_widget = QTabWidget(self)

        self.model_tab = QWidget()
        self.server_tab = QWidget()

        self.tab_widget.addTab(self.model_tab, "Model Settings")
        self.tab_widget.addTab(self.server_tab, "Server Settings")

        self.setCentralWidget(self.tab_widget)

        # Model Settings Tab
        self.model_layout = QVBoxLayout()
        self.model_tab.setLayout(self.model_layout)

        self.model_settings_layout = QVBoxLayout()  # Use QVBoxLayout for the entire tab

        self.model_chooser = ModelChooser()
        self.model_chooser.layout.setAlignment(Qt.AlignTop)

        self.model_settings_layout.addWidget(self.model_chooser)

        # Add some vertical space between Model Selection and GPU Layers
        self.model_settings_layout.addSpacing(10)

        self.row1_layout = QHBoxLayout()  # Create a QHBoxLayout for GPU Layers
        self.gpu_layers_label = QLabel('GPU Layers:', self)
        self.gpu_layers_entry = QSpinBox(self)
        self.gpu_layers_entry.setMinimum(1)
        self.gpu_layers_entry.setMaximum(100)
        self.row1_layout.addWidget(self.gpu_layers_label)
        self.row1_layout.addWidget(self.gpu_layers_entry)
        self.model_settings_layout.addLayout(self.row1_layout)

        # Add some vertical space between GPU Layers and Threads
        self.model_settings_layout.addSpacing(10)

        self.row2_layout = QHBoxLayout()  # Create a QHBoxLayout for Threads
        self.threads_label = QLabel('Threads:', self)
        self.threads_entry = QSpinBox(self)
        self.threads_entry.setMinimum(1)
        self.threads_entry.setMaximum(100)
        self.row2_layout.addWidget(self.threads_label)
        self.row2_layout.addWidget(self.threads_entry)
        self.model_settings_layout.addLayout(self.row2_layout)

        # Add some vertical space between Threads and Context Size
        self.model_settings_layout.addSpacing(10)

        self.row3_layout = QHBoxLayout()  # Create a QHBoxLayout for Context Size
        self.ctx_size_label = QLabel('Context Size:', self)
        self.ctx_size_entry = QSpinBox(self)
        self.ctx_size_entry.setMinimum(1)
        self.ctx_size_entry.setMaximum(10000)
        self.row3_layout.addWidget(self.ctx_size_label)
        self.row3_layout.addWidget(self.ctx_size_entry)
        self.model_settings_layout.addLayout(self.row3_layout)

        self.model_settings_layout.addSpacing(10)

        self.row4_layout = QHBoxLayout()  # Create a QHBoxLayout for Context Size
        self.bth_size_label = QLabel('Batch Size:', self)
        self.bth_size_entry = QSpinBox(self)
        self.bth_size_entry.setMinimum(1)
        self.bth_size_entry.setMaximum(10000)
        self.row4_layout.addWidget(self.bth_size_label)
        self.row4_layout.addWidget(self.bth_size_entry)
        self.model_settings_layout.addLayout(self.row4_layout)

        # Add some vertical space between Context Size and MLock checkbox
        self.model_settings_layout.addSpacing(10)

        # Checkbox for the --mlock option
        self.mlock_checkbox = QCheckBox('Lock memory (mlock)', self)
        self.model_settings_layout.addWidget(self.mlock_checkbox)  # Add checkbox to layout

        # Add stretch to push all content to the top and leave any remaining space at the bottom
        self.model_settings_layout.addStretch()

        self.model_layout.addLayout(self.model_settings_layout)

        # Server Settings Tab
        self.server_layout = QVBoxLayout()
        self.server_tab.setLayout(self.server_layout)

        self.server_settings_layout = QVBoxLayout()  # Use QVBoxLayout for the entire tab

        self.host_label = QLabel('Server Host:', self)
        self.host_entry = QLineEdit(self)
        self.host_entry.setPlaceholderText('Server Host...')
        self.host_entry.setText('localhost')  # Set default host value

        self.port_label = QLabel('Server Port:', self)
        self.port_entry = QSpinBox(self)
        self.port_entry.setMinimum(1)
        self.port_entry.setMaximum(65535)
        self.port_entry.setValue(8080)  # Set default port value

        self.server_settings_layout.addWidget(self.host_label)
        self.server_settings_layout.addWidget(self.host_entry)
        self.server_settings_layout.addWidget(self.port_label)
        self.server_settings_layout.addWidget(self.port_entry)

        # Checkbox for the OpenAI compatible wrapper
        self.oai_checkbox = QCheckBox('Use OpenAI compatible wrapper', self)

        self.oaiport_label = QLabel('OpenAI Server Port:', self)
        self.oaiport_entry = QSpinBox(self)
        self.oaiport_entry.setMinimum(1)
        self.oaiport_entry.setMaximum(65535)
        self.oaiport_entry.setValue(8089)  # Set default port value

        self.server_settings_layout.addWidget(self.oai_checkbox)
        self.server_settings_layout.addWidget(self.oaiport_label)
        self.server_settings_layout.addWidget(self.oaiport_entry)

        # Add stretch to push all content to the top and leave any remaining space at the bottom
        self.server_settings_layout.addStretch()

        self.server_layout.addLayout(self.server_settings_layout)

        self.output_text = QPlainTextEdit(self)
        self.output_text.setReadOnly(True)
        self.output_text.hide()

        self.stop_button = QPushButton('Unload Model', self)
        self.stop_button.hide()
        self.stop_button.clicked.connect(self.stop_server)

        self.model_layout.addWidget(self.output_text)
        self.model_layout.addWidget(self.stop_button)

        self.start_button = QPushButton('Load Model', self)
        self.start_button.clicked.connect(self.start_server)

        self.model_layout.addWidget(self.mlock_checkbox)
        self.model_layout.addWidget(self.start_button)

        self.show()

    def start_server(self):
        model_path = self.model_chooser.model_entry.text()
        gpu_layers = str(self.gpu_layers_entry.value())
        threads = str(self.threads_entry.value())
        ctx_size = str(self.ctx_size_entry.value())
        bth_size = str(self.bth_size_entry.value())
        host = self.host_entry.text()
        port = str(self.port_entry.value())
        mlock = "--mlock" if self.mlock_checkbox.isChecked() else ""

        if not model_path:
            return

        cmd = [
            "./server",
            "--model", model_path,
            "--n-gpu-layers", gpu_layers,
            "--threads", threads,
            "--ctx-size", ctx_size,
            "--batch-size", bth_size,
            "--host", host,  # Add host argument
            "--port", port,  # Add port argument
            mlock  # Include --mlock if the checkbox is checked
        ]

        self.save_settings(model_path, gpu_layers, threads, ctx_size, bth_size, mlock)

        self.server_runner = ServerRunner(cmd)
        self.server_runner.started.connect(self.on_server_started)
        self.server_runner.stopped.connect(self.on_server_stopped)
        self.server_runner.output_received.connect(self.on_output_received)

        self.server_runner_thread = threading.Thread(target=self.server_runner.run_server)
        self.server_runner_thread.start()

        self.model_chooser.hide()
        self.gpu_layers_label.hide()
        self.gpu_layers_entry.hide()
        self.threads_label.hide()
        self.threads_entry.hide()
        self.ctx_size_label.hide()
        self.ctx_size_entry.hide()
        self.bth_size_label.hide()
        self.bth_size_entry.hide()
        self.mlock_checkbox.hide()
        self.host_label.hide()
        self.host_entry.hide()
        self.port_label.hide()
        self.port_entry.hide()
        self.oaiport_label.hide()
        self.oaiport_entry.hide()
        self.start_button.hide()
        self.oai_checkbox.hide()
        self.output_text.show()
        self.stop_button.show()

        # Start the api_like_OAI.py script in a separate thread with a delay
        api_thread = threading.Thread(target=self.start_api_script_with_delay)
        api_thread.start()

    def start_api_script_with_delay(self):
        # Delay for a specified time (in seconds) before starting the API script
        api_delay = 10  # Set the delay time in seconds (adjust as needed)
        time.sleep(api_delay)

        # Start the api_like_OAI.py script as a separate process
        self.api_process = subprocess.Popen(["python3", "api_like_OAI.py"], stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, universal_newlines=True)

        while True:
            line = self.api_process.stdout.readline()
            if not line:
                break
            self.on_output_received(line)

    def on_server_started(self):
        print("Server started")

    def on_server_stopped(self):
        print("Server stopped")
        if self.api_process:
            self.api_process.terminate()
            self.api_process.wait()
        self.server_runner_thread.join()
        self.server_runner_thread = None

        self.output_text.hide()
        self.stop_button.hide()
        self.model_chooser.show()
        self.gpu_layers_label.show()
        self.gpu_layers_entry.show()
        self.threads_label.show()
        self.threads_entry.show()
        self.ctx_size_label.show()
        self.ctx_size_entry.show()
        self.bth_size_label.show()
        self.bth_size_entry.show()
        self.mlock_checkbox.show()
        self.host_label.show()
        self.host_entry.show()
        self.port_label.show()
        self.port_entry.show()
        self.oai_checkbox.show()
        self.oaiport_label.show()
        self.oaiport_entry.show()
        self.start_button.show()

    def on_output_received(self, output):
        # Remove leading and trailing whitespace
        output = output.strip()

        # Remove ANSI escape codes (used for formatting in some terminals)
        output = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', output)

        # Append the cleaned output to the text area
        self.output_text.appendPlainText(output)

    def stop_server(self):
        if self.server_runner:
            self.server_runner.process.terminate()
            self.server_runner.process.wait()

    def load_settings(self):
        config = configparser.ConfigParser()
        config_file = os.path.join(os.path.expanduser("~"), ".config", "llama_server_settings.ini")
        if os.path.exists(config_file):
            config.read(config_file)
            if config.has_section("Settings"):
                model_path = config.get("Settings", "model_path")
                gpu_layers = config.get("Settings", "gpu_layers")
                threads = config.get("Settings", "threads")
                ctx_size = config.get("Settings", "ctx_size")
                bth_size = config.get("Settings", "bth_size")
                host = config.get("Settings", "host")  # Load host setting
                port = config.get("Settings", "port")  # Load port setting
                mlock = config.get("Settings", "mlock")  # Load mlock setting
                self.model_chooser.model_entry.setText(model_path)
                self.gpu_layers_entry.setValue(int(gpu_layers))
                self.threads_entry.setValue(int(threads))
                self.ctx_size_entry.setValue(int(ctx_size))
                self.bth_size_entry.setValue(int(bth_size))
                self.port_entry.setValue(int(port))
                self.host_entry.setText(host)
                self.mlock_checkbox.setChecked(mlock == "True")  # Set checkbox state

    def save_settings(self, model_path, gpu_layers, threads, ctx_size, bth_size, mlock):
        config = configparser.ConfigParser()
        config_file = os.path.join(os.path.expanduser("~"), ".config", "llama_server_settings.ini")
        if not config.has_section("Settings"):
            config.add_section("Settings")
        config.set("Settings", "model_path", model_path)
        config.set("Settings", "gpu_layers", gpu_layers)
        config.set("Settings", "threads", threads)
        config.set("Settings", "ctx_size", ctx_size)
        config.set("Settings", "bth_size", bth_size)
        config.set("Settings", "host", self.host_entry.text())  # Save host setting
        config.set("Settings", "port", str(self.port_entry.value()))  # Save port setting as string
        config.set("Settings", "mlock", str(self.mlock_checkbox.isChecked()))  # Save mlock setting as string
        with open(config_file, "w") as configfile:
            config.write(configfile)


def main():
    app = QApplication(sys.argv)
    window = LlamaServerWrapper()
    app.aboutToQuit.connect(window.stop_server)  # Ensure the server is stopped when the GUI is closed
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
