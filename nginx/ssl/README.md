# SSL Certificate and Key placeholders
# In production, replace these with actual SSL certificates
# Generate self-signed certificates for development:
# openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# This directory should contain:
# - cert.pem (SSL certificate)
# - key.pem (SSL private key)