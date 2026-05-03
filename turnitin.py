import argparse
import io
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ── Band height in PDF points (1 pt = 1/72 inch). Adjust to taste. ──
BAND_H = 48

# ── Horizontal padding from page edges ──
PADDING = 25

# ── Gap between image and the page-number text ──
IMG_TEXT_GAP = 14

# ── Image scale factor (1.0 = original size) ──
IMG_SCALE = 0.35

# ── Center position for left-side image+text group (x coordinate) ──
LEFT_CENTER_X = 110

# ── Image vertical padding from the INNER edge of each band:
#    IMG_TOP_PADDING    = distance (pts) from top of header band → top of image
#    IMG_BOTTOM_PADDING = distance (pts) from bottom of footer band → bottom of image
IMG_TOP_PADDING = 16
IMG_BOTTOM_PADDING = 2

# ── Vertical padding from page edges ──
TOP_PAGE_PADDING = 10  # space from top edge → header band
BOTTOM_PAGE_PADDING = 14  # space from bottom edge → footer band

# ── Custom TTF font path ──
FONT_PATH = "/home/funinkina/Downloads/Noto_Sans/NotoSans-VariableFont_wdth,wght.ttf"  # e.g. "./fonts/Inter-Regular.ttf"
FONT_NAME = "CustomFont"

# ── Image native aspect ratio (1392 × 417) ──
IMG_ASPECT = 1392 / 417


def draw_band(c, band_y, width, page_num, total_pages, config):
    """
    Draws one header/footer band.
    band_y = bottom-left Y coordinate of the band rectangle.
    is_header = band_y > 0
    """
    is_header = band_y > 0

    # ── Optional background ──────────────────────────────────────────
    bg = config.get("bg_color")
    if bg:
        c.setFillColor(HexColor(bg))
        c.rect(0, band_y, width, BAND_H, fill=1, stroke=0)

    # ── Image geometry ────────────────────────────────────────────────
    img_w = 0
    img_h = 0
    img_y = band_y  # fallback; overwritten below
    img_reader = None

    img_path = config.get("image", "")
    if img_path and Path(img_path).exists():
        try:
            img_reader = ImageReader(img_path)
            img_h = BAND_H * IMG_SCALE
            img_w = img_h * IMG_ASPECT

            if is_header:
                # Anchor to TOP of band, then step down by IMG_TOP_PADDING
                band_top = band_y + BAND_H
                img_y = band_top - IMG_TOP_PADDING - img_h
            else:
                # Anchor to BOTTOM of band, then step up by IMG_BOTTOM_PADDING
                img_y = band_y + IMG_BOTTOM_PADDING

        except Exception as e:
            print(f"  [warn] Could not load image: {e}")

    # ── "Page X of Y – Left Label" ────────────────────────────────────
    left_label = config.get("left_label", "")
    page_text = f"Page {page_num + 2} of {total_pages + 2}"
    if left_label:
        page_text += f" - {left_label}"

    font = config.get("font", "Noto Sans")
    font_size = config.get("font_size", 9)
    text_w = c.stringWidth(page_text, font, font_size)
    text_y = band_y + BAND_H / 2 - font_size / 2  # vertically centred in band

    # ── Centre image+text group at LEFT_CENTER_X ─────────────────────
    total_group_w = img_w + (IMG_TEXT_GAP if img_w else 0) + text_w
    group_start_x = LEFT_CENTER_X - total_group_w / 2

    # Draw image
    if img_reader is not None and img_w > 0:
        c.drawImage(
            img_reader,
            group_start_x,
            img_y,
            width=img_w,
            height=img_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Draw page text
    c.setFillColor(HexColor(config.get("text_color", "#141414")))
    c.setFont(font, font_size)
    text_x = group_start_x + img_w + (IMG_TEXT_GAP if img_w else 0)
    c.drawString(text_x, text_y, page_text)

    # ── Right label ───────────────────────────────────────────────────
    right_label = config.get("right_label", "")
    if right_label:
        c.drawRightString(width - PADDING, text_y, right_label)


# ─────────────────────────────────────────────────────────────────────
#  CORE ENGINE
# ─────────────────────────────────────────────────────────────────────
def build_overlay_pdf(page_sizes, config):
    buf = io.BytesIO()
    total = len(page_sizes)
    c = canvas.Canvas(buf)

    for i, (w, h) in enumerate(page_sizes):
        c.setPageSize((w, h))
        # Header shifted down by TOP_PAGE_PADDING
        draw_band(c, h - BAND_H - TOP_PAGE_PADDING, w, i + 1, total, config)

        # Footer shifted up by BOTTOM_PAGE_PADDING
        draw_band(c, BOTTOM_PAGE_PADDING, w, i + 1, total, config)
        c.showPage()

    c.save()
    buf.seek(0)
    return buf


def stamp_pdf(input_path, output_path, config):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    page_sizes = [
        (float(p.mediabox.width), float(p.mediabox.height)) for p in reader.pages
    ]

    overlay_reader = PdfReader(build_overlay_pdf(page_sizes, config))

    for i, page in enumerate(reader.pages):
        page.merge_page(overlay_reader.pages[i])
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Saved -> {output_path}  ({len(reader.pages)} pages stamped)")


# ─────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────
def main():
    if FONT_PATH and Path(FONT_PATH).exists():
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
    else:
        print(f"[warn] Font not found at {FONT_PATH}, falling back to Helvetica")

    parser = argparse.ArgumentParser(
        description="Stamp identical header & footer bands onto every PDF page"
    )
    parser.add_argument("input", help="Input PDF path")
    parser.add_argument("output", help="Output PDF path")
    parser.add_argument(
        "--image", default="", help="Path to image (1392x417 or any aspect ratio)"
    )
    parser.add_argument("--left-label", default="", help="Text after 'Page X of Y  -'")
    parser.add_argument("--right-label", default="", help="Right-aligned label")
    parser.add_argument(
        "--bg-color", default="", help="Band background hex color, e.g. #f5f5f5"
    )
    parser.add_argument(
        "--border-color", default="#cccccc", help="Inner border line color"
    )
    parser.add_argument("--text-color", default="#000000", help="Text color hex")
    parser.add_argument("--font-size", default=6, type=int, help="Font size in points")
    args = parser.parse_args()

    config = {
        "image": args.image,
        "left_label": args.left_label,
        "right_label": args.right_label,
        "bg_color": args.bg_color,
        "border_color": args.border_color,
        "text_color": args.text_color,
        "font": FONT_NAME if FONT_PATH and Path(FONT_PATH).exists() else "Helvetica",
        "font_size": args.font_size,
    }

    stamp_pdf(args.input, args.output, config)


if __name__ == "__main__":
    main()
