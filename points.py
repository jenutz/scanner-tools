#!/bin/python3

"""
Interactive tool to select four corner points on an image.
After selection, the image is perspective-transformed into a rectangular,
straightened image based on those points.

BUG: Due to OpenCV behavior, you must press 'q' to close the displayed
straightened image window or proceed to the next image.
Clicking the window close button might proceed to the next image without confirmation.

Usage:
    ./points.py image.jpg
"""

import cv2
import numpy as np
import sys
import math

points = []

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
        points.append((x, y))
        cv2.circle(img, (x, y), img_width // 100, (0, 255, 0), -1)
        cv2.putText(
            img, f"{len(points)}", (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
        )
        cv2.imshow("Select 4 Corners", img)
        if len(points) == 4:
            straighten()


def straighten():
    global points
    TL = min(points, key=lambda e: e[0] + e[1])
    BR = max(points, key=lambda e: e[0] + e[1])
    points.remove(TL)
    points.remove(BR)

    BL = min(points, key=lambda e: e[0])
    TR = max(points, key=lambda e: e[0])
    points.clear()

    pts_src = np.array([TL, TR, BR, BL], dtype="float32")

    width = int(distance(TL, TR))
    height = int(distance(TL, BL))

    pts_dst = np.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32"
    )

    M = cv2.getPerspectiveTransform(pts_src, pts_dst)
    warped = cv2.warpPerspective(orig_img, M, (width, height))

    output_path = f"{img_path.rstrip(".jpg")}_{TL[0]}.jpg"
    cv2.imwrite(output_path, warped)
    print(f"[✔] Saved: {output_path}")

    cv2.namedWindow(f"Straightened Image {TL[0]}", cv2.WINDOW_NORMAL)
    cv2.imshow(f"Straightened Image {TL[0]}", warped)
    key = cv2.waitKey(0)
    cv2.destroyWindow(f"Straightened Image {TL[0]}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python straighten.py image.jpg")
        sys.exit(1)

    for img_path in sys.argv[1:]:

        orig_img = cv2.imread(img_path)
        if orig_img is None:
            print(f"Error: Cannot read image '{img_path}'")
            sys.exit(1)

        img = orig_img.copy()
        img_height, img_width = img.shape[:2]
        img_area = img_width * img_height
        cv2.namedWindow("Select 4 Corners", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Select 4 Corners", 2048, 1080)
        cv2.imshow("Select 4 Corners", img)
        cv2.setMouseCallback("Select 4 Corners", click_event)
        key = cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
