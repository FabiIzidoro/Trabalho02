from flask import Flask, render_template, request, send_file
from PIL import Image
import os
from uuid import uuid4

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def encode_lsb(image, message):
    binary_message = ''.join(format(ord(c), '08b') for c in message) + '1111111111111110'
    pixels = image.getdata()
    new_pixels = []

    binary_index = 0
    for pixel in pixels:
        new_pixel = list(pixel)
        for i in range(3):
            if binary_index < len(binary_message):
                new_pixel[i] = new_pixel[i] & ~1 | int(binary_message[binary_index])
                binary_index += 1
        new_pixels.append(tuple(new_pixel))

    encoded_img = Image.new(image.mode, image.size)
    encoded_img.putdata(new_pixels)
    return encoded_img

def decode_lsb(image):
    pixels = image.getdata()
    bits = ""
    for pixel in pixels:
        for i in range(3):
            bits += str(pixel[i] & 1)
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    message = ""
    for c in chars:
        if message.endswith('\xFE'):
            break
        message += c
    return message[:-1]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    image = Image.open(request.files['image']).convert('RGB')
    message = request.form['message'] + '\xFE'
    encoded_image = encode_lsb(image, message)
    output_path = os.path.join(UPLOAD_FOLDER, f'encoded_{uuid4().hex}.png')
    encoded_image.save(output_path)
    return send_file(output_path, as_attachment=True)

@app.route('/decode', methods=['POST'])
def decode():
    image = Image.open(request.files['image']).convert('RGB')
    message = decode_lsb(image)
    return render_template('index.html', decoded_message=message)

if __name__ == '__main__':
    app.run(debug=True)