# Azure-Powered Batch Form Filler

A Python service that processes PDF forms using Azure Document Intelligence to automatically fill form fields and highlight important terms. Designed to work with your existing UI after Monday.com login and file download.

## Features

- **Azure Document Intelligence Integration**: Uses Azure's prebuilt-layout model for accurate text and layout detection
- **Smart Form Filling**: Automatically detects form labels and fills corresponding values
- **Keyword Highlighting**: Highlights important terms like "signature" and "consent" with semi-transparent overlays
- **Batch Processing**: Handles ZIP files containing multiple documents
- **File Type Support**: PDF processing with stubs for DOCX and image conversion
- **REST API**: Simple Flask endpoint for integration with your UI
- **Security**: API key authentication and automatic cleanup of temporary files

## Project Structure

```
azure-form-filler/
├── app.py                      # Flask API with /process endpoint
├── azure_processor.py          # Azure AI calls and form processing logic
├── pdf_utils.py                # PDF rendering and overlay utilities
├── converters.py               # File type conversion (PDF, DOCX, images)
├── requirements.txt            # Python dependencies
├── env.sample                  # Environment configuration template
└── README.md                   # This file
```

## Setup

### 1. Install Dependencies

```bash
cd azure-form-filler
pip install -r requirements.txt
```

### 2. Configure Azure Document Intelligence

1. Create an Azure Document Intelligence resource in the Azure portal
2. Get your endpoint URL and API key
3. Copy `env.sample` to `.env` and fill in your credentials:

```bash
cp env.sample .env
```

Edit `.env`:
```ini
AZURE_DI_ENDPOINT=https://YOUR-RESOURCE-NAME.cognitiveservices.azure.com/
AZURE_DI_KEY=YOUR-AZURE-KEY
MAX_CONTENT_LENGTH_MB=200
API_SHARED_SECRET=change-me-to-something-secure
```

### 3. Run the Service

```bash
python app.py
```

The service will start on `http://localhost:5001`

## API Usage

### Endpoint: POST /process

Process uploaded files with form filling and highlighting.

#### Request Format

**Form Data:**
- `zip_file` (file): ZIP file containing documents to process
- `file` (file): Single PDF file to process (alternative to zip_file)
- `fill_map` (string): JSON mapping field labels to values
- `highlight_terms` (string): JSON array of terms to highlight

**Headers:**
- `X-API-KEY`: Your API shared secret

#### Example Request

```bash
export API_KEY=change-me-to-something-secure

# Process a ZIP file
curl -X POST http://localhost:5001/process \
  -H "X-API-KEY: $API_KEY" \
  -F "zip_file=@/path/to/forms.zip" \
  -F 'fill_map={"name":"David Smith","dob":"1990-05-15","phone":"(555)123-4567"}' \
  -F 'highlight_terms=["signature","consent","emergency"]' \
  --output processed.zip

# Process a single PDF
curl -X POST http://localhost:5001/process \
  -H "X-API-KEY: $API_KEY" \
  -F "file=@/path/to/form.pdf" \
  -F 'fill_map={"name":"Jane Doe","address":"123 Main St"}' \
  -F 'highlight_terms=["signature"]' \
  --output processed.pdf
```

#### Response

- **Success (200)**: ZIP file containing processed documents
- **Error (4xx/5xx)**: JSON error message

### Health Check: GET /health

```bash
curl http://localhost:5001/health
```

Response: `{"status": "healthy", "service": "azure-form-filler"}`

## Form Field Mapping

The service recognizes common form field labels and maps them to your provided values:

| Key | Recognized Labels |
|-----|-------------------|
| `name` | name, patient name, full name, first name, last name, patient |
| `dob` | dob, date of birth, birth date, birthday |
| `phone` | phone, telephone, tel, phone number, mobile, cell |
| `address` | address, street address, mailing address, home address |
| `email` | email, e-mail, email address |
| `ssn` | ssn, social security, social security number |
| `id` | id, identification, patient id, account number |
| `signature` | signature, sign, signed by, patient signature |
| `consent` | consent, agreement, authorization, permission |
| `emergency` | emergency, emergency contact, next of kin |
| `insurance` | insurance, insurance provider, policy number, group number |
| `allergies` | allergies, allergic, allergy |
| `medications` | medications, meds, current medications, prescriptions |
| `diagnosis` | diagnosis, condition, medical condition |
| `treatment` | treatment, therapy, procedure |
| `date` | date, appointment date, visit date, service date |

## Processing Flow

1. **Upload**: Accept ZIP file or single PDF
2. **Extract**: Extract files to temporary directory
3. **Analyze**: Use Azure Document Intelligence to detect text and layout
4. **Match**: Find form labels that match your fill_map keys
5. **Fill**: Place values to the right of matching labels
6. **Highlight**: Add yellow highlights over matching terms
7. **Render**: Create new PDF with overlays and highlights
8. **Package**: Re-ZIP processed files
9. **Cleanup**: Remove all temporary files

## File Type Support

- **PDF**: Full processing with Azure AI
- **Images** (JPG, PNG, BMP, TIFF): Converted to PDF then processed
- **DOCX**: Stub implementation (TODO: add LibreOffice conversion)
- **Other**: Copied through without processing

## Security Features

- **API Key Authentication**: All requests require valid X-API-KEY header
- **File Size Limits**: Configurable maximum upload size (default: 200MB)
- **Temporary File Cleanup**: All temporary files are automatically deleted
- **No Data Persistence**: No PHI or sensitive data is stored

## Error Handling

The service provides clear error messages for common issues:

- **401 Unauthorized**: Invalid or missing API key
- **400 Bad Request**: Missing required fields or invalid JSON
- **413 Payload Too Large**: File exceeds size limit
- **500 Internal Server Error**: Azure API errors or processing failures

## Testing

### Create Test Files

```python
# Create a sample PDF form
from pdf_utils import create_sample_pdf
create_sample_pdf("test_form.pdf")

# Create a test image
from converters import create_test_image
create_test_image("test_image.png")
```

### Test with Sample Data

```bash
# Test with sample form
curl -X POST http://localhost:5001/process \
  -H "X-API-KEY: change-me-to-something-secure" \
  -F "file=@test_form.pdf" \
  -F 'fill_map={"name":"Test User","dob":"2000-01-01","phone":"555-1234"}' \
  -F 'highlight_terms=["signature","consent"]' \
  --output test_output.pdf
```

## Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `AZURE_DI_ENDPOINT` | Required | Azure Document Intelligence endpoint |
| `AZURE_DI_KEY` | Required | Azure Document Intelligence API key |
| `MAX_CONTENT_LENGTH_MB` | 200 | Maximum upload size in MB |
| `API_SHARED_SECRET` | change-me | API key for authentication |
| `PORT` | 5001 | Port to run the service on |
| `FLASK_DEBUG` | False | Enable Flask debug mode |

## Troubleshooting

### Common Issues

1. **Azure Authentication Error**: Check your endpoint URL and API key in `.env`
2. **File Upload Fails**: Verify file size is under the limit and file is valid
3. **No Form Fields Detected**: Ensure PDF contains recognizable form labels
4. **Highlighting Not Visible**: Check that highlight terms appear in the document text

### Debug Mode

Enable debug mode for detailed error messages:

```bash
export FLASK_DEBUG=true
python app.py
```

## Development

### Adding New Field Types

To add support for new form field types, edit `FIELD_SYNONYMS` in `azure_processor.py`:

```python
FIELD_SYNONYMS = {
    # ... existing fields ...
    'new_field': ['new field', 'new field label', 'alternative name'],
}
```

### Extending File Type Support

To add support for new file types, implement conversion functions in `converters.py`:

```python
def new_format_to_pdf(file_path: str) -> str:
    # Implementation here
    pass
```

## License

This project is part of the UPRS-RPA system.

## Support

For issues and questions, please refer to the main project documentation or create an issue in the repository.
