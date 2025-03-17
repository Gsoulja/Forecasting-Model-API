# Forecasting API Deployment Guide

This repository contains a time series forecasting API built with FastAPI and Hugging Face models. This guide will walk you through deploying the API on a VPS with Docker, Nginx, and setting up SSL for secure access.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [VPS Deployment Guide](#vps-deployment-guide)
  - [1. Prepare Your VPS](#1-prepare-your-vps)
  - [2. Deploy with Docker](#2-deploy-with-docker)
  - [3. Set Up Nginx as Reverse Proxy](#3-set-up-nginx-as-reverse-proxy)
  - [4. Secure with SSL (HTTPS)](#4-secure-with-ssl-https)
- [Testing Your API](#testing-your-api)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Prerequisites

- A VPS with Ubuntu 20.04+ (DigitalOcean, AWS, Linode, etc.)
- SSH access to your VPS
- A domain name (optional but recommended)
- Basic knowledge of Linux commands

## Project Structure

```
forecast-api/
├── app.py                 # FastAPI application
├── download_model.py      # Script to download Hugging Face models
├── Dockerfile             # Docker container configuration
├── docker-compose.yml     # Docker Compose setup
├── requirements.txt       # Python dependencies
└── README.md              # This documentation
```

## Local Development

Before deploying to a VPS, test your API locally:

```bash
# Clone the repository or create these files
git clone https://github.com/yourusername/forecast-api.git
cd forecast-api

# Install dependencies
pip install -r requirements.txt

# Download a model
python download_model.py --model distilbert-base-uncased --type sequence_classification

# Run the API locally
uvicorn app:app --reload

# Test the API at http://localhost:8000/docs
```

## VPS Deployment Guide

### 1. Prepare Your VPS

```bash
# Connect to your VPS
ssh username@your-vps-ip

# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker  # Apply group changes without logging out

# Install Docker Compose
sudo apt install docker-compose-plugin
```

### 2. Deploy with Docker

```bash
# Create a directory for your application
mkdir -p ~/forecast-api
cd ~/forecast-api

# Clone your repository or upload your files
# Option 1: Clone from Git (if using a repository)
git clone https://github.com/yourusername/forecast-api.git .

# Option 2: Upload files via SCP (from your local machine)
# scp -r ./forecast-api/* username@your-vps-ip:~/forecast-api/

# Build and run your Docker containers
docker compose up -d

# Check if the container is running
docker ps

# Check logs if needed
docker logs forecast-api
```

### 3. Set Up Nginx as Reverse Proxy

Nginx will forward requests to your Docker container:

```bash
# Install Nginx
sudo apt install nginx

# Create a new Nginx configuration
sudo nano /etc/nginx/sites-available/forecast-api
```

Add the following configuration (replace `yourdomain.com` with your domain or server IP):

```nginx
server {
    listen 80;
    server_name yourdomain.com;  # Or your VPS IP address

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration:

```bash
# Create a symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/forecast-api /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# If the test is successful, restart Nginx
sudo systemctl restart nginx
```

### 4. Secure with SSL (HTTPS)

```bash
# Install Certbot (Let's Encrypt client)
sudo apt install certbot python3-certbot-nginx

# Obtain an SSL certificate (requires a domain name)
sudo certbot --nginx -d yourdomain.com

# Follow the prompts to complete the setup
# Certbot will modify your Nginx configuration automatically
```

Your API is now accessible securely at `https://yourdomain.com`!

## Testing Your API

You can test your deployed API using Postman:

### Example 1: Testing the Health Endpoint

1. Open Postman
2. Create a GET request to `https://yourdomain.com/health`
3. Send the request to verify the API is running

### Example 2: Forecasting with JSON Data

1. Create a POST request to `https://yourdomain.com/forecast/`
2. Select Body > raw > JSON
3. Add sample data:

```json
{
  "dates": [
    "2023-01-01", "2023-01-08", "2023-01-15", "2023-01-22", 
    "2023-01-29", "2023-02-05", "2023-02-12", "2023-02-19"
  ],
  "values": [
    1200, 1350, 1280, 1420, 1510, 1380, 1450, 1550
  ],
  "horizon": 4
}
```

4. Send the request and check the forecast results

### Example 3: Forecasting with CSV Upload

1. Create a POST request to `https://yourdomain.com/forecast-from-csv/`
2. Select Body > form-data
3. Add the following key-value pairs:
   - Key: `file` (Type: File) → Select your CSV file
   - Key: `date_column` (Type: Text) → Value: `date`
   - Key: `value_column` (Type: Text) → Value: `sales`
   - Key: `horizon` (Type: Text) → Value: `4`
4. Send the request and check the forecast results

## Troubleshooting

### Docker Issues

```bash
# Check container status
docker ps -a

# View container logs
docker logs forecast-api

# Restart the container
docker restart forecast-api

# Rebuild and restart (if you made changes)
docker compose down
docker compose up -d --build
```

### Nginx Issues

```bash
# Check Nginx status
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

### SSL/HTTPS Issues

```bash
# Test SSL renewal
sudo certbot renew --dry-run

# Check SSL certificate status
sudo certbot certificates
```

## Maintenance

### Updating Your API

```bash
# Pull latest code (if using Git)
cd ~/forecast-api
git pull

# Rebuild and restart containers
docker compose down
docker compose up -d --build
```

### Automatic SSL Renewal

Let's Encrypt certificates expire after 90 days. Certbot creates a timer that automatically renews certificates before they expire:

```bash
# Check if the renewal timer is active
sudo systemctl status certbot.timer
```

### Backups

Regular backups of your model files and configurations are recommended:

```bash
# Backup your model files
tar -czvf backup-models.tar.gz ~/forecast-api/models

# Backup Docker configuration files
tar -czvf backup-config.tar.gz ~/forecast-api/*.py ~/forecast-api/docker-compose.yml ~/forecast-api/Dockerfile ~/forecast-api/requirements.txt
```

---

That's it! Your forecasting API should now be securely deployed on your VPS. If you have any questions or issues, please open an issue in this repository.
