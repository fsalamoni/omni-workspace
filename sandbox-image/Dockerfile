FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    tmux \
    wget \
    jq \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for JS tasks
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest

# Install Python tools
RUN pip install --no-cache-dir \
    ipython \
    jupyter \
    requests \
    beautifulsoup4 \
    pandas \
    numpy

# Action Server dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic

WORKDIR /workspace

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# The container will run the action_server on port 8080
EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
