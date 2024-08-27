FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the required Python packages
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copy the ragbot directory into the working directory
COPY ragbot/ ./ragbot/

# Expose the port that the FastAPI app listens on
EXPOSE 8687

CMD ["python", "/app/ragbot/initiate_vdb"]

# Command to run the application
CMD ["python", "/app/ragbot/api.py", "--port", "8687"]
