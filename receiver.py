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
@login_required
def receive_file():
    # Handle Text
    content = request.form.get("text")
    if content:
        text_path = os.path.join(SAVE_DIR, "received_text.txt")
        if os.path.exists(text_path):
            with open(text_path, "r") as f:
                existing_content = f.read()
            with open(text_path, "w") as f:
                f.write(content + "\n" + existing_content)
        else:
            with open(text_path, "w") as f:
                f.write(content + "\n")
        print("Text saved:", content)

        # Keep only the 10 most recent text entries
        with open(text_path, "r") as f:
            lines = f.readlines()
        if len(lines) > 10:
            with open(text_path, "w") as f:
                f.writelines(lines[:10])

    # Handle Files
    if request.data:
        # Extract filename from headers
        filename = request.headers.get("X-File-Name", "received_file")

        # Guess extension if missing
        if "." not in filename:
            mime_type = request.headers.get("Content-Type")
            ext = mimetypes.guess_extension(mime_type) or ""
            filename += ext

        file_path = os.path.join(SAVE_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(request.data)
        print("File saved:", filename)

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

    return "Received", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
