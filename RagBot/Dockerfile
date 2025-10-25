# # # Use an official Python image as the base image
# # FROM assistant-bot:dude_4

# # # FROM python:3.10-slim
# # RUN apt-get update && apt-get -y install

# # # RUN pip install --upgrade pip

# # COPY . /app/RagBot
# # # Set the working directory
# # WORKDIR /app/RagBot

# # # Copy the requirements.txt file
# # # COPY requirements.txt .

# # # RUN pip install -r requirements.txt
# # # RUN pip install --no-cache-dir -r requirements.txt

# # # Copy the rest of the application code
# # ENV CUDA_HOME=/usr/local/cuda
# # ENV PATH=$CUDA_HOME/bin:$PATH
# # ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# # # Make the initiation script executable
# # RUN chmod +x ./run_app.sh
# # # RUN pip install 'markitdown[all]'
# # # RUN pip install --upgrade transformers==4.51.0
# # # RUN pip install flash-attn==2.8.3

# # # Run the database initiation script
# # # RUN ./initiate_db.sh

# # # Expose the port that the FastAPI app listens on
# # # RUN chmod go-w /app/RagBot/filebeat.yml
# # # RUN chmod go-w /app/RagBot/prometheus.yml

# # # RUN apt-get install libgl1-mesa-glx

# # EXPOSE 8689
# # EXPOSE 8585
# # # Command to run the application
# # # CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8689", "--reload"]
# # CMD ["./run_app.sh"]




# # ========================= uncomment the following lines for creating new image. ===================================

# # # Use an official Python image as the base image
# FROM pytorch/pytorch:latest
# # FROM assistant-bot:dudedude
# # FROM assistant-bot:dude_6
# ENV PATH=/usr/local/cuda-12.0/bin:$PATH
# ENV LD_LIBRARY_PATH=/usr/local/cuda-12.0/lib64:$LD_LIBRARY_PATH

# # FROM rocm/pytorch:latest
# # Add actual packages you need
# RUN apt-get update && apt-get -y install curl wget  

# # FROM python:3.10-slim
# # COPY ./nvidia-files/nvidia_cudnn_cu12-9.1.0.70-py3-none-manylinux2014_x86_64.whl /tmp/nvidia_cudnn_cu12-9.1.0.70-py3-none-manylinux2014_x86_64.whl
# # COPY ./nvidia-files/torch-2.5.1-cp310-cp310-manylinux1_x86_64.whl /tmp/torch-2.5.1-cp310-cp310-manylinux1_x86_64.whl
# # COPY ./nvidia-files/triton-3.1.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl /tmp/triton-3.1.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
# # COPY ./nvidia-files/nvidia_cublas_cu12-12.4.5.8-py3-none-manylinux2014_x86_64.whl /tmp/nvidia_cublas_cu12-12.4.5.8-py3-none-manylinux2014_x86_64.whl
# # COPY ./nvidia-files/nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# # COPY ./nvidia-files/nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl /tmp/nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl
# # COPY ./nvidia-files/nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl /tmp/nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl
# # COPY ./nvidia-files/nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# # COPY ./nvidia-files/nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# # COPY ./nvidia-files/nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# # COPY ./nvidia-files/nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# # COPY ./nvidia-files/nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl /tmp/nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl
# # COPY ./nvidia-files/nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /tmp/nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# # COPY ./nvidia-files/nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl /tmp/nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl

# COPY ./nvidia-files/nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl ./nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl
# COPY ./nvidia-files/nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl ./nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl
# COPY ./nvidia-files/nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl ./nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl
# COPY ./nvidia-files/nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl ./nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl
# COPY ./nvidia-files/scipy-1.16.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./scipy-1.16.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/torch-2.7.1-cp313-cp313-manylinux_2_28_x86_64.whl ./torch-2.7.1-cp313-cp313-manylinux_2_28_x86_64.whl
# COPY ./nvidia-files/cuda-keyring_1.1-1_all.deb ./cuda-keyring_1.1-1_all.deb
# # COPY ./nvidia-files/triton-3.3.1-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl ./triton-3.3.1-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl

# # 2. Install the wheel file using pip.
# #    The path provided to pip is the path *inside* the container.

# RUN pip install ./nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl 
# RUN pip install ./nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl 
# RUN pip install ./nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl 
# RUN pip install ./nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl 
# RUN pip install ./nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl 
# RUN pip install ./nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl 
# RUN pip install ./nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl 
# RUN pip install ./nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl 
# RUN pip install ./nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl 
# RUN pip install ./nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# RUN pip install./cuda-keyring_1.1-1_all.deb

# # RUN apt-get update && apt-get install -y \
# #     wget \
# #     ca-certificates \
# #     gnupg \
# #     && wget -O /tmp/cuda-keyring.deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb \
# #     && dpkg -i /tmp/cuda-keyring.deb \
# #     && apt-get update \
# #     && apt-get install -y \
# #     cuda-nvcc-12-0 \
# #     cuda-cudart-dev-12-0 \
# #     cuda-compiler-12-0 \
# #     && rm -rf /var/lib/apt/lists/* /tmp/cuda-keyring.deb

# # Run pip install ./triton-3.3.1-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl

# # Update and install system dependencies

# # Set CUDA environment variables (make sure they're consistent)
# ENV CUDA_HOME=/usr/local/cuda-12.0
# ENV PATH=$CUDA_HOME/bin:$PATH
# ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# # Verify nvcc is available
# RUN nvcc --version

# # Copy the requirements.txt file
# COPY requirements.txt .

# # Clear pip cache and install requirements with hash bypass
# # RUN pip cache purge
# # couldn't download => thus changed to copy based 


# # Install CUDA toolkit from NVIDIA repository
# # RUN apt-get update && apt-get install -y \
# #     wget \
# #     ca-certificates \
# #     && wget -O /tmp/cuda-keyring.deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb \
# #     && dpkg -i /tmp/cuda-keyring.deb \
# #     && apt-get update \
# #     && apt-get install -y \
# #     cuda-nvcc-12-8 \
# #     cuda-cudart-dev-12-8 \
# #     && rm -rf /var/lib/apt/lists/* /tmp/cuda-keyring.deb


# # COPY cuda-keyring_1.1-1_all.deb /tmp/cuda-keyring.deb

# # RUN apt-get update && apt-get install -y \
# #     ca-certificates \
# #     && dpkg -i /tmp/cuda-keyring.deb \
# #     && apt-get update \
# #     && apt-get -y install \
# #     cuda-nvcc-12-1 \
# #     cuda-cudart-dev-12-1 \
# #     && rm -rf /var/lib/apt/lists/* /tmp/cuda-keyring.deb

# # Set CUDA environment variables
# ENV CUDA_HOME=/usr/local/cuda
# ENV PATH=$CUDA_HOME/bin:$PATH
# ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# # RUN pip install --no-cache-dir --upgrade pip
# # RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
# RUN pip install https://files.pythonhosted.org/packages/be/56/6e46904a6a408e5fbc9f6a345ed94bfb73bdb5251ce39bb60b6bf023c0ed/pyairports-2.1.1.tar.gz 
# RUN pip install -r requirements.txt

# # Copy the rest of the application code
# COPY . /app/RagBot

# # Set the working directory
# WORKDIR /app/RagBot

# # RUN pip install flash

# # RUN pip uninstall -y ninja && pip install ninja
# # RUN pip install packaging
# # RUN pip install flash-attn
# # RUN pip install uvicorn

# # Make the initiation script executable
# # RUN chmod +x /app/initiate_db.sh /app/run_app.sh

# # Run the database initiation script
# # RUN ./initiate_db.sh

# # Expose the port that the FastAPI app listens on
# # RUN chmod go-w /app/RagBot/filebeat.yml
# # RUN chmod go-w /app/RagBot/prometheus.yml
# # EXPOSE 8689 8585
# # RUN chmod +x /app/RagBot/start.sh
# # # Command to run the application
# # CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8689", "--reload"]
# # CMD ["/app/RagBot/start.sh"]



FROM pytorch/pytorch:latest

ENV PATH=/usr/local/cuda-12.0/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/cuda-12.0/lib64:$LD_LIBRARY_PATH

# Add actual packages you need
RUN apt-get update && apt-get -y install curl  

# Copy NVIDIA wheel files
# COPY ./nvidia-files/nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl ./nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl
# COPY ./nvidia-files/nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl ./nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl
# COPY ./nvidia-files/nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl ./nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl
# COPY ./nvidia-files/nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl ./nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl
# COPY ./nvidia-files/scipy-1.16.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl ./scipy-1.16.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
# COPY ./nvidia-files/torch-2.7.1-cp313-cp313-manylinux_2_28_x86_64.whl ./torch-2.7.1-cp313-cp313-manylinux_2_28_x86_64.whl

# Copy flash-attn wheel file (you'll need to download this manually)
# COPY ./nvidia-files/flash_attn-2.8.1+cu12torch2.4cxx11abiTRUE-cp310-cp310-linux_x86_64.whl ./flash_attn-2.8.1+cu12torch2.4cxx11abiTRUE-cp310-cp310-linux_x86_64.whl

# Copy the local cuda-keyring deb file
# COPY ./nvidia-files/cuda-keyring_1.1-1_all.deb ./cuda-keyring_1.1-1_all.deb

# Install NVIDIA wheel files
# RUN pip install ./nvidia_cublas_cu12-12.6.4.1-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl \
#     ./nvidia_nvjitlink_cu12-12.6.85-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl \
#     ./nvidia_cusparse_cu12-12.5.4.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl \
#     ./nvidia_curand_cu12-10.3.7.77-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl \
#     ./nvidia_cufft_cu12-11.3.0.4-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl \
#     ./nvidia_cudnn_cu12-9.5.1.17-py3-none-manylinux_2_28_x86_64.whl \
#     ./nvidia_cuda_nvrtc_cu12-12.6.77-py3-none-manylinux2014_x86_64.whl \
#     ./nvidia_cusolver_cu12-11.7.1.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl \
#     ./nvidia_cusparselt_cu12-0.6.3-py3-none-manylinux2014_x86_64.whl \
#     ./nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl


RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    gnupg \
    && wget -O /tmp/cuda-keyring.deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb \
    && dpkg -i /tmp/cuda-keyring.deb \
    && apt-get update \
    && apt-get install -y \
    cuda-nvcc-12-0 \
    cuda-cudart-dev-12-0 \
    cuda-compiler-12-0 \
    && rm -rf /var/lib/apt/lists/* /tmp/cuda-keyring.deb

# Install CUDA toolkit using local cuda-keyring file
RUN apt-get update && apt-get install -y \
    ca-certificates \
    gnupg \
    && dpkg -i ./cuda-keyring_1.1-1_all.deb \
    && apt-get update \
    && apt-get install -y \
    cuda-nvcc-12-0 \
    cuda-cudart-dev-12-0 \
    cuda-compiler-12-0 \
    && rm -rf /var/lib/apt/lists/* ./cuda-keyring_1.1-1_all.deb

# Set CUDA environment variables
ENV CUDA_HOME=/usr/local/cuda-12.0
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Verify nvcc is available
RUN nvcc --version

# Copy the requirements.txt file
COPY requirements.txt .

# Install flash-attn from local wheel file
# RUN pip install ./flash_attn-2.8.1+cu12torch2.4cxx11abiTRUE-cp310-cp310-linux_x86_64.whl

# Install pyairports and other requirements
RUN pip install https://files.pythonhosted.org/packages/be/56/6e46904a6a408e5fbc9f6a345ed94bfb73bdb5251ce39bb60b6bf023c0ed/pyairports-2.1.1.tar.gz 
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app/RagBot

# Set the working directory
WORKDIR /app/RagBot


