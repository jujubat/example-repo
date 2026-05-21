# Backend Dockerfile for Picup AI & Training Services
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5000
# Set environment so flask CLI knows where to find the application
ENV FLASK_APP=app.py
# Launch the server directly to avoid CLI lookup issues
CMD ["python", "app.py"]
