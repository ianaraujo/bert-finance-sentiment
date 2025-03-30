# Use a base image that includes Python and CUDA libraries, if you need GPU support.
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory for your code
WORKDIR /app

# Install dependencies
RUN pip3 install --upgrade pip

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

RUN pip3 install transformers datasets peft

# Now copy the rest of your source code
# (But we won't copy the /data or /models directories; those will be mounted as volumes)
COPY . /app

# By default, the container will start in /app
WORKDIR /app

# This is optional if you want a default command:
# CMD ["python3", "src/train_domain.py"]
# Typically we'll override this with our own 'docker run' command.

