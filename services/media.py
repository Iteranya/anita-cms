# file: services/media.py

import os
import io
import time
from typing import List
from PIL import Image

# Custom exceptions for the service layer
class MediaServiceError(Exception): pass
class InvalidFileNameError(MediaServiceError): pass
class FileNotFoundError(MediaServiceError): pass
class ImageProcessingError(MediaServiceError): pass

class MediaService:
    def __init__(self, media_dir: str = "uploads/media"):
        self.MEDIA_DIR = media_dir
        # Ensure the media directory exists on instantiation
        os.makedirs(self.MEDIA_DIR, exist_ok=True)

    def list_files(self) -> List[dict]:
        """Lists all image files in the media directory."""
        files = os.listdir(self.MEDIA_DIR)
        image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
        
        images = []
        for f in files:
            if f.lower().endswith(image_extensions):
                images.append({"filename": f, "url": f"/media/{f}"})
        return images

    def get_file_path(self, filename: str) -> str:
        """Validates a filename and returns its full path."""
        # Security: Prevent directory traversal attacks
        if '..' in filename or '/' in filename or '\\' in filename:
            raise InvalidFileNameError("Invalid characters in filename.")
        
        file_path = os.path.join(self.MEDIA_DIR, filename)
        if not os.path.isfile(file_path):
            raise FileNotFoundError("File not found.")
            
        return file_path

    def delete_file(self, filename: str):
        """Deletes a file after validating its name and existence."""
        file_path = self.get_file_path(filename) # Reuse validation
        os.remove(file_path)

    def process_and_save_image(self, file_contents: bytes, original_filename: str) -> dict:
        """
        Processes an in-memory image, compresses it, saves the best version,
        and returns a report.
        """
        try:
            image = Image.open(io.BytesIO(file_contents))
            original_format = image.format or 'PNG' # Default if format is not detected

            # Handle transparency (convert RGBA to RGB with a white background)
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGBA')
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            original_name = os.path.splitext(original_filename)[0]
            timestamp = int(time.time())
            
            compressed_files = []
            temp_paths_to_clean = []

            # Strategy 1: Save as JPEG
            jpg_path = os.path.join(self.MEDIA_DIR, f"{original_name}_{timestamp}_temp.jpg")
            image.save(jpg_path, 'JPEG', quality=80, optimize=True)
            compressed_files.append(('jpg', jpg_path, os.path.getsize(jpg_path)))
            temp_paths_to_clean.append(jpg_path)

            # Strategy 2: Save as WebP
            webp_path = os.path.join(self.MEDIA_DIR, f"{original_name}_{timestamp}_temp.webp")
            image.save(webp_path, 'WEBP', quality=80, method=4)
            compressed_files.append(('webp', webp_path, os.path.getsize(webp_path)))
            temp_paths_to_clean.append(webp_path)

            # Determine the best format (smallest file size)
            best_format, best_path, best_size = min(compressed_files, key=lambda x: x[2])
            
            # Rename the best file to its final name
            final_filename = f"{original_name}_{timestamp}.{best_format}"
            final_path = os.path.join(self.MEDIA_DIR, final_filename)
            os.rename(best_path, final_path)
            
            # Clean up all temporary files (including the one that was renamed)
            for path in temp_paths_to_clean:
                if os.path.exists(path):
                    os.remove(path)

            return {
                "original": original_filename, "saved_as": final_filename,
                "url": f"/media/{final_filename}", "size": best_size,
                "format_chosen": best_format
            }
        except Exception as e:
            raise ImageProcessingError(f"Failed to process image: {e}")