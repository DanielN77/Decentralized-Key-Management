# Python based image
FROM python:3.12

# Define working directory inside container
WORKDIR /node

# Copy source code into the container
COPY . /node

# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command for running flask app
CMD ["python", "node.py"]