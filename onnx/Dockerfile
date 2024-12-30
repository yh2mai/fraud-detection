# Use a lightweight Python base image
FROM python:3.9-slim

# Install ONNX Runtime and Flask
RUN pip install --no-cache-dir onnxruntime flask onnx tensorflow==2.15.0

RUN pip install numpy tf2onnx onnx-tf flask-cors

# Copy the ONNX model to the container
COPY model.onnx /app/model.onnx

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
