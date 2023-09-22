#!/bin/bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make LLAMA_HIPBLAS=1 LLAMA_DISABLE_LOGS=1
  mv server \
    ../
cd ..
rm -r -f -d llama.cpp
echo "Build complete"