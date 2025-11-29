from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
import io
import os

# Import modul steganografi dan watermarking yang sudah dipisahkan
from steganography import encode_message_lsb, decode_message_lsb, get_max_message_size
from watermarking import (
    add_visible_watermark,
    add_visible_watermark_image,
    add_invisible_watermark,
    extract_invisible_watermark,
    compare_images
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Routes
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/steganografi")
def steganografi_page():
    return render_template('steganografi.html')

@app.route("/watermarking")
def watermarking_page():
    return render_template('watermarking.html')

@app.route("/steganography/encode", methods=['POST'])
def stego_encode():
    try:
        if 'image' not in request.files or 'message' not in request.form:
            return jsonify({'error': 'Image and message required'}), 400

        file = request.files['image']
        message = request.form['message']

        # Open image
        image = Image.open(file.stream)

        # Encode message with steps
        stego_image, steps = encode_message_lsb(image, message, return_steps=True)

        # Save to bytes
        img_io = io.BytesIO()
        stego_image.save(img_io, 'PNG')
        img_io.seek(0)

        # Convert to base64 for JSON response
        import base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': img_base64,
            'steps': steps
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/steganography/decode", methods=['POST'])
def stego_decode():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Image required'}), 400

        file = request.files['image']
        image = Image.open(file.stream)

        # Decode message with steps
        message, steps = decode_message_lsb(image, return_steps=True)

        return jsonify({
            'success': True,
            'message': message,
            'steps': steps
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/watermark/visible", methods=['POST'])
def watermark_visible():
    try:
        if 'image' not in request.files or 'text' not in request.form:
            return jsonify({'error': 'Image and text required'}), 400

        file = request.files['image']
        watermark_text = request.form['text']
        position = request.form.get('position', 'bottom-right')
        opacity = int(request.form.get('opacity', 128))

        # Open image
        image = Image.open(file.stream)

        # Add watermark with steps
        watermarked_image, steps = add_visible_watermark(image, watermark_text, position, opacity, return_steps=True)

        # Save to bytes
        img_io = io.BytesIO()
        watermarked_image.save(img_io, 'PNG')
        img_io.seek(0)

        # Convert to base64
        import base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': img_base64,
            'steps': steps
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/watermark/image", methods=['POST'])
def watermark_image():
    try:
        if 'image' not in request.files or 'logo' not in request.files:
            return jsonify({'error': 'Base image and logo required'}), 400

        base_file = request.files['image']
        logo_file = request.files['logo']
        position = request.form.get('position', 'bottom-right')
        opacity = int(request.form.get('opacity', 128))
        scale = float(request.form.get('scale', 0.2))

        # Open images
        base_image = Image.open(base_file.stream)
        logo_image = Image.open(logo_file.stream)

        # Add watermark with steps
        watermarked_image, steps = add_visible_watermark_image(base_image, logo_image, position, opacity, scale, return_steps=True)

        # Save to bytes
        img_io = io.BytesIO()
        watermarked_image.save(img_io, 'PNG')
        img_io.seek(0)

        # Convert to base64
        import base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': img_base64,
            'steps': steps
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/watermark/invisible/add", methods=['POST'])
def watermark_invisible_add():
    try:
        if 'image' not in request.files or 'text' not in request.form:
            return jsonify({'error': 'Image and text required'}), 400

        file = request.files['image']
        watermark_text = request.form['text']

        # Open image
        image = Image.open(file.stream)

        # Add invisible watermark
        watermarked_image = add_invisible_watermark(image, watermark_text)

        # Save to bytes
        img_io = io.BytesIO()
        watermarked_image.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='watermarked_invisible.png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/watermark/invisible/extract", methods=['POST'])
def watermark_invisible_extract():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Image required'}), 400

        file = request.files['image']
        image = Image.open(file.stream)

        # Extract watermark
        watermark = extract_invisible_watermark(image)

        return jsonify({'watermark': watermark})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
