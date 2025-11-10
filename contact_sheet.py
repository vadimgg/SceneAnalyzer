import math
from PIL import Image, ImageDraw, ImageFont


def create_contact_sheet(scene_data, output_path: str,
                         max_width=400, cols=3, padding=40,
                         border=5, bg_color=(20, 18, 14),
                         border_color=(170, 150, 120),
                         font_color=(235, 220, 200),
                         timestamp_color=(200, 190, 175),
                         font_size_title=22,
                         font_size_time=16,
                         font_path="/System/Library/Fonts/Supplemental/Arial.ttf"):
    """
    Create a vintage-style contact sheet with all scenes.
    Each scene has a top label (Scene X - 10s) and 3 frames with timestamps.
    """
    print("🧩 Generating contact sheet...")

    try:
        font_title = ImageFont.truetype(font_path, font_size_title)
        font_time = ImageFont.truetype(font_path, font_size_time)
    except Exception:
        font_title = font_time = ImageFont.load_default()

    # Build list of all frame images with metadata
    all_frames = []
    for scene_num, frames, duration in scene_data:
        for frame_path, timestamp in frames:
            all_frames.append({
                "scene": scene_num,
                "duration": duration,
                "path": frame_path,
                "timestamp": timestamp
            })

    # Load images and resize proportionally
    images = []
    for f in all_frames:
        img = Image.open(f["path"]).convert("RGB")
        w, h = img.size
        scale = max_width / w
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        images.append((img, f["scene"], f["duration"], f["timestamp"]))

    # Layout calculations
    rows = math.ceil(len(images) / cols)
    max_heights = [max(img[0].height for img in images[r * cols:(r + 1) * cols]) for r in range(rows)]
    sheet_w = cols * (max_width + 2 * border) + (cols - 1) * padding
    sheet_h = sum(h + 2 * border + font_size_title + 8 for h in max_heights) + (rows - 1) * padding
    sheet = Image.new("RGB", (sheet_w, sheet_h), bg_color)
    draw = ImageDraw.Draw(sheet)

    y = 0
    for r in range(rows):
        row_imgs = images[r * cols:(r + 1) * cols]
        x = 0
        for img, scene_num, duration, timestamp in row_imgs:
            # Frame border
            framed = Image.new("RGB", (img.width + 2 * border, img.height + 2 * border), border_color)
            framed.paste(img, (border, border))
            offset_x = x
            offset_y = y

            sheet.paste(framed, (offset_x, offset_y))

            # Scene title on top (only once per scene group of 3)
            if timestamp == row_imgs[0][3]:
                title_text = f"Scene {scene_num} – {int(duration)}s"
                tw, th = draw.textbbox((0, 0), title_text, font=font_title)[2:]
                draw.text(
                    (offset_x + (img.width - tw) // 2, offset_y - font_size_title - 8),
                    title_text, fill=font_color, font=font_title
                )

            # Timestamp below each frame
            tw, th = draw.textbbox((0, 0), timestamp, font=font_time)[2:]
            draw.text(
                (offset_x + (img.width - tw) // 2, offset_y + img.height + border + 4),
                timestamp, fill=timestamp_color, font=font_time
            )

            x += max_width + 2 * border + padding
        y += max_heights[r] + 2 * border + font_size_title + 8 + padding

    sheet.save(output_path)
    print(f"🎞️  Saved contact sheet: {output_path}")

