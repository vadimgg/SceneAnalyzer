import os
import re
import tempfile
import sys
from datetime import datetime

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


def is_url(path: str) -> bool:
    """Check if input is a URL."""
    return re.match(r"^https?://", path) is not None


def sanitize_filename(name: str) -> str:
    """Make a filesystem-safe short filename from a title."""
    if not name:
        return "downloaded_video"
    name = re.sub(r"[^\w\s-]", "", name)            # remove weird chars
    name = re.sub(r"\s+", "_", name.strip())        # spaces -> underscores
    return name[:80]


def download_video_from_url(url: str, output_dir: str = None):
    """
    Download the video and return (local_path, sane_title).
    Adds a datetime suffix to ensure unique filenames.
    """
    if yt_dlp is None:
        print("❌ yt-dlp not installed. Run: pip install yt-dlp")
        sys.exit(1)

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="composition_")
    os.makedirs(output_dir, exist_ok=True)

    print(f"⬇️  Downloading video from {url} ...")

    # Use title in outtmpl so file is named after video title where possible
    outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")
    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "mp4/bestvideo+bestaudio/best",
        "quiet": True,
        "merge_output_format": "mp4",
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        # info may include 'title' and 'ext'
        raw_title = info.get("title") or info.get("id") or "downloaded_video"
        sane = sanitize_filename(raw_title)

        # Add a timestamp suffix for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sane_unique = f"{sane}_{timestamp}"

        # Construct expected filename (some extractors add extension differently)
        ext = info.get("ext", "mp4")
        downloaded_file = os.path.join(output_dir, f"{raw_title}.{ext}")

        # If file doesn't exist (yt-dlp renamed it differently), find the actual one
        if not os.path.exists(downloaded_file):
            for f in os.listdir(output_dir):
                if f.lower().endswith((".mp4", ".mov", ".mkv")):
                    downloaded_file = os.path.join(output_dir, f)
                    break

    # Rename the downloaded file to include the unique timestamp
    unique_path = os.path.join(output_dir, f"{sane_unique}.{ext}")
    os.rename(downloaded_file, unique_path)

    print(f"✅ Downloaded: {unique_path}")
    return unique_path, sane_unique

