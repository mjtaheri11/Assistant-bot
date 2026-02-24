# Use an official Python runtime as a parent image
# FROM mlrepo.abramad.com/python:3.11-slim
FROM 172.29.14.10:6002/da/dev/backend:1.0.3

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
# COPY requirements_3.txt .

# ffmpeg installation
# RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Install dependencies
# RUN pip install --no-cache-dir -r requirements_3.txt

# Copy the src directory to the root of the project (/app)
COPY src ./src

# Copy api.py to the root of the project (/app)
COPY api.py .

# Expose the port uvicorn will run on
EXPOSE 9090

# Command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "9090"]

# buildctl --addr tcp://buildkitd.buildkit.svc.cluster.local:80 build --frontend dockerfile.v0 --local context=. --local dockerfile=. --secret id=dockerconfig,src=$HOME/.docker/config.json --output type=image,name=172.29.14.10:6002/test-image:1.0,push=true 
