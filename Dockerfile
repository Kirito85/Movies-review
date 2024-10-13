# Step 1: Use an official Python runtime as a base image
FROM python:3.9-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the rest of the app's code
COPY . /app

# Step 5: Expose the port the app runs on
EXPOSE 5000

# Step 6: Define environment variable for Flask
ENV FLASK_APP=app.py

# Step 7: Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]