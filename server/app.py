from flask import Flask, send_from_directory, request, redirect, session
import os
import qrcode
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PHOTO_FOLDER = os.path.join(BASE_DIR, "..", "Photos")
QR_FOLDER = os.path.join(BASE_DIR, "..", "qr")
LOG_FILE = os.path.join(BASE_DIR, "..", "download_logs.txt")

os.makedirs(QR_FOLDER, exist_ok=True)

# Public URL (used ONLY for QR)
GALLERY_URL = "https://qr-photo-share.onrender.com"

# ---------------- NAME ENTRY ----------------


@app.route("/enter-name", methods=["GET", "POST"])
def enter_name():
    if request.method == "POST":
        name = request.form.get("guest_name")
        if name:
            session["guest_name"] = name.strip()
            return redirect("/")

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
                    Enter Gallery
                </button>
            </form>
        </div>

    </body>
    </html>
    """

# ---------------- GALLERY ----------------


@app.route("/")
def gallery():
    if "guest_name" not in session:
        return redirect("/enter-name")

    guest_name = session.get("guest_name", "Guest")
    images = os.listdir(PHOTO_FOLDER)

    html = f"""
    <html>
    <head>
        <title>Event Photo Gallery</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="/static/style.css?v=7">
    </head>
    <body>

        <h1>Event Photo Gallery</h1>
        <p class="subtitle">Welcome, {guest_name} 👋 — browse and download your photos</p>

        <div class="container">
            <div class="gallery">
    """

    for img in images:
        if img.lower().endswith((".jpg", ".png", ".jpeg")):
            html += f"""
            <div class="card">
                <img src="/photos/{img}">
                <a href="/download/{img}">Download</a>
            </div>
            """

    html += """
            </div>
        </div>

        <div class="footer">
            © Photo Share · Access via QR Code
        </div>

    </body>
    </html>
    """

    return html

# ---------------- FILE SERVING ----------------


@app.route("/photos/<filename>")
def serve_photo(filename):
    return send_from_directory(PHOTO_FOLDER, filename)

# ---------------- DOWNLOAD + LOG ----------------


@app.route("/download/<filename>")
def download_photo(filename):
    ip = request.remote_addr
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    guest = session.get("guest_name", "Unknown")

    with open(LOG_FILE, "a") as log:
        log.write(f"{time} | {guest} | {ip} | {filename}\n")

    return send_from_directory(PHOTO_FOLDER, filename, as_attachment=True)

# ---------------- QR CODE ----------------


@app.route("/qr")
def serve_qr():
    qr_path = os.path.join(QR_FOLDER, "gallery_qr.png")

    if not os.path.exists(qr_path):
        qr = qrcode.make(GALLERY_URL)
        qr.save(qr_path)

    return send_from_directory(QR_FOLDER, "gallery_qr.png")

# ---------------- RUN ----------------


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
