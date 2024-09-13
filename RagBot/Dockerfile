# Use an official Python image as the base image
FROM ragbot-api:latest
#RUN apt-get update && apt-get -y install

# Set the working directory
WORKDIR /app/ragbot

# Copy the requirements.txt file
#COPY requirements.txt .
#RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Install dependencies after cache
#RUN pip install python-docx==1.1.2

# Copy the rest of the application code
COPY . /app

# Make the initiation script executable
# RUN chmod +x /app/initiate_db.sh /app/run_app.sh

# Run the database initiation script
# RUN ./initiate_db.sh

# Expose the port that the FastAPI app listens on
EXPOSE 8687

# Command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8687", "--reload"]
