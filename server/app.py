from flask import Flask, send_from_directory, request
import os
import qrcode
from datetime import datetime

app = Flask(__name__)

# ---------------- PATH SETUP ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PHOTO_FOLDER = os.path.join(BASE_DIR, "..", "Photos")
QR_FOLDER = os.path.join(BASE_DIR, "..", "qr")
LOG_FILE = os.path.join(BASE_DIR, "..", "download_logs.txt")

os.makedirs(QR_FOLDER, exist_ok=True)

# --------------IP--------------
GALLERY_URL = "https://qr-photo-share.onrender.com"


# ---------------- ROUTES ----------------
# Gallery


@app.route("/")
def gallery():
    images = os.listdir(PHOTO_FOLDER)

    html = """
    <html>
    <head>
        <title>QR Photo Share</title>
        <meta http-equiv="refresh" content="5">
        <link rel="stylesheet" href="/static/style.css?v=2">
    </head>
    <body>

    <h1>QR Photo Share</h1>

    <div class="container">
        <p>Scan the QR code to access this gallery</p>
        <img src="/qr" width="180">
        <p><b>Gallery auto-refreshes every 5 seconds</b></p>

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

    </body>
    </html>
    """

    return html


@app.route("/photos/<filename>")
def serve_photo(filename):
    return send_from_directory(PHOTO_FOLDER, filename)
# ------------Image Categories------------


@app.route("/")
def categories():
    categories = [
        folder for folder in os.listdir(PHOTO_FOLDER)
        if os.path.isdir(os.path.join(PHOTO_FOLDER, folder))
    ]


@app.route("/category/<category>")
def category_gallery(category):
    category_path = os.path.join(PHOTO_FOLDER, category)


# Download


@app.route("/download/<filename>")
def download_photo(filename):
    ip = request.remote_addr
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as log:
        log.write(f"{time} | {ip} | {filename}\n")

    return send_from_directory(PHOTO_FOLDER, filename, as_attachment=True)


@app.route("/qr")
def serve_qr():
    qr_path = os.path.join(QR_FOLDER, "gallery_qr.png")

    if not os.path.exists(qr_path):
        qr = qrcode.make(GALLERY_URL)
        qr.save(qr_path)

    return send_from_directory(QR_FOLDER, "gallery_qr.png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
