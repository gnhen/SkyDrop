# SkyDrop

<p align="center">
   <img src="static/src/SkyDropICON.png" height="200">
</p>

**🎉 Now Modernized with Enhanced Security & Docker Support!**

# What is this?

SkyDrop is an open source, lightweight, cross-platform AirDrop alternative server.

It receives text and files via HTTP requests and displays them on a web interface for easy access across devices. Perfect for sharing content between iOS devices, Android, and desktop computers.

**Key Features:**
- 🔒 Secure authentication with CSRF protection and rate limiting
- 📦 Docker support for easy deployment
- 🚀 Modern Python backend with Flask
- 🎨 Clean, responsive web interface
- 📱 iOS Shortcut integration
- 🔄 Keeps 10 most recent items (text and files)

# ❗ Watch the Demo Video on YouTube
<p align="center">
<a href="https://www.youtube.com/watch?v=SV0vZcAXVro" target="_blank">
  <img src="static/src/skydropVid.png" width="560" height="315" />
</a>
</p>

---

# 🚀 Quick Start

## Option 1: Docker (Recommended - Clone and Run!)

```bash
# Clone and start in 3 commands!
git clone <your-repo-url>
cd SkyDrop
docker-compose up -d

# That's it! Access at http://localhost:5000
# Default login: admin / admin

# ⚠️ IMPORTANT: Change credentials immediately for production!
# Edit .env file, then restart:
docker-compose restart

# View logs
docker-compose logs -f
```

Access at `http://localhost:5000`

## Option 2: Local Python Installation

```bash
# Clone and navigate to directory
git clone <your-repo-url>
cd SkyDrop

# Run the startup script (Linux/Mac)
./start.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: Create local environment overrides
cp .env .env.local
# Edit .env.local with your custom settings

python receiver.py
```

**Note:** The default `.env` file is included for easy setup. For production, create `.env.local` with secure credentials.

---

# 📋 Setup Guide

## 1. Server Setup

### Prerequisites
- Python 3.11+ OR Docker
- A device that's always running (Raspberry Pi, VPS, or local server)
- Static IP or domain name

### Configuration

1. **For testing/development:** Just use the defaults
   - The included `.env` file has working defaults
   - Login with `admin` / `admin`

2. **For production deployment:**
   ```bash
   # Option A: Edit .env directly
   nano .env
   
   # Option B: Create local override (recommended)
   cp .env .env.local
   nano .env.local
   ```

3. **Generate secure credentials:**
   ```bash
   # Generate secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Generate secure password
   python -c "import secrets; print(secrets.token_urlsafe(16))"
   ```

4. **Update your values:**
   ```env
   SECRET_KEY=<your-generated-secret-key>
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=<your-generated-password>
   ```

### Network Setup

Choose one of these options:

**Option A: Static IP (Local Network)**
1. Configure your Raspberry Pi/server with a static IP
2. Access via `http://192.168.1.X:5000`

**Option B: CloudFlare Tunnel (Recommended for Remote Access)**
1. Install CloudFlare Tunnel on your server
2. Configure tunnel to point to `localhost:5000`
3. Access via your CloudFlare URL

**Option C: Port Forwarding**
1. Forward port 5000 on your router to your server
2. Access via your public IP
3. ⚠️ Requires proper security setup

## 2. iOS Shortcut Setup

1. [Download the Shortcut](https://www.icloud.com/shortcuts/beb1a4544f67442f98d4582a6d78f0bd)
2. Edit the shortcut:
   - Change URL to your server: `http://YOUR-IP:5000/receive`
   - Set Username and Password (from your `.env`)
3. Add to Share Sheet for quick access
4. Optionally add to home screen

## 3. Android / Other Platforms

Create HTTP POST requests to `/receive` with:
- Headers: `Username`, `Password`
- Form data: `text` for text content
- Or file upload with `X-File-Name` header

---

# 🔒 Security Features

**NEW in Modernized Version:**
- ✅ CSRF protection on all forms
- ✅ XSS prevention with proper HTML escaping
- ✅ Rate limiting to prevent abuse
- ✅ Input validation and sanitization
- ✅ Secure session management
- ✅ Environment-based configuration
- ✅ Structured logging

---

# 📚 Documentation

- **[MODERNIZATION.md](MODERNIZATION.md)** - Detailed migration guide and new features
- **Configuration** - See `.env.example` for all options
- **API Endpoints** - See code comments in `receiver.py`

---

# 🛠️ Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run in development mode
export FLASK_ENV=development
python receiver.py

# Run tests (coming soon)
pytest tests/
```

---

# 💡 Tips

1. **Bookmark the index page** on all your devices for quick access
2. **Use CloudFlare Tunnel** for secure external access without port forwarding
3. **Enable HTTPS** in production with nginx + Let's Encrypt
4. **Regular backups** of your `received_files/` directory
5. **Monitor logs** for suspicious activity

---

# 🔄 Migration from Old Version

If updating from the original version:

1. **Backup your data:**
   ```bash
   cp -r received_files received_files.backup
   cp key.txt key.txt.backup
   ```

2. **Convert to new format:**
   - Read credentials from `key.txt`
   - Add to `.env` file instead
   - Run new version

See [MODERNIZATION.md](MODERNIZATION.md) for detailed migration steps.

---

# ⚠️ Security Warnings

### ⚠️ Keep Credentials Private
- Never share your `.env` file
- Use strong, unique passwords
- Change default credentials immediately

### ⚠️ HTTPS in Production
- Use reverse proxy (nginx/Caddy) with SSL
- Never send credentials over unencrypted HTTP on public networks
- Consider using CloudFlare Tunnel for built-in encryption

### ⚠️ Regular Updates
- Keep dependencies updated: `pip install -U -r requirements.txt`
- Monitor security advisories
- Review logs regularly

---

# 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

**Wanted:**
- Android app/shortcut equivalent
- Additional platform integrations
- UI improvements
- Test coverage

---

# 📜 License

MIT License - See LICENSE file for details

---

# 🙏 Credits

Original concept and implementation by Grant Hendricks
Modernization updates: Enhanced security, Docker support, and code refactoring

---

**Enjoy SkyDrop! 🎉**

For issues or questions, please open a GitHub issue.
