FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire project including submodules
COPY . .

# Initialize git submodules (if not already done)
RUN git submodule update --init --recursive || true

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -e .
RUN pip install -e submodules/awlkit/

# Optional: Install Ollama support
RUN pip install -e '.[ollama]' || pip install -e .

# Create outputs directory
RUN mkdir -p outputs

# Set environment variables for better terminal interaction
ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color

# Default command to run the chat interface
CMD ["sv-agent", "chat"]