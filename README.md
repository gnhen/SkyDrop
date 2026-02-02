# SkyDrop

<p align="center">
   <img src="static/src/SkyDropICON.png" height="200">
</p>

# What is this?

SkyDrop is an open source, lightweight, cross-platform AirDrop alternative server.

It receives text and files via HTTP requests and displays them on a web interface for easy access across devices. Perfect for sharing content between iOS devices, Android, and desktop computers.

**Key Features:**
- Secure authentication with CSRF protection and rate limiting
- Docker support for easy deployment
- Modern Python backend with Flask
- Clean, responsive web interface
- Keeps 10 most recent items (text and files)

# Watch the Demo Video on YouTube
<p align="center">
<a href="https://www.youtube.com/watch?v=SV0vZcAXVro" target="_blank">
  <img src="static/src/skydropVid.png" width="560" height="315" />
</a>
</p>

---

# Installation

## Option 1: Docker

```bash
git clone https://github.com/gnhen/SkyDrop
cd SkyDrop
docker-compose up -d

# Default login: admin / admin

# Change credentials immediately for production!
# Edit .env file, then restart:
docker-compose restart

# View logs
docker-compose logs -f
```

Access at `http://localhost:5000`

## Option 2: Local Python Installation

```bash
# Clone and navigate to directory
git clone https://github.com/gnhen/SkyDrop
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
- Server
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
   SECRET_KEY=<secret-key>
   ADMIN_USERNAME=<user>
   ADMIN_PASSWORD=<password>
   ```
