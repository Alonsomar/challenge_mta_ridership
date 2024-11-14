# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Dash is running on
EXPOSE 8050

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
