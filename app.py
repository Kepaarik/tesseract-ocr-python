"""
Tesseract OCR Test Project
A simple Flask web application to test Tesseract OCR functionality.
"""

import os
import sys
from flask import Flask, render_template, request, jsonify
import pytesseract
from PIL import Image
import io

# Явно указываем путь к исполняемому файлу tesseract
# Tesseract обычно установлен в /usr/bin/tesseract в Linux/Docker окружениях
tesseract_cmd = '/usr/bin/tesseract'

if os.path.isfile(tesseract_cmd):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    TESSERACT_AVAILABLE = True
else:
    # Пытаемся найти через PATH
    import shutil
    tesseract_cmd = shutil.which('tesseract')
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        TESSERACT_AVAILABLE = True
    else:
        TESSERACT_AVAILABLE = False

app = Flask(__name__)

# Проверка доступности Tesseract при старте
def check_tesseract_status():
    """Проверяет, доступен ли Tesseract и возвращает статус."""
    if not TESSERACT_AVAILABLE:
        return False, "Tesseract executable not found in system"
    try:
        version = pytesseract.get_tesseract_version()
        return True, f"Tesseract version: {version}"
    except Exception as e:
        return False, str(e)

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
    if not TESSERACT_AVAILABLE:
        return "ERROR: tesseract is not installed or it's not in your PATH"
    try:
        version = pytesseract.get_tesseract_version()
        return str(version)
    except Exception as e:
        return f"Error: {str(e)}"


def get_available_languages():
    """Get list of available Tesseract languages."""
    if not TESSERACT_AVAILABLE:
        return ["ERROR: tesseract is not installed or it's not in your PATH"]
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
    # Default to both English and Russian
    default_lang = 'eng+rus'
    return render_template('index.html', 
                         tesseract_version=tesseract_version,
                         available_languages=available_languages,
                         default_lang=default_lang)


@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    """API endpoint for OCR processing."""
    if not TESSERACT_AVAILABLE:
        return jsonify({'error': 'Tesseract is not installed or not in your PATH'}), 503
        
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
        
        # Get optional parameters - default to eng+rus for bilingual support
        lang = request.form.get('lang', 'eng+rus')
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
    """Test endpoint to verify Tesseract is working with English and Russian."""
    try:
        from PIL import ImageDraw, ImageFont
        
        # Create a test image with both English and Russian text
        img = Image.new('RGB', (500, 150), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a font that supports Cyrillic
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 24)
            except:
                font = ImageFont.load_default()
        
        # Add both English and Russian text
        english_text = "Hello World! OCR Test 123."
        russian_text = "Привет мир! Тест OCR 123."
        
        draw.text((10, 30), english_text, fill='black', font=font)
        draw.text((10, 70), russian_text, fill='black', font=font)
        
        # Perform OCR with both English and Russian languages
        text = pytesseract.image_to_string(img, lang='eng+rus')
        
        # Check if both languages are detected
        has_english = 'Hello' in text or 'World' in text or 'OCR' in text
        has_russian = 'Привет' in text or 'мир' in text or 'Тест' in text
        
        return jsonify({
            'success': True,
            'tesseract_version': get_tesseract_version(),
            'available_languages': get_available_languages(),
            'test_image_english': english_text,
            'test_image_russian': russian_text,
            'ocr_result': text.strip(),
            'english_detected': has_english,
            'russian_detected': has_russian,
            'both_languages_working': has_english and has_russian
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
