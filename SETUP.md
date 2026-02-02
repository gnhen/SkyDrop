## Setup Instructions

### Local Development

1. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run the application:**
   ```bash
   python receiver.py
   ```

### Docker Deployment

1. **Using Docker Compose (Recommended):**
   ```bash
   # Create .env file with your settings
   cp .env.example .env
   
   # Start the application
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Stop the application
   docker-compose down
   ```

2. **Using Docker only:**
   ```bash
   # Build image
   docker build -t skydrop:latest .
   
   # Run container
   docker run -d \
     -p 5000:5000 \
     -v $(pwd)/received_files:/app/received_files \
     -e SECRET_KEY=your-secret-key \
     -e ADMIN_USERNAME=admin \
     -e ADMIN_PASSWORD=your-password \
     --name skydrop \
     skydrop:latest
   ```

## Migration from Old Version

If you're migrating from the original version:

1. **Backup your data:**
   ```bash
   cp -r received_files received_files.backup
   cp key.txt key.txt.backup
   ```

2. **Convert credentials to .env:**
   ```bash
   # Read old key.txt (format: username:password\nsecret_key)
   # Create new .env file
   echo "ADMIN_USERNAME=your_username" > .env
   echo "ADMIN_PASSWORD=your_password" >> .env
   echo "SECRET_KEY=your_secret_key" >> .env
   ```

3. **Update dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python receiver.py  # Auto-creates database on first run
   ```

## Security Improvements Made

### XSS Protection
- **Before:** String concatenation with basic quote escaping
  ```javascript
  html += `<div onclick="copyText('${line.replace(/'/g, "\\'")}')">${line}</div>`;
  ```
- **After:** DOM manipulation with textContent
  ```javascript
  const lineDiv = document.createElement('div');
  lineDiv.textContent = line;  // Safe - auto-escapes HTML
  ```

### CSRF Protection
- Added CSRF tokens to all forms
- Configured Flask-WTF for automatic protection
- Added CSRF exemption only for external API endpoint with custom auth

### Rate Limiting
- Login: 10 requests/minute
- API endpoints: 20-60 requests/minute
- Upload: 20 requests/minute

### Input Validation
- Filename sanitization with path traversal prevention
- File size validation
- File type checking
- Empty input rejection

## Configuration Options

All settings can be configured via environment variables:

```bash
# Flask Settings
FLASK_ENV=development          # or 'production'
SECRET_KEY=change-this         # Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password

# Application
MAX_CONTENT_LENGTH=16777216    # 16MB in bytes
SAVE_DIR=received_files

# Database
DATABASE_URL=sqlite:///skydrop.db

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://

# Server
HOST=0.0.0.0
PORT=5000
```

## Testing

The application includes basic error handling. For production use, consider:

```bash
# Install dev dependencies
pip install pytest pytest-flask pytest-cov

# Run tests (to be added)
pytest tests/
```

## Production Deployment

For production environments:

1. **Use strong credentials:**
   ```bash
   export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   export ADMIN_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")
   ```

2. **Enable HTTPS:**
   - Use nginx or Caddy as reverse proxy
   - Set up Let's Encrypt SSL certificates
   - Update SESSION_COOKIE_SECURE=True in production config

3. **Use production-grade database:**
   - PostgreSQL recommended over SQLite
   - Configure DATABASE_URL appropriately

4. **Set up monitoring:**
   - Add application monitoring (e.g., Sentry)
   - Configure log aggregation
   - Set up health check alerts

## Troubleshooting

### CSRF Token Issues
If you see CSRF errors, ensure:
- The login form includes `{{ csrf_token() }}`
- JavaScript includes CSRF token in POST requests
- Cookies are enabled

### Rate Limiting Errors
If hitting rate limits:
- Adjust limits in `config.py`
- Use Redis for distributed rate limiting: `RATELIMIT_STORAGE_URL=redis://localhost:6379`

### File Upload Issues
- Check `MAX_CONTENT_LENGTH` setting
- Verify file permissions on `received_files/` directory
- Check disk space
