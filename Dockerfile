FROM python:3.11-slim
WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Install Python requirements (GitHub will do this in seconds)
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt --retries 10

# Set up paths and directories
ENV PYTHONPATH=/app
RUN mkdir -p /app/data && chmod 777 /app/data

# Copy code and run
COPY . .
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]