# GLM-OCR GUI

A PyQt5-based graphical user interface for GLM-OCR, supporting drag-and-drop, file browsing, and clipboard paste for image/PDF text recognition.

## Features

- Drag and drop images/PDFs directly into the window
- Browse and select files via button
- Paste images directly from clipboard (Ctrl+V or button)
- Markdown-formatted OCR results display
- Export results to Markdown, JSON, or TXT format

## Requirements

1. **Ollama** - Must be running locally
   ```bash
   ollama serve
   ```

2. **GLM-OCR Model** - Must be downloaded
   ```bash
   ollama pull glm-ocr:latest
   ```

3. **Python 3.10+** with uv package manager

## Quick Start

### Option 1: Use Batch File (Windows)

Double-click `启动.bat` to automatically:
- Create virtual environment if not exists
- Install dependencies
- Launch the GUI

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/Starzzb/GLMOCR_GUI.git
cd GLMOCR_GUI

# Create virtual environment
uv venv

# Install dependencies
uv pip install PyQt5 Pillow PyYAML requests

# Run the application
.venv\Scripts\python.exe main.py
```

## Usage

### Input Methods

1. **Drag and Drop**: Drag image/PDF files onto the drop area
2. **Browse**: Click "Browse Files" button to select files
3. **Paste**: 
   - Click "Paste Image" button, or
   - Press Ctrl+V to paste clipboard image

### Supported Formats

| Format | Extensions | Max Size |
|--------|------------|----------|
| Images | .jpg, .jpeg, .png | 10 MB |
| PDF   | .pdf        | 50 MB |

### Export Results

Click "Export Result" to save recognition output as:
- Markdown file (.md)
- Plain text (.txt)
- JSON file (.json)

## Configuration

Edit `config/default_config.yaml` to customize:

```yaml
pipeline:
  ocr_api:
    api_host: "localhost"    # Ollama server host
    api_port: 11434          # Ollama server port
    api_path: "/api/generate"
    model: "glm-ocr:latest"  # Model name
    api_mode: "ollama_generate"

ocr:
  use_pdf_pipeline: true
  max_pages: 100
  timeout: 120
```

## Project Structure

```
glm_ocr_gui/
├── main.py                  # Application entry point
├── pyproject.toml           # Project configuration
├── 启动.bat                 # Windows startup script
├── config/
│   └── default_config.yaml  # Default configuration
├── core/
│   ├── config_manager.py    # Configuration loader
│   ├── file_validator.py    # File format/size validator
│   └── recognizer.py        # GLM-OCR API wrapper
├── ui/
│   ├── main_window.py       # Main window
│   ├── drop_area.py         # Drag-and-drop component
│   └── result_viewer.py     # Markdown display component
└── utils/
    └── image_utils.py       # Image preprocessing utilities
```

## Troubleshooting

### Connection Error
- Ensure Ollama is running: `ollama serve`
- Check default_config.yaml api_host and api_port settings

### Model Not Found
- Download the model: `ollama pull glm-ocr:latest`

### Import Error
- Reinstall dependencies: `uv pip install PyQt5 Pillow PyYAML requests`

## License

MIT License