# Use official Python image
FROM python:3.13.2

# Set the working directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the app files
COPY . .

# Set environment variable for Flask
ENV FLASK_ENV=development

# Expose Flask port
EXPOSE 5000

# Start Flask with auto-reload enabled
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]
