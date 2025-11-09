import os
import sys
import shutil
import re
from download_video import is_url, download_video_from_url
from scene_detect import detect_scenes, extract_scene_frames
from contact_sheet import create_contact_sheet


def sanitize_filename(name: str) -> str:
    """Clean up filename to be filesystem-safe."""
    name = re.sub(r"[^\w\s-]", "", name)  # remove non-alphanumeric chars
    name = re.sub(r"\s+", "_", name.strip())  # replace spaces with underscores
    return name[:80]  # keep it short and safe


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <video_path_or_url> [threshold]")
        sys.exit(1)

    input_arg = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0

    # Determine input source (URL or local file)
    if is_url(input_arg):
        print(f"⬇️  Downloading video from {input_arg} ...")
        video_path, title = download_video_from_url(input_arg)
        base_name = sanitize_filename(title)
        downloaded = True
    else:
        if not os.path.exists(input_arg):
            print(f"❌ File not found: {input_arg}")
            sys.exit(1)
        video_path = input_arg
        base_name = sanitize_filename(os.path.splitext(os.path.basename(video_path))[0])
        downloaded = False

    # Output structure
    output_dir = f"{base_name}_scenes"
    sheet_name = f"{base_name}_composition_sheet.jpg"
    sheet_path = os.path.join(os.getcwd(), sheet_name)

    try:
        # 1️⃣ Detect scenes
        scenes = detect_scenes(video_path, threshold)

        # 2️⃣ Extract representative frames
        scene_data = extract_scene_frames(video_path, scenes, output_dir)

        # 3️⃣ Generate composition/contact sheet
        create_contact_sheet(scene_data, sheet_path)
        print(f"✅ Composition sheet saved: {sheet_path}")

    finally:
        # 🧹 Cleanup temporary files
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            print(f"🧹 Deleted scene folder: {output_dir}")

        if downloaded and os.path.exists(video_path):
            os.remove(video_path)
            print(f"🧹 Deleted downloaded video: {video_path}")


if __name__ == "__main__":
    main()

