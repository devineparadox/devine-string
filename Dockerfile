# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot script when the container launches
CMD ["python", "session_generator_bot.py"]
