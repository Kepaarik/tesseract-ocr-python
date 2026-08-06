# Tesseract OCR Test Project

A simple Flask web application to test Tesseract OCR functionality.

## Features

- 🖼️ **Image Upload**: Drag & drop or click to upload images
- 🔍 **OCR Processing**: Extract text from images using Tesseract
- 📊 **Statistics**: View confidence scores, word count, and line detection
- 🧪 **Built-in Test**: Verify Tesseract installation with automated test
- 🌐 **Multi-language Support**: Select from available Tesseract languages
- ⚙️ **Customizable**: Configure Page Segmentation Mode (PSM)

## Requirements

- Python 3.x
- Tesseract OCR
- pip packages: flask, pytesseract, pillow

## Installation

### 1. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr libtesseract-dev
sudo apt-get install tesseract-ocr-rus  # Russian language support
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # Additional languages including Russian
```

**Windows:**
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
   - Choose the latest version (e.g., `tesseract-ocr-w64-setup-5.x.x.exe`)
   
2. Run the installer and install to the default location:
   - Default path: `C:\Program Files\Tesseract-OCR\`
   - **Important:** During installation, check "Additional language data" and select **Russian (rus)** and **English (eng)**

3. After installation, verify that `tesseract.exe` exists at:
   - `C:\Program Files\Tesseract-OCR\tesseract.exe`

The application will automatically detect the Tesseract path on Windows. If you installed Tesseract to a different location, edit `app.py`:

```python
if platform.system() == 'Windows':
    tesseract_path = r"C:\Your\Custom\Path\tesseract.exe"  # Update this path
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
```

### 2. Install Python Dependencies

```bash
pip install flask pytesseract pillow
```

## Usage

### Run the Web Application

```bash
python app.py
```

Open your browser and navigate to: http://localhost:5000

### API Endpoints

#### POST /api/ocr
Process an image and extract text.

**Parameters:**
- `image`: Image file (multipart/form-data) or base64 string
- `lang`: Language code (default: 'eng')
- `psm`: Page Segmentation Mode (optional)
- `oem`: OCR Engine Mode (optional)
- `details`: Include detailed statistics (true/false)

**Example:**
```bash
curl -X POST -F "image=@test.png" -F "lang=eng" http://localhost:5000/api/ocr
```

#### GET /api/test
Run a built-in test to verify Tesseract is working correctly.

**Example:**
```bash
curl http://localhost:5000/api/test
```

## Supported Image Formats

- PNG
- JPG/JPEG
- GIF
- BMP
- TIFF
- WEBP

## Project Structure

```
/workspace
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Web interface
├── uploads/              # Temporary upload folder
├── README.md            # This file
└── requirements.txt     # Python dependencies
```

## Troubleshooting

### Tesseract Not Found (Windows)

If you get "ERROR: tesseract is not installed or it's not in your PATH" on Windows:

1. **Verify Installation**: Make sure Tesseract OCR is installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`

2. **Check the Path in Code**: The application automatically tries these paths:
   - `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
   
   If installed elsewhere, edit `app.py` and update the path:
   ```python
   if platform.system() == 'Windows':
       tesseract_path = r"C:\Your\Actual\Path\tesseract.exe"
       pytesseract.pytesseract.tesseract_cmd = tesseract_path
   ```

3. **Add to PATH (Optional)**: You can also add Tesseract to your system PATH:
   - Right-click "This PC" → Properties → Advanced System Settings
   - Click "Environment Variables"
   - Under "System variables", find and edit "Path"
   - Add: `C:\Program Files\Tesseract-OCR\`

4. **Install Language Data**: During Tesseract installation, make sure to select:
   - English (eng)
   - Russian (rus)
   
   Or re-run the installer and modify the installation to add languages.

### Tesseract Not Found (Linux/macOS)

1. Ensure Tesseract is installed: `which tesseract`
2. Install missing languages:
   - Ubuntu: `sudo apt-get install tesseract-ocr-rus`
   - macOS: `brew install tesseract-lang`

## License

MIT License
