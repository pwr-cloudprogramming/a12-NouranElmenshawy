FROM python:3.10-alpine


WORKDIR /app

# Copy the backend application files to the container
COPY backend/src/ ./backend/

# Copy the frontend application files to the container
COPY frontend/src/ ./frontend/

# Ensure that the requirements.txt file is in the context root or adjust the COPY path accordingly
COPY backend/src/requirements.txt ./

# Install the required Python packages
RUN pip install -r requirements.txt

# Environment variable to set the path to the frontend directory
ENV FRONTEND_DIR=/app/frontend

# Command to run the application
CMD ["python3", "backend/app.py"]
