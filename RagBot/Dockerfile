# # Use an official Python image as the base image
# FROM assistant-bot:dude_7

# # FROM python:3.10-slim
# # RUN apt-get update && apt-get -y install

# # RUN pip install --upgrade pip

# COPY . /app/RagBot
# # Set the working directory
# WORKDIR /app/RagBot

# # Copy the requirements.txt file
# # COPY requirements.txt .

# # RUN pip install -r requirements.txt
# # RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application code
# COPY . /app/RagBot

# # Make the initiation script executable
# # RUN chmod +x /app/initiate_db.sh /app/run_app.sh

# # Run the database initiation script
# # RUN ./initiate_db.sh

# # Expose the port that the FastAPI app listens on
# # RUN chmod go-w /app/RagBot/filebeat.yml
# # RUN chmod go-w /app/RagBot/prometheus.yml

# RUN apt-get install libgl1-mesa-glx

# EXPOSE 8687
# # Command to run the application
# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8687", "--reload"]




# # # Use an official Python image as the base image
FROM pytorch/pytorch:latest
# # FROM assistant-bot:dudedude
# # FROM assistant-bot:dude_6

# # FROM rocm/pytorch:latest

# RUN apt-get update && apt-get -y install curl wget  # Add actual packages you need

# # FROM python:3.10-slim
# COPY nvidia_cudnn_cu12-9.1.0.70-py3-none-manylinux2014_x86_64.whl /tmp/nvidia_cudnn_cu12-9.1.0.70-py3-none-manylinux2014_x86_64.whl
# COPY torch-2.5.1-cp310-cp310-manylinux1_x86_64.whl /tmp/torch-2.5.1-cp310-cp310-manylinux1_x86_64.whl
# COPY triton-3.1.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl /tmp/triton-3.1.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
# COPY nvidia_cublas_cu12-12.4.5.8-py3-none-manylinux2014_x86_64.whl /tmp/nvidia_cublas_cu12-12.4.5.8-py3-none-manylinux2014_x86_64.whl
COPY nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
COPY nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl /tmp/nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl
COPY nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl /tmp/nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl
COPY nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
COPY nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
COPY nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
COPY nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
COPY nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl /tmp/nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl
COPY nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
COPY nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl /tmp/nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl

# 2. Install the wheel file using pip.
#    The path provided to pip is the path *inside* the container.
RUN pip install /tmp/nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
RUN pip install /tmp/nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl
RUN pip install /tmp/nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl
RUN pip install /tmp/nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
RUN pip install /tmp/nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
RUN pip install /tmp/nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
RUN pip install /tmp/nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
RUN pip install /tmp/nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl
RUN pip install /tmp/nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
RUN pip install /tmp/nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl

# Update and install system dependencies

# Copy the requirements.txt file
COPY requirements.txt .

# Clear pip cache and install requirements with hash bypass
RUN pip cache purge
# RUN pip install --no-cache-dir --upgrade pip
# RUN pip install -r requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt


# # Install CUDA toolkit from NVIDIA repository

# couldn't download => thus changed to copy based 
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

COPY cuda-keyring_1.1-1_all.deb /tmp/cuda-keyring.deb

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && dpkg -i /tmp/cuda-keyring.deb \
    && apt-get update \
    && apt-get -y install \
    cuda-nvcc-12-1 \
    cuda-cudart-dev-12-1 \
    && rm -rf /var/lib/apt/lists/* /tmp/cuda-keyring.deb

# Set CUDA environment variables
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Copy the rest of the application code
COPY . /app/RagBot

# Set the working directory
WORKDIR /app/RagBot

RUN pip install flash
RUN pip uninstall -y ninja && pip install ninja
RUN pip install packaging
RUN pip install flash-attn
RUN pip install uvicorn

# # Make the initiation script executable
# # RUN chmod +x /app/initiate_db.sh /app/run_app.sh

# # Run the database initiation script
# # RUN ./initiate_db.sh

# # Expose the port that the FastAPI app listens on
# # RUN chmod go-w /app/RagBot/filebeat.yml
# # RUN chmod go-w /app/RagBot/prometheus.yml
# # EXPOSE 8687 8585
# # RUN chmod +x /app/RagBot/start.sh
# # # Command to run the application
# # CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8687", "--reload"]
# # CMD ["/app/RagBot/start.sh"]

