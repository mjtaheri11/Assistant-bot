# # Use an official Python image as the base image
# FROM pytorch/pytorch:latest
# FROM assistant-bot:dudedude
FROM assistant-bot:dude_6

# FROM rocm/pytorch:latest

# RUN apt-get update && apt-get -y install curl wget  # Add actual packages you need

# FROM python:3.10-slim

# Copy the requirements.txt file
# COPY requirements.txt .

# RUN pip install -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Install CUDA toolkit from NVIDIA repository

# RUN apt-get update && apt-get install -y \
#     wget \
#     ca-certificates \
#     && wget -O /tmp/cuda-keyring.deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb \
#     && dpkg -i /tmp/cuda-keyring.deb \
#     && apt-get update \
#     && apt-get install -y \
#     cuda-nvcc-12-1 \
#     cuda-cudart-dev-12-1 \
#     && rm -rf /var/lib/apt/lists/* /tmp/cuda-keyring.deb

# # Set CUDA environment variables
# ENV CUDA_HOME=/usr/local/cuda
# ENV PATH=$CUDA_HOME/bin:$PATH
# ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Copy the rest of the application code
COPY . /app/RagBot

# Set the working directory
WORKDIR /app/RagBot

# RUN pip install flash
# RUN pip uninstall -y ninja && pip install ninja
# RUN pip install packaging
# RUN pip install flash-attn
# RUN pip install uvicorn

# Make the initiation script executable
# RUN chmod +x /app/initiate_db.sh /app/run_app.sh

# Run the database initiation script
# RUN ./initiate_db.sh

# Expose the port that the FastAPI app listens on
# RUN chmod go-w /app/RagBot/filebeat.yml
# RUN chmod go-w /app/RagBot/prometheus.yml
EXPOSE 8687 8585
RUN chmod +x /app/RagBot/start.sh
# # Command to run the application
# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8687", "--reload"]
CMD ["/app/RagBot/start.sh"]