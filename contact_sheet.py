import math
from PIL import Image, ImageDraw, ImageFont


def create_contact_sheet(scene_data, output_path: str,
                         max_width=400, cols=5, padding=6,
                         border=3, bg_color=(15, 15, 15),
                         border_color=(230, 230, 230),
                         font_color=(240, 240, 240),
                         font_size=18,
                         font_path="/System/Library/Fonts/Supplemental/Arial.ttf"):
    """Create a contact sheet from scene images."""
    print("🧩 Generating contact sheet...")

    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()

    images = []
    for s in scene_data:
        img = Image.open(s["image"]).convert("RGB")
        w, h = img.size
        scale = max_width / w
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        label = f"Scene {s['num']} – {s['start']} – {s['duration']}s"
        images.append((img, label))

    rows = math.ceil(len(images) / cols)
    max_heights = [max(img[0].height for img in images[r * cols:(r + 1) * cols]) for r in range(rows)]

    sheet_w = cols * (max_width + 2 * border) + (cols - 1) * padding
    sheet_h = sum(h + 2 * border + font_size + 8 for h in max_heights) + (rows - 1) * padding
    sheet = Image.new("RGB", (sheet_w, sheet_h), bg_color)
    draw = ImageDraw.Draw(sheet)

    y = 0
    for r in range(rows):
        row_imgs = images[r * cols:(r + 1) * cols]
        x = 0
        for img, label_text in row_imgs:
            framed = Image.new("RGB", (img.width + 2 * border, img.height + 2 * border), border_color)
            framed.paste(img, (border, border))
            offset_x = x + (max_width - img.width) // 2
            offset_y = y + (max_heights[r] - img.height) // 2
            sheet.paste(framed, (offset_x, offset_y))

            try:
                bbox = draw.textbbox((0, 0), label_text, font=font)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            except AttributeError:
                tw, th = font.getsize(label_text)

            label_y = offset_y + img.height + border + 4
            draw.text(
                (offset_x + (img.width + 2 * border - tw) // 2, label_y),
                label_text, fill=font_color, font=font
            )
            x += max_width + 2 * border + padding
        y += max_heights[r] + 2 * border + font_size + 8 + padding

    sheet.save(output_path)
    print(f"🎞️  Saved contact sheet: {output_path}")

