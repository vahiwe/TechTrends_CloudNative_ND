# Base image python 2.7
FROM python:2.7

# Copy the techtrends directory to the image
COPY techtrends/ /app/

# Set the working directory
WORKDIR /app

# Install the requirements
RUN pip install -r requirements.txt

# Initialize the database
RUN python init_db.py

# Expose the port
EXPOSE 3111

# Run the app
CMD ["python", "app.py"]