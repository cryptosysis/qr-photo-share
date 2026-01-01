from flask import Flask, send_from_directory, request, redirect, session
import os
from datetime import datetime
import qrcode

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

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
