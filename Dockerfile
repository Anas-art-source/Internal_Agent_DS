# Use the official image as a parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME FastAPI-SocketIO-App

# Run app.py when the container launches
CMD ["uvicorn", "app:app_sio", "--host", "0.0.0.0", "--port", "5000"]
