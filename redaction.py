import os
import sys
import io

import cv2
from PIL import Image
import pytesseract as ocr
from pdf2image import convert_from_path
import img2pdf

from detectors import detect_all_pii, get_mask_range


def Regex_Search(bounding_boxes, use_ner=True, confidence_threshold=0.85):
    """Reconstruct text from OCR bounding boxes and detect all PII types."""
    text = ""
    for character in range(len(bounding_boxes)):
        if len(bounding_boxes[character]) != 0:
            text += bounding_boxes[character][0]
        else:
            text += "?"

    detections = detect_all_pii(text, use_ner=use_ner, confidence_threshold=confidence_threshold)

    # Convert to array format compatible with masking: [detection_dict, ...]
    # Each detection already has start/end positions mapping to bounding_boxes indices
    return detections


def Mask_UIDs(
    image_path,
    detections,
    bounding_boxes,
    rtype,
    level="standard",
    work_dir=".",
    SR=False,
    SR_Ratio=[1, 1],
):
    """Mask detected PII regions on the image."""
    img = cv2.imread(image_path)

    if rtype == 2:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rtype == 3:
        img = cv2.rotate(img, cv2.ROTATE_180)
    elif rtype == 4:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    height = img.shape[0]

    if SR is True:
        height *= SR_Ratio[1]

    for detection in detections:
        mask_start, mask_end = get_mask_range(detection, level)
        char_start = detection["start"]

        for i in range(mask_start, mask_end):
            box_idx = char_start + i
            if box_idx >= len(bounding_boxes):
                break

            digit = bounding_boxes[box_idx].split()
            if len(digit) < 5:
                continue

            if SR is False:
                top_left_corner = (int(digit[1]), height - int(digit[4]))
                bottom_right_corner = (int(digit[3]), height - int(digit[2]))
            else:
                top_left_corner = (
                    int(int(digit[1]) / SR_Ratio[0]),
                    int((height - int(digit[4])) / SR_Ratio[1]),
                )
                bottom_right_corner = (
                    int(int(digit[3]) / SR_Ratio[0]),
                    int((height - int(digit[2])) / SR_Ratio[1]),
                )

            img = cv2.rectangle(
                img, top_left_corner, bottom_right_corner, (0, 0, 0), -1
            )

    if rtype == 2:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif rtype == 3:
        img = cv2.rotate(img, cv2.ROTATE_180)
    elif rtype == 4:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

    base = os.path.splitext(os.path.basename(image_path))
    file_name = base[0] + "_masked" + base[1]
    output_path = os.path.join(work_dir, file_name)
    cv2.imwrite(output_path, img)
    return output_path


def Extract_and_Mask_UIDs(
    image_path,
    work_dir=".",
    level="standard",
    SR=False,
    sr_image_path=None,
    SR_Ratio=[1, 1],
    use_ner=True,
    confidence_threshold=0.85,
):
    """Try 8 orientations (4 rotations x 2 blur states) to detect and mask PII."""
    if SR is False:
        img = cv2.imread(image_path)
    else:
        img = cv2.imread(sr_image_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    rotations = [
        [gray, 1],
        [cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE), 2],
        [cv2.rotate(gray, cv2.ROTATE_180), 3],
        [cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE), 4],
        [cv2.GaussianBlur(gray, (5, 5), 0), 1],
        [
            cv2.GaussianBlur(
                cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE), (5, 5), 0
            ),
            2,
        ],
        [cv2.GaussianBlur(cv2.rotate(gray, cv2.ROTATE_180), (5, 5), 0), 3],
        [cv2.GaussianBlur(cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE), (5, 5), 0), 4],
    ]

    settings = "-l eng --oem 3 --psm 11"

    for rotation in rotations:
        _, img_encoded = cv2.imencode(".png", rotation[0])
        img_bytes = io.BytesIO(img_encoded)
        image = Image.open(img_bytes)
        bounding_boxes = ocr.image_to_boxes(image, config=settings).split(" 0\n")
        detections = Regex_Search(bounding_boxes, use_ner=use_ner, confidence_threshold=confidence_threshold)

        if len(detections) == 0:
            continue

        if SR is False:
            masked_img = Mask_UIDs(
                image_path, detections, bounding_boxes, rotation[1], level, work_dir
            )
        else:
            masked_img = Mask_UIDs(
                image_path,
                detections,
                bounding_boxes,
                rotation[1],
                level,
                work_dir,
                True,
                SR_Ratio,
            )
        return (masked_img, detections)

    return (None, [])


def _mask_value(detection, level):
    """Return a masked representation of the detected value for stats."""
    value = detection["value"]
    mask_start, mask_end = get_mask_range(detection, level)
    chars = list(value)
    for i in range(mask_start, mask_end):
        chars[i] = "X"
    return "".join(chars)


def redact(input_path, level, work_dir=".", use_ner=True, confidence_threshold=0.85):
    """Main entry point. Processes PDF (all pages) or images.

    Returns (output_path_or_None, stats_dict).
    """
    ext = os.path.splitext(input_path)[1].lower()
    is_pdf = ext == ".pdf"

    stats = {
        "total_detections": 0,
        "by_type": {},
        "pages_processed": 0,
        "detections": [],
    }

    if is_pdf:
        pages = convert_from_path(input_path, 300)
        stats["pages_processed"] = len(pages)
        masked_page_paths = []

        for page_num, page in enumerate(pages, start=1):
            temp_img = os.path.join(work_dir, f"page_{page_num}.jpg")
            page.save(temp_img, "JPEG")
            masked_img, detections = Extract_and_Mask_UIDs(
                temp_img, work_dir, level, use_ner=use_ner, confidence_threshold=confidence_threshold
            )

            if masked_img is not None:
                masked_page_paths.append(masked_img)
                for det in detections:
                    stats["total_detections"] += 1
                    stats["by_type"][det["type"]] = (
                        stats["by_type"].get(det["type"], 0) + 1
                    )
                    stats["detections"].append(
                        {
                            "type": det["type"],
                            "masked_value": _mask_value(det, level),
                            "page": page_num,
                        }
                    )
            else:
                # No detections on this page — keep original
                masked_page_paths.append(temp_img)

        if stats["total_detections"] == 0:
            return (None, stats)

        # Combine all pages into a single PDF
        image_paths = []
        for p in masked_page_paths:
            img = Image.open(p)
            image_paths.append(img.filename)
            img.close()

        pdf_bytes = img2pdf.convert(masked_page_paths)
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_pdf = os.path.join(work_dir, base + "_masked.pdf")
        with open(output_pdf, "wb") as f:
            f.write(pdf_bytes)
        return (output_pdf, stats)

    else:
        # Image file (JPG, JPEG, PNG)
        stats["pages_processed"] = 1
        masked_img, detections = Extract_and_Mask_UIDs(
            input_path, work_dir, level, use_ner=use_ner, confidence_threshold=confidence_threshold
        )

        if masked_img is not None:
            for det in detections:
                stats["total_detections"] += 1
                stats["by_type"][det["type"]] = stats["by_type"].get(det["type"], 0) + 1
                stats["detections"].append(
                    {
                        "type": det["type"],
                        "masked_value": _mask_value(det, level),
                        "page": 1,
                    }
                )

        return (masked_img, stats)


if __name__ == "__main__":
    import tempfile

    work_dir = tempfile.mkdtemp()
    result_path, stats = redact(
        sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "standard", work_dir
    )
    if result_path:
        print("Output:", result_path)
        print("Stats:", stats)
    else:
        print("Can't find any PII!")
