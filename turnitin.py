"""
PDF Header & Footer Overlay Tool
---------------------------------
Stamps an identical header and footer onto every page of an existing PDF
without modifying the original content.

Layout (same for header and footer):
  LEFT:  [Image 1392x417] <gap> Page X of Y - Left Label
  RIGHT: Right Label

Usage:
    python add_header_footer.py input.pdf output.pdf \
        --image logo.png \
        --left-label "Document Name" \
        --right-label "Confidential"
"""

import argparse
import io
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter


# ── Band height in PDF points (1 pt = 1/72 inch). Adjust to taste. ──
BAND_H = 48

# ── Horizontal padding from page edges ──
PADDING = 25

# ── Gap between image and the page-number text ──
IMG_TEXT_GAP = 10

# ── Image scale factor (1.0 = original size) ──
IMG_SCALE = 0.3

# ── Center position for left-side image+text group (x coordinate) ──
LEFT_CENTER_X = 140

# ── Image vertical padding (top for header, bottom for footer) ──
IMG_TOP_PADDING = -10
IMG_BOTTOM_PADDING = 8

# ── Image native aspect ratio (1392 × 417) ──
IMG_ASPECT = 1392 / 417


def draw_band(c, band_y, width, page_num, total_pages, config):
    """
    Draws one header/footer band.
    band_y = bottom-left Y coordinate of the band rectangle.
    """

    # ── Optional background ──────────────────────────────────────────
    bg = config.get("bg_color")
    if bg:
        c.setFillColor(HexColor(bg))
        c.rect(0, band_y, width, BAND_H, fill=1, stroke=0)

    # ── Image (left side) ────────────────────────────────────────────
    img_w = 0
    img_h = 0
    img_path = config.get("image", "")
    if img_path and Path(img_path).exists():
        try:
            img = ImageReader(img_path)
            # Use top padding for header (band_y > 0), bottom padding for footer (band_y == 0)
            if band_y > 0:
                img_h = BAND_H * IMG_SCALE
                img_y = band_y + IMG_TOP_PADDING
            else:
                img_h = BAND_H * IMG_SCALE
                img_y = band_y + IMG_BOTTOM_PADDING
            img_w = img_h * IMG_ASPECT
        except Exception as e:
            print(f"  [warn] Could not draw image: {e}")

    # ── "Page X of Y – Left Label" (after the image) ─────────────────
    text_x = PADDING + img_w + IMG_TEXT_GAP
    text_y = band_y + BAND_H / 2 - 5  # vertically centred

    left_label = config.get("left_label", "")
    page_text = f"Page {page_num + 1} of {total_pages}"
    if left_label:
        page_text += f"  -  {left_label}"

    c.setFillColor(HexColor(config.get("text_color", "#000000")))
    c.setFont(config.get("font", "Helvetica"), config.get("font_size", 9))
    text_w = c.stringWidth(
        page_text, config.get("font", "Helvetica"), config.get("font_size", 9)
    )

    # ── Center image+text group at LEFT_CENTER_X ─────────────────────
    total_w = img_w + IMG_TEXT_GAP + text_w
    group_start_x = LEFT_CENTER_X - total_w / 2

    # Draw image at start of group
    if img_w > 0 and img_h > 0 and img_path and Path(img_path).exists():
        img_x = group_start_x
        c.drawImage(
            img,
            img_x,
            img_y,
            width=img_w,
            height=img_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Draw text after image
    text_x = group_start_x + img_w + IMG_TEXT_GAP
    text_y = band_y + BAND_H / 2 - 5  # vertically centred
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

        # Header band — anchored to top
        draw_band(c, h - BAND_H, w, i + 1, total, config)

        # Footer band — anchored to bottom
        draw_band(c, 0, w, i + 1, total, config)

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
        "font_size": args.font_size,
    }

    stamp_pdf(args.input, args.output, config)


if __name__ == "__main__":
    main()
