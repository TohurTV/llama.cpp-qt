# llama.cpp-qt

![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)

This repository contains a Python-based graphical wrapper for the LLama.cpp server, providing a user-friendly interface
for configuring and running the server. LLama.cpp is a lightweight implementation of GPT-like models.

## Requirements

Before you begin, ensure you have met the following requirements:

- **Python 3.6 or higher:** You can download it from the [official Python website](https://www.python.org/downloads/).
- **pyqt5 or Python-AnyQT**
- **Python flask and requests:** Required for the OpenAI like api wrapper.
- **llama.cpp requirements:**You can learn the requirements for CPU,Cuda, or AMD rocm builds here, [Llama.cpp Github](https://github.com/ggerganov/llama.cpp).
## Build

To build and run the LLama.cpp Server Wrapper, follow these steps:

1. Clone this repository to your local machine:
   ```sh
   git clone https://github.com/your-username/llama-cpp-wrapper.git

2. Change your current directory to the cloned repository:
   ```sh
   cd llama-cpp-wrapper

3. Run the build for your platform:
   for AMD GPUs run
   ```sh
   sh ./build-rocm.sh
4. Run llama.cpp-qt
   ```sh
   ./llama.cpp-qt