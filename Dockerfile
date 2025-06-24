# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with legacy resolver to avoid conflicts
RUN pip install --no-cache-dir -r requirements.txt --use-deprecated=legacy-resolver

# Copy the API code
COPY api/ ./api/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run the FastAPI server
CMD ["python", "-m", "uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"] 