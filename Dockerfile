FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project configuration
COPY pyproject.toml ./

# Copy source code (ВАЖНО: ОБЯЗАТЕЛЬНО перед pip install -e .)
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy remaining files
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (for webhook mode)
EXPOSE 8080

# Command to run the application
CMD ["python", "-m", "src.main"] 