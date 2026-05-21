# SOP File Upload Documentation

## Supported File Formats

The SOP management system now supports uploading SOP documents in various formats:

### 1. **PDF Files (.pdf)**
- Text is extracted using PyPDF2 library
- Supports multi-page documents
- Preserves basic formatting

### 2. **Excel Files (.xlsx, .xls)**
- Data is extracted from all sheets
- Each column becomes a section with its values
- Uses pandas for processing

### 3. **Image Files (.jpg, .jpeg, .png)**
- Text is extracted using OCR (Tesseract)
- Requires Tesseract OCR to be installed on the system
- Best results with clear, high-contrast text

### 4. **Text Files (.txt)**
- Direct text reading with UTF-8 encoding
- No processing required

### 5. **Word Documents (.docx)**
- Text is extracted from paragraphs
- Preserves basic structure
- Uses python-docx library

### 6. **Google Sheets**
- Currently accepts URLs but requires API setup for automatic processing
- Placeholder implementation included

## Dependencies Required

Add these to your `requirements.txt`:

```
PyPDF2
pandas
openpyxl
pytesseract
Pillow
python-docx
```

## System Requirements

### For OCR (Image Processing):
1. Install Tesseract OCR on your system:
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`

2. Make sure Tesseract is in your PATH

### For Google Sheets Integration (Future):
1. Set up Google Cloud Project
2. Enable Google Sheets API
3. Create OAuth2 credentials
4. Configure service account or OAuth flow

## Usage

1. **Manual Entry**: Type or paste SOP content directly
2. **File Upload**: Select a file and upload - content is automatically extracted
3. **Google Sheets**: Enter the full Google Sheets URL (API integration pending)

## File Size Limits

- Default Flask upload limit: 16MB (configurable in app config)
- Consider adding file size validation for production use

## Security Considerations

- File type validation is implemented
- Temporary files are cleaned up after processing
- Consider adding virus scanning for uploaded files
- Implement user authentication and authorization

## Error Handling

The system provides detailed error messages for:
- Unsupported file types
- Corrupted files
- Missing dependencies
- Processing failures

## Future Enhancements

1. **Google Sheets API Integration**: Full OAuth2 setup for automatic sheet processing
2. **Advanced OCR**: Better image preprocessing and multiple language support
3. **Document Structure Preservation**: Maintain formatting and tables from source documents
4. **Batch Upload**: Upload multiple files at once
5. **File Versioning**: Keep track of uploaded file versions