# Use a lightweight Python base image
FROM python:3.9-slim

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the model to the container
COPY classification_model.h5 /app/classification_model.h5

# Copy the Flask app code to the container
COPY app.py /app/app.py

# Copy the finetune app code to the container
COPY finetune.py /app/finetune.py

# Set the working directory
WORKDIR /app

# Expose the port for the REST API
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
