"""
Azure Document Intelligence Processor
Handles Azure AI calls and coordinates form filling and highlighting
"""

import os
import zipfile
import tempfile
import shutil
from typing import Dict, List, Tuple, Any
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from pdf_utils import render_overlays_and_highlights
from converters import convert_to_pdf_if_needed

# Azure configuration
AZURE_ENDPOINT = os.getenv('AZURE_DI_ENDPOINT')
AZURE_KEY = os.getenv('AZURE_DI_KEY')

# Field label synonyms for matching
FIELD_SYNONYMS = {
    'name': ['name', 'patient name', 'full name', 'first name', 'last name', 'patient'],
    'dob': ['dob', 'date of birth', 'birth date', 'birthday'],
    'phone': ['phone', 'telephone', 'tel', 'phone number', 'mobile', 'cell'],
    'address': ['address', 'street address', 'mailing address', 'home address'],
    'email': ['email', 'e-mail', 'email address'],
    'ssn': ['ssn', 'social security', 'social security number'],
    'id': ['id', 'identification', 'patient id', 'account number'],
    'signature': ['signature', 'sign', 'signed by', 'patient signature'],
    'consent': ['consent', 'agreement', 'authorization', 'permission'],
    'emergency': ['emergency', 'emergency contact', 'next of kin'],
    'insurance': ['insurance', 'insurance provider', 'policy number', 'group number'],
    'allergies': ['allergies', 'allergic', 'allergy'],
    'medications': ['medications', 'meds', 'current medications', 'prescriptions'],
    'diagnosis': ['diagnosis', 'condition', 'medical condition'],
    'treatment': ['treatment', 'therapy', 'procedure'],
    'date': ['date', 'appointment date', 'visit date', 'service date']
}

def normalize_text(text: str) -> str:
    """Normalize text for comparison by removing punctuation and converting to lowercase"""
    import re
    # Remove punctuation and extra whitespace
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Collapse multiple whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def find_matching_labels(analysis: Dict[str, Any], fill_map: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Find labels in the document that match the fill_map keys
    
    Returns:
    List of dicts with page, x, y, text, and matched_key
    """
    overlays = []
    
    # Process paragraphs and lines from Azure analysis
    for page_num, page in enumerate(analysis.get('pages', []), 1):
        # Check paragraphs
        for paragraph in page.get('paragraphs', []):
            text = paragraph.get('content', '')
            normalized_text = normalize_text(text)
            
            # Check for matches in fill_map
            for key, value in fill_map.items():
                if key in FIELD_SYNONYMS:
                    synonyms = FIELD_SYNONYMS[key]
                    if any(synonym in normalized_text for synonym in synonyms):
                        # Get bounding region for positioning
                        if paragraph.get('boundingRegions'):
                            region = paragraph['boundingRegions'][0]
                            polygon = region.get('polygon', [])
                            if len(polygon) >= 4:  # Need at least 2 points (x,y pairs)
                                # Use top-right corner for positioning
                                x = max(polygon[0::2])  # Max X coordinate
                                y = max(polygon[1::2])  # Max Y coordinate
                                
                                overlays.append({
                                    'page': page_num,
                                    'x': x + 10,  # Offset 10 points to the right
                                    'y': y,
                                    'text': value,
                                    'matched_key': key
                                })
        
        # Also check lines for more granular matching
        for line in page.get('lines', []):
            text = line.get('content', '')
            normalized_text = normalize_text(text)
            
            for key, value in fill_map.items():
                if key in FIELD_SYNONYMS:
                    synonyms = FIELD_SYNONYMS[key]
                    if any(synonym in normalized_text for synonym in synonyms):
                        if line.get('boundingRegions'):
                            region = line['boundingRegions'][0]
                            polygon = region.get('polygon', [])
                            if len(polygon) >= 4:
                                x = max(polygon[0::2])
                                y = max(polygon[1::2])
                                
                                overlays.append({
                                    'page': page_num,
                                    'x': x + 10,
                                    'y': y,
                                    'text': value,
                                    'matched_key': key
                                })
    
    return overlays

def find_highlight_regions(analysis: Dict[str, Any], highlight_terms: List[str]) -> List[Dict[str, Any]]:
    """
    Find regions in the document that contain highlight terms
    
    Returns:
    List of dicts with page and polygon coordinates
    """
    highlights = []
    
    for page_num, page in enumerate(analysis.get('pages', []), 1):
        # Check paragraphs
        for paragraph in page.get('paragraphs', []):
            text = paragraph.get('content', '')
            normalized_text = normalize_text(text)
            
            for term in highlight_terms:
                if normalize_text(term) in normalized_text:
                    if paragraph.get('boundingRegions'):
                        region = paragraph['boundingRegions'][0]
                        polygon = region.get('polygon', [])
                        if len(polygon) >= 4:
                            highlights.append({
                                'page': page_num,
                                'polygon': polygon
                            })
        
        # Check lines
        for line in page.get('lines', []):
            text = line.get('content', '')
            normalized_text = normalize_text(text)
            
            for term in highlight_terms:
                if normalize_text(term) in normalized_text:
                    if line.get('boundingRegions'):
                        region = line['boundingRegions'][0]
                        polygon = region.get('polygon', [])
                        if len(polygon) >= 4:
                            highlights.append({
                                'page': page_num,
                                'polygon': polygon
                            })
    
    return highlights

def analyze_with_azure(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Analyze PDF using Azure Document Intelligence prebuilt-layout model
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        Analysis result from Azure
    """
    if not AZURE_ENDPOINT or not AZURE_KEY:
        raise ValueError("Azure credentials not configured. Set AZURE_DI_ENDPOINT and AZURE_DI_KEY")
    
    client = DocumentIntelligenceClient(
        endpoint=AZURE_ENDPOINT, 
        credential=AzureKeyCredential(AZURE_KEY)
    )
    
    # Use prebuilt-layout model
    poller = client.begin_analyze_document(
        "prebuilt-layout", 
        document=pdf_bytes
    )
    
    result = poller.result()
    return result.to_dict()

def process_zip_with_azure(
    zip_path: str, 
    fill_map: Dict[str, str], 
    highlight_terms: List[str],
    input_dir: str = None,
    output_dir: str = None
) -> str:
    """
    Process all PDF files in a ZIP with Azure Document Intelligence
    
    Args:
        zip_path: Path to input ZIP file
        fill_map: Dictionary mapping field labels to values
        highlight_terms: List of terms to highlight
        input_dir: Directory containing extracted files (optional)
        output_dir: Directory for processed files (optional)
        
    Returns:
        Path to output ZIP file
    """
    # Create temporary directories if not provided
    temp_input = input_dir is None
    temp_output = output_dir is None
    
    if temp_input:
        input_dir = tempfile.mkdtemp()
    if temp_output:
        output_dir = tempfile.mkdtemp()
    
    try:
        # Extract ZIP if input_dir is empty
        if not os.listdir(input_dir):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(input_dir)
        
        # Process each file
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                input_path = os.path.join(root, file)
                
                # Calculate relative path for output
                rel_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, rel_path)
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Process based on file type
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext == '.pdf':
                    # Process PDF with Azure
                    process_pdf_with_azure(input_path, output_path, fill_map, highlight_terms)
                else:
                    # Convert other file types to PDF if possible
                    try:
                        converted_pdf = convert_to_pdf_if_needed(input_path)
                        if converted_pdf:
                            process_pdf_with_azure(converted_pdf, output_path, fill_map, highlight_terms)
                            # Clean up temporary converted file
                            os.remove(converted_pdf)
                        else:
                            # Copy through if conversion not supported
                            shutil.copy2(input_path, output_path)
                    except Exception as e:
                        print(f"Warning: Could not process {file}: {e}")
                        # Copy through on error
                        shutil.copy2(input_path, output_path)
        
        # Create output ZIP
        output_zip_path = os.path.join(output_dir, '..', 'processed.zip')
        output_zip_path = os.path.abspath(output_zip_path)
        
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zip_ref.write(file_path, arcname)
        
        return output_zip_path
    
    finally:
        # Clean up temporary directories
        if temp_input and os.path.exists(input_dir):
            shutil.rmtree(input_dir)
        if temp_output and os.path.exists(output_dir):
            shutil.rmtree(output_dir)

def process_pdf_with_azure(
    input_pdf_path: str, 
    output_pdf_path: str, 
    fill_map: Dict[str, str], 
    highlight_terms: List[str]
):
    """
    Process a single PDF file with Azure Document Intelligence
    
    Args:
        input_pdf_path: Path to input PDF
        output_pdf_path: Path for output PDF
        fill_map: Dictionary mapping field labels to values
        highlight_terms: List of terms to highlight
    """
    # Read PDF file
    with open(input_pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Analyze with Azure
    analysis = analyze_with_azure(pdf_bytes)
    
    # Find matching labels for form filling
    overlays = find_matching_labels(analysis, fill_map)
    
    # Find regions to highlight
    highlights = find_highlight_regions(analysis, highlight_terms)
    
    # Render overlays and highlights
    render_overlays_and_highlights(input_pdf_path, output_pdf_path, overlays, highlights)
