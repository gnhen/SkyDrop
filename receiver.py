"""
SkyDrop - Cross-platform file and text sharing application
Modernized with security enhancements and proper architecture
"""
from flask import (
    Flask,
    request,
    send_from_directory,
    jsonify,
    redirect,
    url_for,
    render_template,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
import os
import mimetypes
import logging
from datetime import datetime
from config import get_config

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config_class = get_config()
app.config.from_object(config_class)

# Initialize extensions
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=app.config['RATELIMIT_STORAGE_URL']
)

# Make CSRF token available in templates
@app.context_processor
def inject_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return dict(csrf_token=generate_csrf)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create save directory
SAVE_DIR = app.config['SAVE_DIR']
os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Database Models
class FileRecord(db.Model):
    """Track uploaded files in database"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.filename,
            'original_name': self.original_filename,
            'size': self.file_size,
            'mime_type': self.mime_type,
            'upload_date': self.upload_date.isoformat(),
            'mtime': self.upload_date.timestamp()
        }


# User model for authentication
class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# Authentication helper
def check_credentials(username, password):
    """Validate user credentials"""
    return (username == app.config['ADMIN_USERNAME'] and 
            password == app.config['ADMIN_PASSWORD'])


# Routes
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    """User login endpoint with rate limiting"""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        
        if check_credentials(username, password):
            user = User(username)
            login_user(user)
            logger.info(f"User {username} logged in successfully")
            next_page = request.args.get('next')
            return redirect(next_page or url_for("index"))
        
        logger.warning(f"Failed login attempt for username: {username}")
        return render_template("login.html", error="Invalid credentials"), 401
    
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """User logout endpoint"""
    logger.info(f"User {current_user.id} logged out")
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    """Main application page"""
    return send_from_directory(".", "index.html")


@app.route("/static/<path:filename>")
def static_files(filename):
    """Serve static files"""
    return send_from_directory("static", filename)


@app.route("/src/<path:filename>")
@login_required
def serve_src(filename):
    """Serve source files"""
    return send_from_directory("src", filename)


@app.route("/<path:filename>")
@login_required
def serve_root(filename):
    """Serve root files"""
    return send_from_directory(".", filename)


@app.route("/received_files/<filename>")
@login_required
def download_file(filename):
    """Download received files"""
    try:
        return send_from_directory(SAVE_DIR, filename)
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return "File not found", 404


@app.route("/get_text")
@login_required
@limiter.limit("60 per minute")
def get_text():
    """Get received text content"""
    text_path = os.path.join(SAVE_DIR, "received_text.txt")
    try:
        if os.path.exists(text_path):
            with open(text_path, "r", encoding="utf-8") as f:
                return f.read()
        return "No text received yet."
    except Exception as e:
        logger.error(f"Error reading text file: {e}")
        return "Error reading text", 500


@app.route("/get_files")
@login_required
@limiter.limit("60 per minute")
def get_files():
    """Get list of received files"""
    try:
        files = [
            {"name": f, "mtime": os.path.getmtime(os.path.join(SAVE_DIR, f))}
            for f in os.listdir(SAVE_DIR)
            if f != "received_text.txt"
        ]
        files.sort(key=lambda x: x["mtime"], reverse=True)
        return jsonify(files)
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({"error": "Failed to list files"}), 500


@app.route("/rename_file", methods=["POST"])
@login_required
@limiter.limit("30 per minute")
def rename_file():
    """Rename a file with validation"""
    old_name = request.form.get("old_name")
    new_name = request.form.get("new_name")
    
    if not old_name or not new_name:
        return "Missing filename", 400
    
    # Validate filenames for path traversal
    old_name = os.path.basename(old_name)
    new_name = os.path.basename(new_name)
    
    if '/' in new_name or '\\' in new_name:
        return "Invalid filename", 400
    
    old_path = os.path.join(SAVE_DIR, old_name)
    new_path = os.path.join(SAVE_DIR, new_name)
    
    try:
        if not os.path.exists(old_path):
            return "File not found", 404
        
        if os.path.exists(new_path):
            return "File with new name already exists", 409
        
        os.rename(old_path, new_path)
        logger.info(f"File renamed: {old_name} -> {new_name}")
        return "File renamed successfully", 200
    except Exception as e:
        logger.error(f"Error renaming file: {e}")
        return "Failed to rename file", 500


@app.route("/upload_file", methods=["POST"])
@login_required
@limiter.limit("20 per minute")
def upload_file():
    """Upload file through web interface"""
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    try:
        # Sanitize filename
        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(SAVE_DIR, safe_filename)
        
        # Save file
        file.save(file_path)
        logger.info(f"File uploaded via web: {safe_filename}")

        # Cleanup old files - keep only 10 most recent
        cleanup_old_files()
        
        return "File uploaded successfully", 200
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return "Failed to upload file", 500


def cleanup_old_files():
    """Keep only the 10 most recent files"""
    try:
        files = [
            {"name": f, "mtime": os.path.getmtime(os.path.join(SAVE_DIR, f))}
            for f in os.listdir(SAVE_DIR)
            if f != "received_text.txt"
        ]
        files.sort(key=lambda x: x["mtime"], reverse=True)
        
        if len(files) > 10:
            for file in files[10:]:
                file_path = os.path.join(SAVE_DIR, file["name"])
                os.remove(file_path)
                logger.info(f"Removed old file: {file['name']}")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


@app.route("/receive", methods=["POST"])
@csrf.exempt  # Exempt for external API calls - uses custom auth
@limiter.limit("30 per minute")
def receive_file():
    """Receive files or text from external sources (iOS Shortcuts, etc.)"""
    username = request.headers.get("Username")
    password = request.headers.get("Password")
    filename = request.headers.get("X-File-Name")
    file_ext = request.headers.get("X-File-Extension", "")
    content_type = request.content_type

    logger.info(f"Receive request - Content-Type: {content_type}, Filename: {filename}")

    # Authentication
    if not check_credentials(username or "", password or ""):
        logger.warning("Authentication failed for /receive endpoint")
        return "Invalid credentials", 401

    try:
        # Handle file uploads via multipart/form-data
        if request.files:
            for key, file in request.files.items():
                if file.filename:
                    logger.info(f"Processing multipart file: {file.filename}")
                    safe_filename = os.path.basename(file.filename)
                    file_path = os.path.join(SAVE_DIR, safe_filename)
                    file.save(file_path)
                    logger.info(f"Saved file: {safe_filename}")
                    cleanup_old_files()
                    return "File received successfully", 200

        # Handle raw file upload
        if filename and request.content_length and request.content_length > 0:
            logger.info(f"Processing raw file: {filename}")
            safe_filename = os.path.basename(filename)

            # Determine file extension
            if file_ext:
                if not safe_filename.lower().endswith(f".{file_ext.lower()}"):
                    safe_filename = f"{safe_filename}.{file_ext}"
            elif content_type and content_type != "application/octet-stream":
                ext = mimetypes.guess_extension(content_type)
                if ext and not safe_filename.lower().endswith(ext.lower()):
                    safe_filename = f"{safe_filename}{ext}"

            file_path = os.path.join(SAVE_DIR, safe_filename)
            with open(file_path, "wb") as f:
                f.write(request.get_data())
            logger.info(f"Saved raw file: {safe_filename}")
            cleanup_old_files()
            return "File received successfully", 200

        # Handle text content
        text_content = request.form.get("text")
        if text_content:
            logger.info("Processing text content")
            text_path = os.path.join(SAVE_DIR, "received_text.txt")

            # Read existing lines
            lines = []
            if os.path.exists(text_path):
                with open(text_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

            # Add new content as first line
            lines.insert(0, text_content + "\n")

            # Keep only 10 most recent lines
            lines = lines[:10]

            # Write back to file
            with open(text_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            logger.info("Text content saved")
            return "Text received successfully", 200

        logger.warning("No content received in request")
        return "No content received", 400

    except Exception as e:
        logger.error(f"Error processing receive request: {e}", exc_info=True)
        return f"Error: {str(e)}", 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return jsonify({"error": "Rate limit exceeded"}), 429


# Database initialization
def init_db():
    """Initialize database tables"""
    with app.app_context():
        # Ensure database directory exists
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
        
        db.create_all()
        logger.info("Database initialized")


if __name__ == "__main__":
    # Note: Database initialization commented out - not currently used
    # Uncomment when implementing database-backed file tracking
    # init_db()
    
    # Get host and port from config or environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f"Starting SkyDrop server on {host}:{port}")
    app.run(host=host, port=port, debug=app.config.get('DEBUG', False))
