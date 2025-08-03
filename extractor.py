#!/bin/python3

"""
A Python script to detect and extract individual photos from scanned
images by analyzing contours, filtering overlaps, and correcting perspective.
Saves extracted photos to a specified folder.

Usage:
    ./extractor.py input1.jpg input2.jpg -o output_folder -t 200
    ./extractor.py *.jpg -t 200
"""

import cv2
import numpy as np
import math
import os
import argparse
from matplotlib import pyplot as plt
import matplotlib.patches as patches

# Percentage of the image size used to determine the thickness of highlight contours
HIGLIGHT_PERCENT = 1

# Minimum percentage of image area/length for an object to be considered for highlighting
FILTER_TINY_AREA_PERCENT = 1
FILTER_TINY_LEN_PERCENT = 1

# Minimum percentage of image area/length required to avoid filtering out the object
FILTER_SMALL_AREA_PERCENT = 5
FILTER_SMALL_LEN_PERCENT = 5


class PhotoExtractor:
    def __init__(self, threshold_value=200, show=False, debug=False):
        self.threshold_value = threshold_value
        self.show = show
        self.debug = debug

        self.image_path = None
        self.image = None
        self.image_height = None
        self.image_width = None
        self.gray = None
        self.thresh_bgr = None
        self.img_copy = None
        self.photos = []
        self.fig = None

        self.small_area_filter = None
        self.small_len_filter = None
        self.tiny_area_filter = None
        self.tiny_len_filter = None


    @staticmethod
    def distance(p1, p2):
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


    def extract_from_scan(self, image_path, output_folder):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Cannot read image: {image_path}")

        self.image_height, self.image_width = self.image.shape[:2]
        self.image_area = self.image_width * self.image_height

        self.small_area_filter = self.image_area * FILTER_SMALL_AREA_PERCENT / 100
        self.small_len_filter = self.image_height * FILTER_SMALL_LEN_PERCENT / 100
        self.tiny_area_filter = self.image_area * FILTER_TINY_AREA_PERCENT / 100
        self.tiny_len_filter = self.image_height * FILTER_TINY_LEN_PERCENT / 100

        self.img_copy = self.image.copy()
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.gray = cv2.GaussianBlur(self.gray, (25, 25), 0)

        _, thresh = cv2.threshold(self.gray, self.threshold_value, 255, cv2.THRESH_BINARY_INV)
        self.thresh_bgr = cv2.bitwise_not(thresh)
        self.thresh_bgr = cv2.cvtColor(self.thresh_bgr, cv2.COLOR_GRAY2BGR)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea)
        contours = [c for c in contours if cv2.contourArea(c) > self.tiny_area_filter]

        os.makedirs(output_folder, exist_ok=True)

        self.photos = []
        counter = 0
        for i, contour in enumerate(contours):
            warped = self.process_contour(contour)
            if warped is None:
                continue
            output_path = (
                f'{output_folder}/{os.path.basename(image_path).rsplit(".", 1)[0]}_{counter}.jpg'
            )
            cv2.imwrite(output_path, warped)
            self.photos.append(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
            counter += 1

        if (self.show or self.debug) and self.photos:
            self.create_check_image()
            if self.show:
                plt.show()
            elif self.debug:
                debug_dir = os.path.join(output_folder, "debug")
                os.makedirs(debug_dir, exist_ok=True)
                debug_img_path = os.path.join(
                    debug_dir, f"{os.path.basename(image_path).rsplit('.', 1)[0]}_summary.jpg"
                )
                self.fig.savefig(debug_img_path)
                plt.close(self.fig)

        return self.photos


    def process_contour(self, contour):
        rect = cv2.minAreaRect(contour)
        box = np.int32(cv2.boxPoints(rect))
        area = cv2.contourArea(box)

        h = PhotoExtractor.distance(box[0], box[1])
        v = PhotoExtractor.distance(box[0], box[3])
        m = min(h, v)

        if area < self.small_area_filter or m < self.small_len_filter:
            cv2.drawContours(
                self.thresh_bgr,
                [box],
                0,
                (0, 0, 255),
                int(self.image_height * HIGLIGHT_PERCENT / 100),
            )
            return None

        cv2.drawContours(
            self.thresh_bgr, [box], 0, (0, 255, 0), int(self.image_height * HIGLIGHT_PERCENT / 100)
        )

        rect_height = int(rect[1][0])
        rect_width = int(rect[1][1])
        src_pts = box.astype("float32")
        dst_pts = np.array(
            [[0, 0], [rect_width - 1, 0], [rect_width - 1, rect_height - 1], [0, rect_height - 1]],
            dtype="float32",
        )

        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(self.img_copy, M, (rect_width, rect_height))
        return warped


    def create_check_image(self):
        check = [cv2.cvtColor(self.thresh_bgr, cv2.COLOR_BGR2RGB), self.gray]
        n = len(self.photos)
        cols = n
        rows = 2

        self.fig, axs = plt.subplots(rows, cols, figsize=(16, 4 * rows))
        self.fig.suptitle(self.image_path, fontsize=16)

        axs = np.array([[axs[0]], [axs[1]]]) if cols == 1 else np.array(axs).reshape(rows, cols)

        for i in range(min(len(check), cols)):
            rotated = cv2.rotate(check[i], cv2.ROTATE_90_CLOCKWISE)
            axs[0, i].imshow(rotated, cmap="gray" if len(rotated.shape) == 2 else None)
            axs[0, i].set_title(f"Check {i}")
            axs[0, i].axis("off")
        for i in range(len(check), cols):
            axs[0, i].set_visible(False)

        for i in range(n):
            axs[1, i].imshow(self.photos[i])
            axs[1, i].set_title(f"Photo {i}")
            axs[1, i].set_xticks([])
            axs[1, i].set_yticks([])
            axs[1, i].add_patch(
                patches.Rectangle(
                    (0, 0),
                    1,
                    1,
                    linewidth=3,
                    edgecolor="black",
                    facecolor="none",
                    transform=axs[1, i].transAxes,
                    clip_on=False,
                )
            )
        for i in range(n, cols):
            axs[1, i].set_visible(False)

        plt.tight_layout(rect=[0, 0, 1, 0.95])


def main():
    parser = argparse.ArgumentParser(description="Extract photos from scanned image")
    parser.add_argument("input_images", nargs="+", help="Path to the scanned image file")
    parser.add_argument(
        "-o",
        "--output",
        default="extracted_photos",
        help="Output folder for extracted photos",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=200,
        help="Threshold value for binarization (0-255)",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Save debug images instead of showing them",
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Do not show or save debug views",
    )

    args = parser.parse_args()

    show = not args.silent and not args.debug
    debug = args.debug and not args.silent

    os.makedirs(args.output, exist_ok=True)

    extractor = PhotoExtractor(threshold_value=args.threshold, show=show, debug=debug)

    total_photos = 0
    for image_path in args.input_images:
        try:
            photos = extractor.extract_from_scan(image_path, args.output)
            total_photos += len(photos)
            print(f"Extracted {len(photos)} photo(s) from {image_path}")
        except EnvironmentError as e:
            print(f"Error processing {image_path}: {str(e)}")

    print(f"Total extracted photos: {total_photos}")


if __name__ == "__main__":
    main()
