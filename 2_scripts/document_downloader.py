import os
import requests
from urllib.parse import urlparse


# ✅ Allowed folders
VALID_CATEGORIES = {"kubernetes", "docker", "fast_api"}


def get_project_root():
    """Get project root directory"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_raw_docs_path(category: str):
    """Get path to raw_docs/category and ensure it exists"""
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category: {category}. Must be one of {VALID_CATEGORIES}")

    path = os.path.join(get_project_root(), "0_docs", "raw_docs", category)
    os.makedirs(path, exist_ok=True)
    return path


def extract_filename_from_url(url: str) -> str:
    """Extract filename from URL"""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    return filename if filename else "downloaded_file"


# 🆕 NEW: Prevent file overwrite
def get_unique_file_path(file_path: str) -> str:
    """
    If file exists, append (1), (2), etc.
    """
    base, extension = os.path.splitext(file_path)
    counter = 1

    new_path = file_path
    while os.path.exists(new_path):
        new_path = f"{base}({counter}){extension}"
        counter += 1

    return new_path


def detect_category(url: str) -> str:
    """Auto-detect category from URL"""
    url = url.lower()

    if "kubernetes" in url:
        return "kubernetes"
    elif "docker" in url:
        return "docker"
    elif "fastapi" in url or "fast_api" in url:
        return "fast_api"

    raise ValueError(
        "Could not detect category from URL. Please specify manually.")


def download_document(url: str, category: str = None, filename: str = None):
    """
    Download a document into the correct category folder
    """

    # Auto-detect if not provided
    if not category:
        category = detect_category(url)

    save_path = get_raw_docs_path(category)

    if not filename:
        filename = extract_filename_from_url(url)

    file_path = os.path.join(save_path, filename)

    # 🆕 Apply unique naming here
    file_path = get_unique_file_path(file_path)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"✅ Saved to: {file_path}")
        return file_path

    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        return None


# =========================
# ▶️ RUN SCRIPT
# =========================
if __name__ == "__main__":
    url = "https://kubernetes.io/docs/concepts/architecture/#etcd"

    download_document(url, category="kubernetes")
