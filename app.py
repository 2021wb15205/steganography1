from flask import Flask, render_template, request, send_from_directory
from en import encode_image, decode_image
import os

app = Flask(__name__)
UPLOAD_FOLDER = "images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/encode", methods=["POST"])
def encode():
    image = request.files["image"]
    message = request.form["message"]

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(filepath)

    output_path = os.path.join(app.config["UPLOAD_FOLDER"], "encoded_" + image.filename)
    encode_image(filepath, message, output_path)

    return render_template("index.html", result=f"""
        ✅ Message encoded!<br>
        <a href='/images/{os.path.basename(output_path)}' download>Download Encoded Image</a>
    """)

@app.route("/decode", methods=["POST"])
def decode():
    image = request.files["image"]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(filepath)

    hidden_message = decode_image(filepath)
    return render_template("index.html", result=f"<h3>Decoded Message:</h3><p>{hidden_message}</p>")

@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True)
