FROM python:3.10-slim

# Install system packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        git \
        curl \
        build-essential \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    black \
    pylint \
    pytest \
    pytest-cov \
    ipython

# Create a non-root user
RUN useradd -m -s /bin/bash developer \
    && chown -R developer:developer /home/developer

USER developer
WORKDIR /workspace

# Install the package in development mode
COPY --chown=developer:developer . .
RUN pip install --user -e . 