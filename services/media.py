import os
import io
import time
import logging
from typing import List, Set
from PIL import Image
import requests 


#TODO: Swap Pillow with pyvips also, cherry pick the branch with the one where I keep invisibility in images


# Custom exceptions for the service layer
class MediaServiceError(Exception): 
    pass
class InvalidFileNameError(MediaServiceError): 
    pass
class FileNotFoundError(MediaServiceError): 
    pass
class ImageProcessingError(MediaServiceError): 
    pass
class CopypartyError(MediaServiceError): 
    pass

# Logger configuration
logger = logging.getLogger("MediaService")

class CopypartyClient:
    """Helper class to handle interactions with Copyparty."""
    def __init__(self, base_url: str, password: str = None):
        self.base_url = base_url.rstrip('/')
        self.password = password
        self.session = requests.Session()
        if self.password:
            # Copyparty accepts password in the 'pw' query param or header
            self.session.headers.update({"pw": self.password})

    def upload(self, local_path: str, filename: str):
        """Uploads a file using HTTP PUT."""
        url = f"{self.base_url}/{filename}"
        with open(local_path, 'rb') as f:
            # Copyparty accepts simple PUT uploads
            resp = self.session.put(url, data=f)
            resp.raise_for_status()

    def delete(self, filename: str):
        """Deletes a file using HTTP DELETE (WebDAV style)."""
        url = f"{self.base_url}/{filename}"
        resp = self.session.delete(url)
        # 404 is fine, means it's already gone
        if resp.status_code != 404:
            resp.raise_for_status()

    def list_files(self) -> Set[str]:
        """
        Fetches a plaintext listing from Copyparty to determine existing files.
        Uses the ?ls=t (plaintext) feature documented in Copyparty.
        """
        try:
            url = f"{self.base_url}/?ls=t"
            resp = self.session.get(url)
            resp.raise_for_status()
            lines = resp.text.strip().split('\n')
            files = {line.strip() for line in lines if line.strip()}
            return files
        except Exception as e:
            logger.error(f"Failed to list Copyparty files: {e}")
            return set()

class MediaService:
    def __init__(self, media_dir: str = "uploads/media"):
        self.MEDIA_DIR = media_dir
        os.makedirs(self.MEDIA_DIR, exist_ok=True)

        # --- Copyparty Configuration ---
        self.cp_url = os.getenv("COPYPARTY_URL")
        self.cp_pass = os.getenv("COPYPARTY_PASSWORD")
        self.copyparty = None

        if self.cp_url:
            try:
                self.copyparty = CopypartyClient(self.cp_url, self.cp_pass)
                logger.info(f"Copyparty integration enabled at {self.cp_url}")
            except Exception as e:
                logger.error(f"Failed to initialize Copyparty: {e}")

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
        if '..' in filename or '/' in filename or '\\' in filename:
            raise InvalidFileNameError("Invalid characters in filename.")
        
        file_path = os.path.join(self.MEDIA_DIR, filename)
        if not os.path.isfile(file_path):
            raise FileNotFoundError("File not found.")
            
        return file_path

    def delete_file(self, filename: str):
        """Deletes a file locally and optionally from Copyparty."""
        file_path = self.get_file_path(filename)
        os.remove(file_path)

        # --- Copyparty Hook ---
        if self.copyparty:
            try:
                self.copyparty.delete(filename)
            except Exception as e:
                # Log error but don't stop the local deletion success
                logger.error(f"Failed to delete {filename} from Copyparty: {e}")

    def process_and_save_image(self, file_contents: bytes, original_filename: str) -> dict:
        """Processes, compresses, saves locally, and uploads to Copyparty."""
        try:
            image = Image.open(io.BytesIO(file_contents))
            # ... (Existing Image Processing Logic) ...
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

            # Save as JPEG
            jpg_path = os.path.join(self.MEDIA_DIR, f"{original_name}_{timestamp}_temp.jpg")
            image.save(jpg_path, 'JPEG', quality=80, optimize=True)
            compressed_files.append(('jpg', jpg_path, os.path.getsize(jpg_path)))
            temp_paths_to_clean.append(jpg_path)

            # Save as WebP
            webp_path = os.path.join(self.MEDIA_DIR, f"{original_name}_{timestamp}_temp.webp")
            image.save(webp_path, 'WEBP', quality=80, method=4)
            compressed_files.append(('webp', webp_path, os.path.getsize(webp_path)))
            temp_paths_to_clean.append(webp_path)

            best_format, best_path, best_size = min(compressed_files, key=lambda x: x[2])
            
            final_filename = f"{original_name}_{timestamp}.{best_format}"
            final_path = os.path.join(self.MEDIA_DIR, final_filename)
            os.rename(best_path, final_path)
            
            # Clean up
            for path in temp_paths_to_clean:
                if os.path.exists(path):
                    os.remove(path)

            # --- Copyparty Hook ---
            upload_status = "skipped"
            if self.copyparty:
                try:
                    self.copyparty.upload(final_path, final_filename)
                    upload_status = "uploaded"
                except Exception as e:
                    logger.error(f"Failed to upload {final_filename} to Copyparty: {e}")
                    upload_status = f"failed: {str(e)}"

            return {
                "original": original_filename, "saved_as": final_filename,
                "url": f"/media/{final_filename}", "size": best_size,
                "format_chosen": best_format, "copyparty_status": upload_status
            }
        except Exception as e:
            raise ImageProcessingError(f"Failed to process image: {e}")

    def sync_to_copyparty(self) -> dict:
        """
        Syncs local files to Copyparty (One-way Sync: Local -> Remote).
        Does not delete files on remote that are missing locally.
        """
        if not self.copyparty:
            raise CopypartyError("Copyparty is not configured.")

        local_files = self.list_files() # Returns list of dicts
        local_filenames = {f['filename'] for f in local_files}
        
        # Get list of files already on server
        remote_filenames = self.copyparty.list_files()

        # Determine what needs uploading
        to_upload = local_filenames - remote_filenames
        
        uploaded = []
        errors = []

        for filename in to_upload:
            try:
                local_path = os.path.join(self.MEDIA_DIR, filename)
                self.copyparty.upload(local_path, filename)
                uploaded.append(filename)
            except Exception as e:
                errors.append({"filename": filename, "error": str(e)})

        return {
            "status": "completed",
            "files_checked": len(local_filenames),
            "files_uploaded": len(uploaded),
            "uploaded_list": uploaded,
            "errors": errors
        }