import requests
import fitz  # PyMuPDF

def download_pdf(url, save_path):
    """Download a PDF file from a given URL and save it to the specified path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"PDF downloaded successfully: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""
    
def get_pdf_link(arxiv_abs_url):
    """Convert an arXiv abstract URL to its corresponding PDF URL."""
    return arxiv_abs_url.replace("abs", "pdf") + ".pdf"