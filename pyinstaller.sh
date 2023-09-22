#!/bin/bash
pyinstaller --noconfirm --onefile --clean \
--add-binary "./server:." \
--add-data "./api_like_OAI.py:." \
"./llama.py" -n "llama"
echo "Build complete"
