FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Add this line to copy the script into the container
COPY scripts/create_superuser.py /app/scripts/create_superuser.py

# Update the CMD to run the script before starting the application
CMD ["sh", "-c", "python scripts/create_superuser.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]