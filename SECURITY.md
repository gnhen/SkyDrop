# Security Policy

## Default Credentials Warning

This repository includes a `.env` file with default credentials (`admin`/`admin`) for easy testing and development.

**YOU MUST CHANGE THESE BEFORE PRODUCTION USE!**

## Production Deployment Checklist

Before deploying SkyDrop to production, ensure you:

### 1. **Change Default Credentials**

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Generate a secure password
python -c "import secrets; print(secrets.token_urlsafe(16))"

# Update .env or create .env.local with these values
```

### 2. **Enable HTTPS**

- Use a reverse proxy (nginx, Caddy, Traefik)
- Obtain SSL certificates (Let's Encrypt recommended)
- Never transmit credentials over plain HTTP on public networks

### 3. **Network Security**

- Use CloudFlare Tunnel for secure external access (recommended)
- OR properly configure firewall rules if using port forwarding
- Consider using a VPN for remote access
- Restrict access to trusted IP addresses if possible

### 4. **Environment Variables**

```bash
# Ensure these are set securely:
SECRET_KEY=<strong-random-key>
ADMIN_USERNAME=<your-username>
ADMIN_PASSWORD=<strong-password>
FLASK_ENV=production
```

### 5. **File Permissions**

```bash
# Protect your environment files
chmod 600 .env
chmod 600 .env.local
chmod 600 .env.production
```

### 6. **Regular Updates**

```bash
# Keep dependencies updated
pip install -U -r requirements.txt

# Or rebuild Docker image
docker-compose build --pull
docker-compose up -d
```

### 7. **Monitoring**

- Review logs regularly: `docker-compose logs -f`
- Monitor for failed login attempts
- Watch for unusual file upload patterns

## Security Features

SkyDrop includes the following security measures:

- CSRF protection on all forms
- XSS prevention with proper HTML escaping
- Rate limiting (10 login attempts/min, 20 uploads/min)
- Path traversal prevention
- Input validation and sanitization
- Secure session management
- HTTP security headers

## Rate Limits

Default rate limits (per IP address):
- Login: 10 requests/minute
- File upload: 20 requests/minute
- API endpoints: 30-60 requests/minute

Configure in `config.py` if needed.

## Known Limitations

1. **SQLite Database**: Default SQLite is suitable for single-user/small deployments. For high-traffic production, consider PostgreSQL.

2. **Session Storage**: Uses in-memory sessions by default. For distributed deployments, configure Redis.

3. **File Storage**: Files stored on filesystem. Consider S3/MinIO for cloud deployments.

4. **No Built-in HTTPS**: Requires reverse proxy for SSL/TLS.

## Reporting a Vulnerability

If you discover a security vulnerability:

1. Open an issue
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Best Practices

### For Local Network Use
- Use static IP
- Keep credentials strong
- Enable router firewall
- Regular backups

### For Internet-Facing Deployments
- Use CloudFlare Tunnel
- OR use nginx with Let's Encrypt SSL
- Enable all security headers
- Use strong, unique passwords
- Consider 2FA (future feature)
- Regular security audits
- Monitor access logs

### For Docker Deployments
- Use Docker secrets for sensitive data (advanced)
- Run container as non-root user (future improvement)
- Keep base images updated
- Use Docker Bench for security scanning

