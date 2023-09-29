# llama.cpp-qt

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)

Llama.cpp-qt is a Python-based graphical wrapper for the LLama.cpp server, providing a user-friendly interface
for configuring and running the server. LLama.cpp is a lightweight implementation of GPT-like models.

## Benifits over other LLama.cpp solutions
Most other interfaces for llama.cpp run exclusively through python, meaning  its the llama.cpp converted to
python in some form or another and depending on your hardware there is overhead to running directly in python.
python is slower then C++, C++ is a Low-level programming language meaning its pretty close to the hardware, python is
a high level programming language which is fine for GUIs (llama.cpp-qt) but for applications that require high performance
such as AI models you want to be as low level as you can be. llama.cpp-qt is a wrapper for llama.cpp meaning it runs llama.cpp directly and is 
faster then other llama.cpp solutions. I personally get about double the tokens per second compared to Text Gen UI, Koboldcpp and llama-cpp-python. 
llama.cpp-qt is also cross platform meaning it runs on Linux and Windows. (macos support coming soon).

## Requirements

Before you begin, ensure you have met the following requirements:

- **Python 3.10 or higher:** You can download it from the [official Python website](https://www.python.org/downloads/) or your Linux distribution's repositories.
- **Python3-virtualenv:** For venv creation on run time/installation.
- **pyqt5 or Python-AnyQT and QT 5:** For the GUI.These should be installed by your Linux distros package manager if you want to use your system theme, if not the default QT theme will be used by the venv.
- **llama.cpp requirements:** You can learn the requirements for CPU,Cuda, or AMD rocm builds
  here, [Llama.cpp Github](https://github.com/ggerganov/llama.cpp).

## Build Linux

To build and run the LLama.cpp-qt Wrapper, follow these steps:

1. Clone this repository to your local machine:
   ```sh
   git clone https://github.com/TohurTV/llama.cpp-qt.git
   ```
2. Change your current directory to the cloned repository:
   ```sh
   cd llama.cpp-qt
   ```
3. Run the build for your platform:for AMD GPUs run
   ```sh
   sh ./build-rocm.sh
   ```
   Cuda is build-cuda.sh and cpu only build is build-cpu.sh


4. Run llama.cpp-qt
   ```sh
   ./llama.cpp-qt
   ```

## Systemwide installation

To install systemwide after running the build script run:

```sh
sh ./install.sh
```

## Windows Setup

To run the LLama.cpp-qt Wrapper, follow these steps:

1. Clone this repository to your local machine:
   ```sh
   git clone https://github.com/TohurTV/llama.cpp-qt.git
   ```
2. Change your current directory to the cloned repository:
   ```sh
   cd llama.cpp-qt
   ```

3. Download the lastest release build from [Llama.cpp Releases](https://github.com/ggerganov/llama.cpp/releases) or use the included bat files download-llama.cpp-{version).bat.
Openblas for running on cpu, Cublas for running on Nvidia GPUs, and clblast for other GPUs.
Rocm build instructions coming soon for windows.


4. If you downloaded the release from llama.cpp's github Extract the release build and copy server.exe and all of the .dlls to the llama.cpp-qt folder if you used one of the bat files proceed to next step.


5. Run the start.bat file to start the llama.cpp-qt GUI.

## Systemwide installation

Windows installers coming soon.