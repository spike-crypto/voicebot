# Use Python 3.10 (stable and compatible)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend folder
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the container root
COPY backend/ .

# Create uploads directory
RUN mkdir -p uploads && chmod 777 uploads

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Set environment variables
ENV FLASK_APP=run.py
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "run.py"]
