import requests
import tempfile
import os
from PIL import Image
import io
from urllib.parse import urlparse

def normalize_url(url):
    """Ensure URL has proper scheme and format"""
    if url.startswith('//'):
        return f'https:{url}'
    elif url.startswith('gs://'):
        return url
    elif not url.startswith(('http://', 'https://')):
        return f'https://{url}'
    return url

def download_image(url, bucket=None):
    """Download image from URL to a temporary file with robust error handling"""
    try:
        url = normalize_url(url)
        
        # Handle Firebase Storage URLs
        if url.startswith('gs://') and bucket:
            path = url[len('gs://' + url.split('/')[2] + 1):]
            blob = bucket.blob(path)
            img_data = blob.download_as_bytes()
        else:
            # Handle regular HTTP URLs
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()
            img_data = response.content
        
        # Create a temporary file with appropriate extension
        img = Image.open(io.BytesIO(img_data))
        
        # Convert to RGB if needed (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
            
        # Determine appropriate file extension
        ext = 'jpg'
        if url.lower().endswith(('.png', '.webp')):
            ext = url.split('.')[-1].lower().split('?')[0]
            
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}')
        img.save(temp_file, format=ext.upper() if ext != 'jpg' else 'JPEG')
        temp_file.close()
        return temp_file.name
    
    except Exception as e:
        print(f"Error downloading image {url}: {str(e)}")
        return None
