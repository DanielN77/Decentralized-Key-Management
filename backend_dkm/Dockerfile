# Python based image
FROM python:3.12

# Define working directory inside container
WORKDIR /backend_dkm

# Copy source code into the container
COPY . /backend_dkm

# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command for running flask app
CMD ["python", "backend_dkm.py"]