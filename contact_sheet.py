from PIL import Image, ImageDraw, ImageFont
import os


def create_contact_sheet(scene_data, output_path, thumb_width=320, spacing=20):
    """
    Create a contact sheet from extracted scene frames.
    Each row = 1 scene, 3 frames (start, middle, end).
    """

    if not scene_data:
        print("⚠️ No scene data found. Skipping contact sheet.")
        return

    # Load all images and store with metadata
    all_rows = []
    for scene_num, frames in scene_data:
        images = []
        for frame_file, timestamp in frames:
            if os.path.exists(frame_file):
                img = Image.open(frame_file).convert("RGB")
                w, h = img.size
                aspect = h / w
                new_h = int(thumb_width * aspect)
                img = img.resize((thumb_width, new_h))
                images.append((img, timestamp))
        if images:
            all_rows.append((scene_num, images))

    if not all_rows:
        print("⚠️ No valid frames to display.")
        return

    # Layout
    num_scenes = len(all_rows)
    row_height = max(img.size[1] for _, frames in all_rows for img, _ in frames)
    sheet_width = (thumb_width * 3) + (spacing * 4)
    sheet_height = (row_height + 60) * num_scenes + spacing * 2

    # Create canvas
    sheet = Image.new("RGB", (sheet_width, sheet_height), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)

    # Load font (fallback if not found)
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
    except:
        font = ImageFont.load_default()

    # Paste images
    y = spacing
    for scene_num, frames in all_rows:
        x = spacing
        for img, timestamp in frames:
            sheet.paste(img, (x, y))
            text_y = y + img.size[1] + 5
            draw.text((x, text_y), timestamp, fill=(220, 220, 220), font=font)
            x += thumb_width + spacing
        draw.text(
            (spacing, y - 25),
            f"Scene {scene_num}",
            fill=(255, 255, 255),
            font=font,
        )
        y += row_height + 60

    sheet.save(output_path)
    print(f"✅ Contact sheet saved as: {output_path}")

