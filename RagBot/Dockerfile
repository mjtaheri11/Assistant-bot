# Use an official Python image as the base image
FROM assistant-bot:dude_6

# FROM python:3.10-slim
# RUN apt-get update && apt-get -y install

# RUN pip install --upgrade pip

# Set the working directory
WORKDIR /app/RagBot

# Copy the requirements.txt file
# COPY requirements.txt .

# RUN pip install -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/RagBot

# Make the initiation script executable
# RUN chmod +x /app/initiate_db.sh /app/run_app.sh

# Run the database initiation script
# RUN ./initiate_db.sh

# Expose the port that the FastAPI app listens on
# RUN chmod go-w /app/RagBot/filebeat.yml
# RUN chmod go-w /app/RagBot/prometheus.yml
EXPOSE 8687
# Command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8687", "--reload"]
