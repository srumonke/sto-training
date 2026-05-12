# Container Security: Multiple issues for scanners to find

# Issue: Using outdated base image with known CVEs Test
FROM python:3.8-slim-buster

# Issue: Running as root (no USER directive)

# Issue: Secrets baked into image layer
ENV DATABASE_PASSWORD="Super$ecret123!"
ENV AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
ENV AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

WORKDIR /app

# Issue: Installing unnecessary packages increases attack surface
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    netcat \
    telnet \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Issue: Exposing debug port
EXPOSE 5000

# Issue: Running with debug mode enabled
CMD ["python", "src/app.py"]
