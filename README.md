# Photo Scan Tools

A set of utilities to streamline the process of scanning, straightening, splitting, and extracting individual photos from multi-photo scan images.

---

## Features

- **Auto Extractor** – Automatically detects and extracts individual photos from a scanned image using contour detection and perspective correction.
- **Manual Straightener** – GUI tool to manually select 4 corners and straighten distorted scans.
- **Vertical Splitter** – Interactive tool to split images vertically with a movable line.
- **Scan GUI** – PyQt interface for controlling `hp-scan` with DPI selection and optional media pause.

---

## Usage

### `extractor.py`
Automatically detects and saves individual photos from input images.

```bash
./extractor.py *.jpg -o output_folder -t 200
```

---

### `points.py`
Manually straighten images by clicking 4 corners.

```bash
./points.py image.jpg
```

Note: You must press `q` to close the image viewer and proceed. Clicking the close button might skip ahead without confirmation.

---

### `split.py`
Split scanned images in half using a vertical line.

```bash
./split.py image1.jpg image2.jpg
```

- Arrow keys or buttons to move the split.
- Click to place line.
- Press `Enter`, `S`, or click `save`.

---

### `scan.py`
PyQt GUI for `hp-scan` with DPI selection. Optionally pauses media using `playerctl`.

```bash
./scan.py
```

---

## Requirements

- Python 3
- PyQt5
- OpenCV (`opencv-python`)
- `hp-scan` (via HPLIP)
- `playerctl` (optional)

