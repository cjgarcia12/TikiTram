# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install SSL certificates
RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates

# Copy files
COPY main_test.py ./
COPY scripts ./scripts
COPY data ./data
COPY config.json ./
COPY .env ./
COPY requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt

CMD ["python", "main_test.py"]