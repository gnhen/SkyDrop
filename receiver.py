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
import os
import mimetypes

app = Flask(__name__)

# Read the secret key and credentials from key.txt
with open("key.txt", "r") as f:
    lines = f.read().strip().split("\n")
    app.secret_key = lines[1]
    credentials = lines[0].split(":")
    USERNAME = credentials[0]
    PASSWORD = credentials[1]

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit
SAVE_DIR = "received_files"
os.makedirs(SAVE_DIR, exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USERNAME and password == PASSWORD:
            user = User(username)
            login_user(user)
            return redirect(url_for("index"))
        return "Invalid credentials"
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return send_from_directory(".", "index.html")


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


@app.route("/src/<path:filename>")
@login_required
def serve_src(filename):
    return send_from_directory("src", filename)


@app.route("/<path:filename>")
@login_required
def serve_root(filename):
    return send_from_directory(".", filename)


# Download Files
@app.route("/received_files/<filename>")
@login_required
def download_file(filename):
    return send_from_directory(SAVE_DIR, filename)


# Get Text
@app.route("/get_text")
@login_required
def get_text():
    text_path = os.path.join(SAVE_DIR, "received_text.txt")
    if os.path.exists(text_path):
        with open(text_path, "r") as f:
            return f.read()
    return "No text received yet."


# Get Files List
@app.route("/get_files")
@login_required
def get_files():
    files = [
        {"name": f, "mtime": os.path.getmtime(os.path.join(SAVE_DIR, f))}
        for f in os.listdir(SAVE_DIR)
        if f != "received_text.txt"
    ]
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return jsonify(files)


# Rename File
@app.route("/rename_file", methods=["POST"])
@login_required
def rename_file():
    old_name = request.form.get("old_name")
    new_name = request.form.get("new_name")
    if not old_name or not new_name:
        return "Invalid request", 400

    old_path = os.path.join(SAVE_DIR, old_name)
    new_path = os.path.join(SAVE_DIR, new_name)

    if not os.path.exists(old_path):
        return "File not found", 404

    os.rename(old_path, new_path)
    return "File renamed", 200


# Upload File
@app.route("/upload_file", methods=["POST"])
@login_required
def upload_file():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    file_path = os.path.join(SAVE_DIR, file.filename)
    file.save(file_path)
    print("File uploaded:", file.filename)

    # Keep only the 10 most recent files
    files = [
        {"name": f, "mtime": os.path.getmtime(os.path.join(SAVE_DIR, f))}
        for f in os.listdir(SAVE_DIR)
        if f != "received_text.txt"
    ]
    files.sort(key=lambda x: x["mtime"], reverse=True)
    if len(files) > 10:
        for file in files[10:]:
            os.remove(os.path.join(SAVE_DIR, file["name"]))

    return "File uploaded", 200


# Receive Text or Files
@app.route("/receive", methods=["POST"])
def receive_file():
    username = request.headers.get("Username")
    password = request.headers.get("Password")
    filename = request.headers.get("X-File-Name")
    file_ext = request.headers.get("X-File-Extension", "")
    content_type = request.content_type

    print("=== Received Request ===")
    print(f"Content-Type: {content_type}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Form Data: {request.form}")
    print(f"Files: {request.files}")
    print(f"Data Length: {request.content_length}")
    print("======================")

    if username != USERNAME or password != PASSWORD:
        print("Authentication failed")
        return "Invalid credentials", 401

    try:
        # Handle file uploads via multipart/form-data
        if request.files:
            for key, file in request.files.items():
                if file.filename:
                    print(f"Processing multipart file: {file.filename}")
                    safe_filename = os.path.basename(file.filename)
                    file_path = os.path.join(SAVE_DIR, safe_filename)
                    file.save(file_path)
                    print(f"Saved file to: {file_path}")
                    return "File received", 200

        # Handle raw file upload
        if filename and request.content_length > 0:
            print(f"Processing raw file: {filename}")
            safe_filename = os.path.basename(filename)

            # Determine file extension
            if file_ext:
                # Use provided extension
                if not safe_filename.lower().endswith(f".{file_ext.lower()}"):
                    safe_filename = f"{safe_filename}.{file_ext}"
            elif content_type and content_type != "application/octet-stream":
                # Try to get extension from content type
                ext = mimetypes.guess_extension(content_type)
                if ext and not safe_filename.lower().endswith(ext.lower()):
                    safe_filename = f"{safe_filename}{ext}"

            file_path = os.path.join(SAVE_DIR, safe_filename)
            with open(file_path, "wb") as f:
                f.write(request.get_data())
            print(f"Saved raw file to: {file_path}")
            return "File received", 200

        # Handle text content
        if request.form.get("text"):
            content = request.form.get("text")
            print(f"Processing text: {content}")
            text_path = os.path.join(SAVE_DIR, "received_text.txt")

            # Read existing lines or create empty list
            lines = []
            if os.path.exists(text_path):
                with open(text_path, "r") as f:
                    lines = f.readlines()

            # Add new content as first line
            lines.insert(0, content + "\n")

            # Keep only 10 most recent lines
            lines = lines[:10]

            # Write back to file
            with open(text_path, "w") as f:
                f.writelines(lines)

            return "Text received", 200

        return "No content received", 400

    except Exception as e:
        print(f"Error processing request: {e}")
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
