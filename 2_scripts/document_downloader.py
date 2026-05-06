import os
import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup


# ✅ Allowed folders
VALID_CATEGORIES = {"kubernetes", "docker", "fast_api"}


def get_project_root():
    """Get project root directory"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_raw_docs_path(category: str):
    """Get path to raw_docs/category and ensure it exists"""
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category: {category}. Must be one of {VALID_CATEGORIES}"
        )

    path = os.path.join(get_project_root(), "0_docs", "raw_docs", category)
    os.makedirs(path, exist_ok=True)
    return path


def extract_filename_from_url(url: str) -> str:
    """Fallback: Extract filename from URL"""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    return filename if filename else "downloaded_file"


def sanitize_filename(name: str) -> str:
    """Clean filename for OS compatibility"""
    name = name.strip().lower()
    name = name.replace(" ", "_")

    # Remove invalid characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)

    return name[:150]  # prevent very long filenames


def extract_title_from_html(content: bytes) -> str:
    """Extract title or h1 from HTML"""
    soup = BeautifulSoup(content, "html.parser")

    if soup.find("h1"):
        title = soup.find("h1").get_text()
    elif soup.title:
        title = soup.title.string
    else:
        return "downloaded_file"

    return sanitize_filename(title)


# 🆕 Prevent file overwrite
def get_unique_file_path(file_path: str) -> str:
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
        "Could not detect category from URL. Please specify manually."
    )


def download_document(url: str, category: str = None, filename: str = None):
    """
    Download a document into the correct category folder
    Uses HTML title as filename when possible
    """

    # Auto-detect category
    if not category:
        category = detect_category(url)

    save_path = get_raw_docs_path(category)

    try:
        response = requests.get(url)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        # ✅ Decide filename
        if not filename:
            if "text/html" in content_type:
                filename = extract_title_from_html(response.content) + ".html"
            else:
                filename = extract_filename_from_url(url)

        file_path = os.path.join(save_path, filename)

        # Prevent overwrite
        file_path = get_unique_file_path(file_path)

        # Save file
        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"✅ Saved to: {file_path}")
        return file_path

    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        return None


# =========================
# ▶️ RUN SCRIPT
# =========================
if __name__ == "__main__":
    url = "https://kubernetes.io/docs/concepts/storage/persistent-volumes/"

    download_document(url, category="kubernetes")
