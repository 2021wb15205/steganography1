from flask import Flask, render_template_string, request, send_from_directory
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = "images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------------------
# Steganography Logic
# ----------------------------
def genData(data):
    return [format(ord(i), '08b') for i in data]

def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):
        pixels = [value for value in next(imdata)[:3] +
                  next(imdata)[:3] +
                  next(imdata)[:3]]

        for j in range(0, 8):
            if (datalist[i][j] == '0' and pixels[j] % 2 != 0):
                pixels[j] -= 1
            elif (datalist[i][j] == '1' and pixels[j] % 2 == 0):
                pixels[j] += 1

        if i == lendata - 1:
            if pixels[-1] % 2 == 0:
                pixels[-1] += 1
        else:
            if pixels[-1] % 2 != 0:
                pixels[-1] -= 1

        yield tuple(pixels[0:3])
        yield tuple(pixels[3:6])
        yield tuple(pixels[6:9])

def encode_image(input_image, message, output_image):
    image = Image.open(input_image, 'r')
    newimg = image.copy()
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPix(newimg.getdata(), message):
        newimg.putpixel((x, y), pixel)
        if x == w - 1:
            x = 0
            y += 1
        else:
            x += 1

    newimg.save(output_image)

def decode_image(image_path):
    image = Image.open(image_path, 'r')
    data = ''
    imgdata = iter(image.getdata())

    while True:
        pixels = [value for value in next(imgdata)[:3] +
                  next(imgdata)[:3] +
                  next(imgdata)[:3]]

        binstr = ''
        for i in pixels[:8]:
            binstr += '0' if i % 2 == 0 else '1'

        data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            return data

# ----------------------------
# HTML + CSS (inline templates)
# ----------------------------
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Image Steganography</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            width: 500px;
            text-align: center;
        }
        h1 { color: #007bff; }
        form { margin: 20px 0; }
        label { display: block; margin-top: 10px; font-weight: bold; }
        textarea, input[type="file"] {
            margin-top: 5px; width: 100%; padding: 8px;
            border-radius: 6px; border: 1px solid #ccc;
        }
        button {
            margin-top: 15px; padding: 10px 20px; border: none;
            border-radius: 6px; background: #007bff; color: white;
            font-size: 16px; cursor: pointer;
        }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Image Steganography</h1>

        <h2>Encode a Message</h2>
        <form action="/encode" method="post" enctype="multipart/form-data">
            <label>Select Image:</label>
            <input type="file" name="image" required>
            <label>Secret Message:</label>
            <textarea name="message" rows="4" required></textarea>
            <button type="submit">Encode</button>
        </form>

        <hr>

        <h2>Decode a Message</h2>
        <form action="/decode" method="post" enctype="multipart/form-data">
            <label>Select Encoded Image:</label>
            <input type="file" name="image" required>
            <button type="submit">Decode</button>
        </form>

        {% if result %}
        <div class="result">
            {{ result|safe }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# ----------------------------
# Flask Routes
# ----------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML)

@app.route("/encode", methods=["POST"])
def encode():
    image = request.files["image"]
    message = request.form["message"]

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(filepath)

    output_path = os.path.join(app.config["UPLOAD_FOLDER"], "encoded_" + image.filename)
    encode_image(filepath, message, output_path)

    return render_template_string(INDEX_HTML, result=f"""
        ✅ Message encoded!<br>
        <a href='/images/{os.path.basename(output_path)}' download>Download Encoded Image</a>
    """)

@app.route("/decode", methods=["POST"])
def decode():
    image = request.files["image"]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(filepath)

    hidden_message = decode_image(filepath)
    return render_template_string(INDEX_HTML, result=f"<h3>Decoded Message:</h3><p>{hidden_message}</p>")

@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ----------------------------
# Run Server
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
