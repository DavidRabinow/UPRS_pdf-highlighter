# File Upload Feature

## Overview

The PDF Highlighting Tool now includes a file upload feature that allows users to upload their own PDF files for processing instead of relying on downloaded files.

## New Features

### 1. File Upload Interface

- Added a file upload input field in the web interface
- Supports only PDF files (`.pdf` extension)
- Shows file information (name and size) after selection
- Validates file type before processing

### 2. Backend File Handling

- Creates an `uploads` directory to store uploaded files
- Generates unique filenames with timestamps
- Copies uploaded files to the Downloads directory for processing
- Integrates with existing ChatGPT highlighting workflow

### 3. Status Tracking

- Displays uploaded file information in the status panel
- Tracks file processing progress
- Shows file name in status updates

## How It Works

### Frontend Changes

1. **File Upload Input**: Added a styled file input field that accepts PDF files
2. **File Validation**: JavaScript validates file type and presence before submission
3. **File Information Display**: Shows selected file name and size
4. **FormData Submission**: Uses FormData to send file and other data to backend

### Backend Changes

1. **File Upload Endpoint**: Modified `/start_automation` to handle multipart form data
2. **File Storage**: Saves uploaded files to `uploads/` directory with unique names
3. **File Processing**: Copies uploaded files to Downloads directory for ChatGPT processing
4. **Status Updates**: Includes uploaded file information in automation status

### Automation Changes

1. **File Handling**: Modified `run_highlighting` method to accept uploaded file path
2. **File Copying**: Copies uploaded file to Downloads directory for processing
3. **Integration**: Seamlessly integrates with existing ChatGPT highlighting workflow

## Usage

1. **Upload File**: Click the file upload field and select a PDF file
2. **Enter Highlight Text**: Specify what text to highlight in the PDF
3. **Configure Options**: Set name text and signature options as needed
4. **Start Processing**: Click "Start Highlighting" to begin processing
5. **Monitor Progress**: Watch the status panel for progress updates

## File Structure

```
uploads/
├── uploaded_1234567890_document1.pdf
├── uploaded_1234567891_document2.pdf
└── ...
```

## Technical Details

### File Validation

- Frontend: JavaScript validates file extension
- Backend: Python validates file type and presence
- Error handling for missing or invalid files

### Security Considerations

- File type validation prevents malicious uploads
- Unique filenames prevent conflicts
- Temporary storage in uploads directory

### Integration Points

- Works with existing `chatgpt_processor_with_highlight.py`
- Works with existing `pdf_field_filler.py`
- Maintains compatibility with existing workflow

## Testing

Use the provided test script to verify functionality:

```bash
python test_file_upload.py
```

This script creates a test PDF file and uploads it to verify the feature works correctly.

## Error Handling

- **No file selected**: Shows error message
- **Invalid file type**: Validates PDF extension
- **File processing errors**: Logged and displayed in status
- **Upload failures**: Graceful error handling with user feedback
