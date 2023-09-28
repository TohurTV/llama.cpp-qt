#!/usr/bin/env python3
import configparser
import os
import platform
import re
import subprocess
import sys
import threading
import time  # Import the time module

from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QSpinBox, QVBoxLayout, \
    QLineEdit, QHBoxLayout, QPlainTextEdit, QCheckBox, QTabWidget, QWidget


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


class LoraChooser(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.lora_entry = QLineEdit()
        self.lora_entry.setPlaceholderText('Select Lora...')
        self.lora_button = QPushButton('Select Lora', self)
        self.lora_button.clicked.connect(self.select_lora)

        self.layout.addWidget(self.lora_entry)
        self.layout.addWidget(self.lora_button)
        self.setLayout(self.layout)

    def select_lora(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Lora Files (*.gguf);;All Files (*)')
        lora_path, _ = file_dialog.getOpenFileName(self, 'Select Lora', '', options=options)
        if lora_path:
            self.lora_entry.setText(lora_path)


class LoraBaseChooser(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.lorabase_entry = QLineEdit()
        self.lorabase_entry.setPlaceholderText('Select Lora Base...')
        self.lorabase_button = QPushButton('Select Lora Base', self)
        self.lorabase_button.clicked.connect(self.select_lorabase)

        self.layout.addWidget(self.lorabase_entry)
        self.layout.addWidget(self.lorabase_button)
        self.setLayout(self.layout)

    def select_lorabase(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Lora Base Files (*.gguf);;All Files (*)')
        lorabase_path, _ = file_dialog.getOpenFileName(self, 'Select Lora Base', '', options=options)
        if lorabase_path:
            self.lorabase_entry.setText(lorabase_path)


class LlamaServerWrapper(QMainWindow):
    # Check the operating system
    if sys.platform.startswith('win'):
        # Windows: Create the folder in AppData\Roaming
        appdata_dir = os.getenv('APPDATA')
        config_dir = os.path.join(appdata_dir, "llama.cpp-qt")
    else:
        # Linux/Unix/Mac: Create the folder in ~/.config
        config_dir = os.path.join(os.path.expanduser("~"), ".config", "llama.cpp-qt")

    # Check if the llama.cpp-qt config directory exists or not
    if not os.path.isdir(config_dir):
        # If the directory is not present, then create it
        os.makedirs(config_dir)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.server_runner = None
        self.api_process = None
        self.load_settings()  # Load saved settings when the application starts

    def initUI(self):
        self.setWindowTitle('LLama.cpp QT')
        self.setGeometry(100, 100, 650, 372)

        self.tab_widget = QTabWidget(self)

        self.model_tab = QWidget()
        self.lora_tab = QWidget()
        self.server_tab = QWidget()

        self.tab_widget.addTab(self.model_tab, "Model Settings")
        self.tab_widget.addTab(self.lora_tab, "Lora Settings")
        self.tab_widget.addTab(self.server_tab, "Server Settings")

        self.setCentralWidget(self.tab_widget)
        self.tab_widget.tabBarClicked.connect(self.handle_tabbar_clicked)
        # Model Settings Tab
        self.model_layout = QVBoxLayout()
        self.model_tab.setLayout(self.model_layout)

        self.model_settings_layout = QVBoxLayout()  # Use QVBoxLayout for the entire tab

        self.model_chooser = ModelChooser()
        self.model_chooser.layout.setAlignment(Qt.AlignTop)

        self.model_settings_layout.addWidget(self.model_chooser)

        self.row1_layout = QHBoxLayout()  # Create a QHBoxLayout for GPU Layers
        self.gpu_layers_label = QLabel('GPU Layers:', self)
        self.gpu_layers_entry = QSpinBox(self)
        self.gpu_layers_entry.setMinimum(1)
        self.gpu_layers_entry.setMaximum(100)
        self.row1_layout.addWidget(self.gpu_layers_label)
        self.row1_layout.addWidget(self.gpu_layers_entry)
        self.model_settings_layout.addLayout(self.row1_layout)

        self.row2_layout = QHBoxLayout()  # Create a QHBoxLayout for Threads
        self.threads_label = QLabel('Threads:', self)
        self.threads_entry = QSpinBox(self)
        self.threads_entry.setMinimum(1)
        self.threads_entry.setMaximum(100)
        self.row2_layout.addWidget(self.threads_label)
        self.row2_layout.addWidget(self.threads_entry)
        self.model_settings_layout.addLayout(self.row2_layout)

        self.row3_layout = QHBoxLayout()  # Create a QHBoxLayout for Context Size
        self.ctx_size_label = QLabel('Context Size:', self)
        self.ctx_size_entry = QSpinBox(self)
        self.ctx_size_entry.setMinimum(1)
        self.ctx_size_entry.setMaximum(10000)
        self.row3_layout.addWidget(self.ctx_size_label)
        self.row3_layout.addWidget(self.ctx_size_entry)
        self.model_settings_layout.addLayout(self.row3_layout)

        self.row4_layout = QHBoxLayout()  # Create a QHBoxLayout for Batch Size
        self.bth_size_label = QLabel('Batch Size:', self)
        self.bth_size_entry = QSpinBox(self)
        self.bth_size_entry.setMinimum(1)
        self.bth_size_entry.setMaximum(10000)
        self.row4_layout.addWidget(self.bth_size_label)
        self.row4_layout.addWidget(self.bth_size_entry)
        self.model_settings_layout.addLayout(self.row4_layout)

        # Checkbox for the --mlock option
        self.row5_layout = QHBoxLayout()  # Create a QHBoxLayout for mlock
        self.mlock_checkbox = QCheckBox('Lock memory (mlock)', self)
        self.row5_layout.addWidget(self.mlock_checkbox)
        self.model_settings_layout.addLayout(self.row5_layout)

        # Checkbox for the ----low-vram option
        self.row6_layout = QHBoxLayout()  # Create a QHBoxLayout for Lowvram
        self.lowvram_checkbox = QCheckBox('Low Vram (Dont assign vram scratch buffer)', self)
        self.row6_layout.addWidget(self.lowvram_checkbox)
        self.model_settings_layout.addLayout(self.row6_layout)

        # Add stretch to push all content to the top and leave any remaining space at the bottom
        self.model_settings_layout.addStretch()

        self.model_layout.addLayout(self.model_settings_layout)

        # Lora Settings Tab
        self.lora_layout = QVBoxLayout()
        self.lora_tab.setLayout(self.lora_layout)

        self.lora_settings_layout = QVBoxLayout()  # Use QVBoxLayout for the entire tab
        self.lora_chooser = LoraChooser()
        self.lora_chooser.layout.setAlignment(Qt.AlignTop)

        self.lora_settings_layout.addWidget(self.lora_chooser)

        self.lorabase_chooser = LoraBaseChooser()
        self.lorabase_chooser.layout.setAlignment(Qt.AlignTop)

        self.lora_settings_layout.addWidget(self.lorabase_chooser)

        # Add stretch to push all content to the top and leave any remaining space at the bottom
        self.lora_settings_layout.addStretch()

        self.lora_layout.addLayout(self.lora_settings_layout)

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

        self.model_layout.addWidget(self.start_button)

        self.show()

    def start_server(self):
        model_path = self.model_chooser.model_entry.text()
        gpu_layers = str(self.gpu_layers_entry.value())
        threads = str(self.threads_entry.value())
        ctx_size = str(self.ctx_size_entry.value())
        bth_size = str(self.bth_size_entry.value())
        mlock = "--mlock" if self.mlock_checkbox.isChecked() else ""
        lowvram = "--low-vram" if self.lowvram_checkbox.isChecked() else ""
        lora_path = self.lora_chooser.lora_entry.text()
        lorabase_path = self.lorabase_chooser.lorabase_entry.text()
        host = self.host_entry.text()
        port = str(self.port_entry.value())
        oaiport = str(self.oaiport_entry.value())

        if not model_path:
            return

        if platform.system() == "Windows":
            # On Windows, execute server.exe
            cmd = [
                "server.exe",
                "--model", model_path,
                "--n-gpu-layers", gpu_layers,
                "--threads", threads,
                "--ctx-size", ctx_size,
                "--batch-size", bth_size,
                "--host", host,
                "--port", port,
                "--path", "./public"
            ]
        else:
            # On Linux and other Unix-like OSes, execute ./server
            cmd = [
                "./server",
                "--model", model_path,
                "--n-gpu-layers", gpu_layers,
                "--threads", threads,
                "--ctx-size", ctx_size,
                "--batch-size", bth_size,
                "--host", host,
                "--port", port,
                "--path", "./public"
            ]

        if self.mlock_checkbox.isChecked():
            cmd.append("--mlock")

        if self.lowvram_checkbox.isChecked():
            cmd.append("--low-vram")

        if self.lora_chooser.lora_entry.text():
            cmd.append("--lora")
            cmd.append(self.lora_chooser.lora_entry.text())  # Append the lora_path value

        if self.lorabase_chooser.lorabase_entry.text():
            cmd.append("--lora-base")
            cmd.append(self.lorabase_chooser.lorabase_entry.text())  # Append the lorabase_path value

        self.save_settings(model_path, gpu_layers, threads, ctx_size, bth_size, mlock, lowvram, lora_path,
                           lorabase_path, host, port, oaiport)

        self.server_runner = ServerRunner(cmd)
        self.server_runner.started.connect(self.on_server_started)
        self.server_runner.stopped.connect(self.on_server_stopped)
        self.server_runner.output_received.connect(self.on_output_received)

        self.server_runner_thread = threading.Thread(target=self.server_runner.run_server)
        self.server_runner_thread.start()

        self.save_model_tab = self.tab_widget.widget(0)
        self.save_lora_tab = self.tab_widget.widget(1)
        self.save_server_tab = self.tab_widget.widget(2)
        self.tab_widget.removeTab(0)
        self.tab_widget.insertTab(0, self.save_model_tab, 'Server Output')
        self.tab_widget.setTabVisible(1, 0)
        self.tab_widget.setTabVisible(2, 0)
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
        self.lowvram_checkbox.hide()
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
        if self.oai_checkbox.isChecked():
            api_thread = threading.Thread(target=self.start_api_script_with_delay)
            api_thread.start()

    def start_api_script_with_delay(self):
        # Delay for a specified time (in seconds) before starting the API script
        api_delay = 10  # Set the delay time in seconds (adjust as needed)
        time.sleep(api_delay)
        host = self.host_entry.text()
        port = str(self.port_entry.value())
        oaiport = str(self.oaiport_entry.value())
        # Start the api_like_OAI.py script as a separate process
        if platform.system() == "Windows":
            self.api_process = subprocess.Popen(
                ["python", "api_like_OAI.py", "--host", host, "--port", oaiport, "--llama-api",
                 "http://" + host + ":" + port],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, universal_newlines=True)
        else:
            self.api_process = subprocess.Popen(
                ["python3", "api_like_OAI.py", "--host", host, "--port", oaiport, "--llama-api",
                 "http://" + host + ":" + port],
                stdout=subprocess.PIPE,
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

        self.tab_widget.setTabVisible(1, 1)
        self.tab_widget.setTabVisible(2, 1)
        self.tab_widget.removeTab(0)
        self.tab_widget.insertTab(0, self.save_model_tab, 'Model Settings')
        self.tab_widget.setCurrentIndex(0)
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
        self.lowvram_checkbox.show()
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
        if sys.platform.startswith('win'):
            # Windows: Load settings from AppData\Roaming
            appdata_dir = os.getenv('APPDATA')
            config_file = os.path.join(appdata_dir, "llama.cpp-qt", "settings.ini")
        else:
            # Linux/Unix/Mac: Load settings from ~/.config
            config_file = os.path.join(os.path.expanduser("~"), ".config", "llama.cpp-qt", "settings.ini")
        if os.path.exists(config_file):
            config.read(config_file)
            if config.has_section("Settings"):
                if config.has_option("Settings", "model_path"):
                    model_path = config.get("Settings", "model_path")
                    self.model_chooser.model_entry.setText(model_path)

                if config.has_option("Settings", "gpu_layers"):
                    gpu_layers = config.get("Settings", "gpu_layers")
                    self.gpu_layers_entry.setValue(int(gpu_layers))

                if config.has_option("Settings", "threads"):
                    threads = config.get("Settings", "threads")
                    self.threads_entry.setValue(int(threads))

                if config.has_option("Settings", "ctx_size"):
                    ctx_size = config.get("Settings", "ctx_size")
                    self.ctx_size_entry.setValue(int(ctx_size))

                if config.has_option("Settings", "bth_size"):
                    bth_size = config.get("Settings", "bth_size")
                    self.bth_size_entry.setValue(int(bth_size))

                if config.has_option("Settings", "mlock"):
                    mlock = config.get("Settings", "mlock")  # Load mlock setting
                    self.mlock_checkbox.setChecked(mlock == "True")  # Set checkbox state

                if config.has_option("Settings", "lowvram"):
                    lowvram = config.get("Settings", "lowvram")  # Load lowvram setting
                    self.lowvram_checkbox.setChecked(lowvram == "True")  # Set checkbox state

                if config.has_option("Settings", "lora_path"):
                    lora_path = config.get("Settings", "lora_path")
                    self.lora_chooser.lora_entry.setText(lora_path)

                if config.has_option("Settings", "lorabase_path"):
                    lorabase_path = config.get("Settings", "lorabase_path")
                    self.lorabase_chooser.lorabase_entry.setText(lorabase_path)

                if config.has_option("Settings", "host"):
                    host = config.get("Settings", "host")  # Load host setting
                    self.host_entry.setText(host)

                if config.has_option("Settings", "port"):
                    port = config.get("Settings", "port")  # Load port setting
                    self.port_entry.setValue(int(port))

                if config.has_option("Settings", "oai"):
                    oai = config.get("Settings", "oai")  # Load openai setting
                    self.oai_checkbox.setChecked(oai == "True")  # Set checkbox state

                if config.has_option("Settings", "oaiport"):
                    oaiport = config.get("Settings", "oaiport")  # Load port setting
                    self.oaiport_entry.setValue(int(oaiport))

    def save_settings(self, model_path, gpu_layers, threads, ctx_size, bth_size, mlock, lowvram, lora_path,
                      lorabase_path, host, port, oaiport):
        config = configparser.ConfigParser()
        if sys.platform.startswith('win'):
            # Windows: Load settings from AppData\Roaming
            appdata_dir = os.getenv('APPDATA')
            config_file = os.path.join(appdata_dir, "llama.cpp-qt", "settings.ini")
        else:
            # Linux/Unix/Mac: Load settings from ~/.config
            config_file = os.path.join(os.path.expanduser("~"), ".config", "llama.cpp-qt", "settings.ini")
        if not config.has_section("Settings"):
            config.add_section("Settings")
        config.set("Settings", "model_path", model_path)
        config.set("Settings", "gpu_layers", gpu_layers)
        config.set("Settings", "threads", threads)
        config.set("Settings", "ctx_size", ctx_size)
        config.set("Settings", "bth_size", bth_size)
        config.set("Settings", "mlock", str(self.mlock_checkbox.isChecked()))  # Save mlock setting as string
        config.set("Settings", "lowvram", str(self.lowvram_checkbox.isChecked()))  # Save lowvram setting as string
        config.set("Settings", "lora_path", lora_path)
        config.set("Settings", "lorabase_path", lorabase_path)
        config.set("Settings", "host", self.host_entry.text())  # Save host setting
        config.set("Settings", "port", str(self.port_entry.value()))  # Save port setting as string
        config.set("Settings", "oai", str(self.oai_checkbox.isChecked()))  # Save openai setting as string
        config.set("Settings", "oaiport", str(self.oaiport_entry.value()))  # Save port setting as string
        with open(config_file, "w") as configfile:
            config.write(configfile)

    def handle_tabbar_clicked(self, index):
        print(index)

        print("x2:", index * 2)


def main():
    app = QApplication(sys.argv)
    window = LlamaServerWrapper()
    app.aboutToQuit.connect(window.stop_server)  # Ensure the server is stopped when the GUI is closed
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
