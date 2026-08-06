"""
Tesseract OCR Test Project
A simple Flask web application to test Tesseract OCR functionality.
"""

import os
from flask import Flask, render_template, request, jsonify
import pytesseract
from PIL import Image
import io

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_tesseract_version():
    """Get Tesseract version information."""
    try:
        version = pytesseract.get_tesseract_version()
        return str(version)
    except Exception as e:
        return f"Error: {str(e)}"


def get_available_languages():
    """Get list of available Tesseract languages."""
    try:
        langs = pytesseract.get_languages(config='')
        return langs
    except Exception as e:
        return [f"Error: {str(e)}"]


@app.route('/')
def index():
    """Render the main page."""
    tesseract_version = get_tesseract_version()
    available_languages = get_available_languages()
    return render_template('index.html', 
                         tesseract_version=tesseract_version,
                         available_languages=available_languages)


@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    """API endpoint for OCR processing."""
    if 'image' not in request.files and 'image' not in request.form:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        # Get image from form data (base64 or file upload)
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            
            image = Image.open(file.stream)
        else:
            # Handle base64 image data
            import base64
            image_data = request.form.get('image', '')
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        
        # Get optional parameters
        lang = request.form.get('lang', 'eng')
        psm = request.form.get('psm', None)
        oem = request.form.get('oem', None)
        
        # Build config string
        config = ''
        if psm:
            config += f' --psm {psm}'
        if oem:
            config += f' --oem {oem}'
        
        # Perform OCR
        text = pytesseract.image_to_string(image, lang=lang, config=config)
        
        # Get detailed data if requested
        get_details = request.form.get('details', 'false').lower() == 'true'
        response = {
            'success': True,
            'text': text,
            'language': lang
        }
        
        if get_details:
            data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
            response['details'] = {
                'confidence': sum([c for c in data['conf'] if c > 0]) / max(len([c for c in data['conf'] if c > 0]), 1),
                'words': len([t for t in data['text'] if t.strip()]),
                'lines': len(set(data['line_num']))
            }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify Tesseract is working."""
    try:
        # Create a simple test image with known text
        from PIL import ImageDraw, ImageFont
        
        # Create a simple white image with black text
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use default font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 30), "Hello World! OCR Test 123.", fill='black', font=font)
        
        # Perform OCR on the test image
        text = pytesseract.image_to_string(img, lang='eng')
        
        return jsonify({
            'success': True,
            'tesseract_version': get_tesseract_version(),
            'available_languages': get_available_languages(),
            'test_image_text': 'Hello World! OCR Test 123.',
            'ocr_result': text.strip(),
            'match': 'Hello World' in text or 'OCR Test' in text
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("Starting Tesseract OCR Test Web Application...")
    print(f"Tesseract Version: {get_tesseract_version()}")
    print(f"Available Languages: {', '.join(get_available_languages())}")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
