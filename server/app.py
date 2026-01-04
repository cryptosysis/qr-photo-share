from flask import Flask, send_from_directory, request, redirect, session
import os
from datetime import datetime
import qrcode
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "change-this-secret-key"


@app.route("/")
def index():
    return redirect("/enter-name")


# -------- PATHS --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_FOLDER = os.path.join(BASE_DIR, "..", "Photos")
QR_FOLDER = os.path.join(BASE_DIR, "..", "qr")
LOG_FILE = os.path.join(BASE_DIR, "..", "download_logs.txt")

os.makedirs(QR_FOLDER, exist_ok=True)

GALLERY_URL = "https://qr-photo-share.onrender.com"

# -------- NAME ENTRY --------


@app.route("/enter-name", methods=["GET", "POST"])
def enter_name():
    if request.method == "POST":
        name = request.form.get("guest_name")
        if name:
            session["guest_name"] = name.strip()
            return redirect("/categories")

    return """
    <html>
    <head>
        <title>Welcome</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>

        <h1>Welcome 👋</h1>
        <p class="subtitle">Please enter your name to continue</p>

        <div class="container">
            <form method="POST">
                <input type="text" name="guest_name" placeholder="Your name" required
                       style="padding:12px;font-size:16px;border-radius:8px;border:none;width:260px;">
                <br><br>
                <button type="submit"
                        style="padding:12px 22px;font-size:16px;border-radius:12px;
                               border:none;background:#667eea;color:white;cursor:pointer;">
                    Continue
                </button>
            </form>
        </div>

    </body>
    </html>
    """

# -------- CATEGORY LIST --------


@app.route("/categories")
def categories():
    if "guest_name" not in session:
        return redirect("/enter-name")

    guest = session["guest_name"]

    category_folders = [
        f for f in os.listdir(PHOTO_FOLDER)
        if os.path.isdir(os.path.join(PHOTO_FOLDER, f))
    ]

    html = f"""
    <html>
    <head>
        <title>Choose Category</title>
        <link rel="stylesheet" href="/static/style.css?v=9">
    </head>
    <body>

        <h1>Welcome, {guest} 👋</h1>
        <p class="subtitle">Select a category to view photos</p>

        <div class="container">
            <div class="gallery">
    """

    for cat in category_folders:
        html += f"""
        <div class="card">
            <a href="/category/{cat}" style="padding:30px;font-size:18px;">
                {cat.replace("_", " ")}
            </a>
        </div>
        """

    html += """
            </div>
        </div>

    </body>
    </html>
    """

    return html

# -------ADMIN UPLOAD--------


ADMIN_PASSWORD = "12345"


@app.route("/admin/upload", methods=["GET", "POST"])
def admin_upload():
    message = ""

    if request.method == "POST":
        password = request.form.get("password")
        category = request.form.get("category")
        files = request.files.getlist("photos")

        if password != ADMIN_PASSWORD:
            message = "❌ Wrong admin password"

        elif not files or files[0].filename == "":
            message = "❌ No files selected"

        else:
            category_path = os.path.join(PHOTO_FOLDER, category)

            if not os.path.exists(category_path):
                message = "❌ Invalid category"

            else:
                for file in files:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(category_path, filename))

                message = f"✅ {len(files)} photo(s) uploaded successfully"

    categories = [
        f for f in os.listdir(PHOTO_FOLDER)
        if os.path.isdir(os.path.join(PHOTO_FOLDER, f))
    ]

    options = "".join(
        f"<option value='{c}'>{c.replace('_', ' ')}</option>"
        for c in categories
    )

    return f"""
    <html>
    <head>
        <title>Admin Upload</title>
        <link rel="stylesheet" href="/static/style.css">
        <style>
            .drop-zone {{
                border: 3px dashed #667eea;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                color: #667eea;
                cursor: pointer;
                margin-bottom: 20px;
            }}
            .drop-zone.dragover {{
                background: rgba(102, 126, 234, 0.15);
            }}
        </style>
    </head>
    <body>

        <h1>Admin Upload</h1>
        <p class="subtitle">Drag & drop or select multiple photos</p>

        <div class="container">
            <form method="POST" enctype="multipart/form-data" onsubmit="showUploading()">

                <input type="password" name="password" placeholder="Admin password" required><br><br>

                <select name="category" required>
                    {options}
                </select><br><br>

                <div class="drop-zone" id="drop-zone">
                    Drop photos here or click to select
                    <input type="file" name="photos" id="file-input"
                           accept="image/*" multiple hidden>
                </div>

                <button type="submit">Upload</button>

                <p id="status">{message}</p>
            </form>
        </div>

        <script>
            const dropZone = document.getElementById("drop-zone");
            const fileInput = document.getElementById("file-input");

            dropZone.onclick = () => fileInput.click();

            dropZone.addEventListener("dragover", e => {{
                e.preventDefault();
                dropZone.classList.add("dragover");
            }});

            dropZone.addEventListener("dragleave", () => {{
                dropZone.classList.remove("dragover");
            }});

            dropZone.addEventListener("drop", e => {{
                e.preventDefault();
                dropZone.classList.remove("dragover");
                fileInput.files = e.dataTransfer.files;
            }});

            function showUploading() {{
                document.getElementById("status").innerText = "⏳ Uploading...";
            }}
            <ul id="file-list" style="list-style:none;padding:0;color:#333;"></ul>

        </script>

    </body>
    </html>
    """


# -------- CATEGORY GALLERY --------


@app.route("/category/<category>")
def category_gallery(category):
    if "guest_name" not in session:
        return redirect("/enter-name")

    category_path = os.path.join(PHOTO_FOLDER, category)

    if not os.path.exists(category_path):
        return "Category not found", 404

    images = os.listdir(category_path)

    html = f"""
    <html>
    <head>
        <title>{category}</title>
        <link rel="stylesheet" href="/static/style.css?v=9">
    </head>
    <body>

        <h1>{category.replace("_", " ")}</h1>

        <div class="container">
            <div class="gallery">
    """

    for img in images:
        if img.lower().endswith((".jpg", ".png", ".jpeg")):
            html += f"""
            <div class="card">
                <img src="/photos/{category}/{img}">
                <a href="/download/{category}/{img}">Download</a>
            </div>
            """

    html += """
            </div>
        </div>

    </body>
    </html>
    """

    return html

# -------- SERVE FILES --------


@app.route("/photos/<category>/<filename>")
def serve_photo(category, filename):
    return send_from_directory(os.path.join(PHOTO_FOLDER, category), filename)

# -------- DOWNLOAD + LOG --------


@app.route("/download/<category>/<filename>")
def download_photo(category, filename):
    ip = request.remote_addr
    guest = session.get("guest_name", "Unknown")
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as log:
        log.write(f"{time} | {guest} | {category} | {filename} | {ip}\n")

    return send_from_directory(
        os.path.join(PHOTO_FOLDER, category),
        filename,
        as_attachment=True
    )

# -------- QR --------


@app.route("/qr")
def serve_qr():
    qr_path = os.path.join(QR_FOLDER, "gallery_qr.png")
    if not os.path.exists(qr_path):
        qrcode.make(GALLERY_URL).save(qr_path)
    return send_from_directory(QR_FOLDER, "gallery_qr.png")

# -------- RUN --------


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
