# Apache Deployment Guide

If you prefer to use Apache instead of Nginx, follow these instructions to set up your Forecasting API with Apache on your VPS.

## Setting up Apache as a Reverse Proxy

### 1. Install Apache

```bash
# Install Apache
sudo apt update
sudo apt install apache2

# Enable necessary modules
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod ssl
```

### 2. Create a Virtual Host Configuration

```bash
# Create a new configuration file
sudo nano /etc/apache2/sites-available/forecast-api.conf
```

Add the following configuration (replace `yourdomain.com` with your domain or server IP):

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAdmin webmaster@yourdomain.com
    
    # Proxy requests to the Docker container
    ProxyPreserveHost On
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/
    
    # Logging
    ErrorLog ${APACHE_LOG_DIR}/forecast-api-error.log
    CustomLog ${APACHE_LOG_DIR}/forecast-api-access.log combined
</VirtualHost>
```

### 3. Enable the Site

```bash
# Enable the site
sudo a2ensite forecast-api.conf

# Test the configuration
sudo apache2ctl configtest

# Restart Apache
sudo systemctl restart apache2
```

### 4. Secure with SSL (HTTPS)

```bash
# Install Certbot for Apache
sudo apt install certbot python3-certbot-apache

# Obtain an SSL certificate
sudo certbot --apache -d yourdomain.com

# Follow the prompts to complete the setup
# Certbot will modify your Apache configuration automatically
```

## Troubleshooting Apache

```bash
# Check Apache status
sudo systemctl status apache2

# Test Apache configuration
sudo apache2ctl configtest

# Check error logs
sudo tail -f /var/log/apache2/forecast-api-error.log

# Check access logs
sudo tail -f /var/log/apache2/forecast-api-access.log
```

## Maintenance

```bash
# Restart Apache after configuration changes
sudo systemctl restart apache2

# Enable Apache to start on boot
sudo systemctl enable apache2
```

Now your Forecasting API should be accessible through Apache at `https://yourdomain.com`!
