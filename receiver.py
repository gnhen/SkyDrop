from flask import Flask, request, send_from_directory, jsonify
import os
import mimetypes

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit
SAVE_DIR = "received_files"
os.makedirs(SAVE_DIR, exist_ok=True)


# Serve Static Files
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/styles.css")
def styles():
    return send_from_directory(".", "styles.css")


@app.route("/scripts.js")
def scripts():
    return send_from_directory(".", "scripts.js")


@app.route("/src/<path:filename>")
def serve_src(filename):
    return send_from_directory("src", filename)


@app.route("/<path:filename>")
def serve_root(filename):
    return send_from_directory(".", filename)


# Download Files
@app.route("/received_files/<filename>")
def download_file(filename):
    return send_from_directory(SAVE_DIR, filename)


# Get Text
@app.route("/get_text")
def get_text():
    text_path = os.path.join(SAVE_DIR, "received_text.txt")
    if os.path.exists(text_path):
        with open(text_path, "r") as f:
            return f.read()
    return "No text received yet."


# Get Files List
@app.route("/get_files")
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
