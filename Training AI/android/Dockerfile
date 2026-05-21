# Android (Kotlin Compose) Dockerfile
# This container is currently a simple placeholder that serves static files
# from the android/ directory. Replace with your real Android build steps
# when you have an actual application to deploy.

FROM eclipse-temurin:17-jdk

WORKDIR /app
COPY . .

# install python so we have a lightweight web server for static assets
RUN apt-get update && apt-get install -y python3 \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8080
CMD ["python3", "-m", "http.server", "8080"]
