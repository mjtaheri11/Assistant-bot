# FROM python:3.10-slim
# Start from NVIDIA's CUDA image with Python support
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04


# Set the working directory inside the container
WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the required Python packages
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copy the ragbot directory into the working directory
COPY initiate_db.sh .
COPY ragbot/ ./ragbot/
COPY saved_models ./saved_models/
COPY KB-tavalla ./KB-tavalla
# Expose the port that the FastAPI app listens on
EXPOSE 8687

RUN chmod +x ./initiate_db.sh 
RUN ./initiate_db.sh

# Command to run the application
CMD ["python3", "ragbot/api.py", "--port", "8687"]
