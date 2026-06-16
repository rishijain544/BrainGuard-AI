"""
Download model files from GitHub LFS at build time or startup.
This solves the problem where Docker COPY only copies LFS pointer files.
"""
import os
import sys
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GitHub repo info
REPO = "rishijain544/BrainGuard-AI"
BRANCH = "main"

# Model files to download (path in repo -> local path)
MODEL_FILES = {
    "backend/models/cnn_best.pth": "models/cnn_best.pth",
    "backend/models/resnet_best.pth": "models/resnet_best.pth",
    "backend/models/vit_best.pth": "models/vit_best.pth",
    "backend/models/segmentation_model.pth": "models/segmentation_model.pth",
}

# Minimum file size to consider valid (LFS pointers are ~130 bytes)
MIN_VALID_SIZE = 10000  # 10 KB


def is_lfs_pointer(filepath):
    """Check if a file is a Git LFS pointer (small text file) rather than actual data."""
    if not os.path.exists(filepath):
        return True  # Missing = needs download
    size = os.path.getsize(filepath)
    if size < MIN_VALID_SIZE:
        # Read first bytes to confirm it's a pointer
        with open(filepath, 'rb') as f:
            header = f.read(100)
        if b'version https://git-lfs' in header:
            return True
    return False


def download_from_github(repo_path, local_path):
    """Download a file from GitHub (handles LFS redirect automatically)."""
    url = f"https://github.com/{REPO}/raw/{BRANCH}/{repo_path}"
    logger.info(f"  Downloading from: {url}")
    logger.info(f"  Saving to: {local_path}")
    
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'BrainGuard-AI-Downloader/1.0')
    
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            
            with open(local_path, 'wb') as f:
                while True:
                    chunk = response.read(8192 * 16)  # 128KB chunks
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = (downloaded / total_size) * 100
                        print(f"\r  Progress: {downloaded/(1024*1024):.1f} MB / {total_size/(1024*1024):.1f} MB ({pct:.0f}%)", end='', flush=True)
            
            print()  # newline after progress
            
            final_size = os.path.getsize(local_path)
            logger.info(f"  Downloaded: {final_size/(1024*1024):.1f} MB")
            
            if final_size < MIN_VALID_SIZE:
                logger.error(f"  File too small ({final_size} bytes) - download may have failed!")
                return False
                
            return True
    except Exception as e:
        logger.error(f"  Download failed: {e}")
        return False


def ensure_models():
    """Ensure all model files are present and not just LFS pointers."""
    logger.info("=" * 60)
    logger.info("BrainGuard AI - Model File Checker")
    logger.info("=" * 60)
    
    all_ok = True
    
    for repo_path, local_path in MODEL_FILES.items():
        logger.info(f"\nChecking: {local_path}")
        
        if os.path.exists(local_path) and not is_lfs_pointer(local_path):
            size_mb = os.path.getsize(local_path) / (1024 * 1024)
            logger.info(f"  OK - {size_mb:.1f} MB (actual model data)")
            continue
        
        if is_lfs_pointer(local_path):
            logger.warning(f"  File is a Git LFS pointer or missing - downloading actual model...")
        
        success = download_from_github(repo_path, local_path)
        if not success:
            logger.error(f"  FAILED to download {local_path}")
            all_ok = False
    
    logger.info("\n" + "=" * 60)
    if all_ok:
        logger.info("All models are ready!")
    else:
        logger.error("Some models failed to download!")
    logger.info("=" * 60)
    
    return all_ok


if __name__ == "__main__":
    success = ensure_models()
    sys.exit(0 if success else 1)
