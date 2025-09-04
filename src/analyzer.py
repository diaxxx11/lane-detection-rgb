from src import config
import cv2
import numpy as np


def decide_tags(classif, width, height, frame=None):
    """
    GOOD if:
      - >= 2 dashed middle segments detected
      - left outer line near left edge AND right outer line near right edge
      - dashed middle lies between them
      - bottom intercepts are inside the accepted vertical band
    Lane side:
      - If dashed middle is closer to the right half -> robot is in LEFT lane
      - If dashed middle is closer to the left half -> robot is in RIGHT lane
    """

    mid_x = classif.get("middle_avg_x", None)
    dash_ok = (classif.get("middle_dash_count", 0) >= 2) and (mid_x is not None)
    if not dash_ok:
        return False, "unknown"

    # --- Gather bottom intercepts above bottom band ---
    min_y = int(height * (1.0 - config.BOTTOM_ACCEPT_BAND))
    left_bxs = [
        bx for (bx, by) in classif.get("left_bottom_pts", [])
        if bx is not None and by < height and by >= min_y
    ]
    right_bxs = [
        bx for (bx, by) in classif.get("right_bottom_pts", [])
        if bx is not None and by < height and by >= min_y
    ]

    # Need one valid line on each side
    if not left_bxs or not right_bxs:
        return False, "unknown"

    left_ok = any(bx <= width * config.LEFT_EDGE_X_MAX for bx in left_bxs)
    right_ok = any(bx >= width * config.RIGHT_EDGE_X_MIN for bx in right_bxs)
    if not (left_ok and right_ok):
        return False, "unknown"

    # Check dashed middle between left and right boundaries
    min_left = min(left_bxs)
    max_right = max(right_bxs)
    if not (min_left < mid_x < max_right):
        return False, "unknown"

    # --- Decide lane band depending on mid_x ---
    center_x = width * 0.5
    if mid_x >= center_x:
        # Dashed line closer to right → robot is in LEFT lane
        band = config.MID_BAND_LEFT_LANE
        tag = "left_lane"
    else:
        # Dashed line closer to left → robot is in RIGHT lane
        band = config.MID_BAND_RIGHT_LANE
        tag = "right_lane"

    # Check if dashed mid_x falls inside expected band
    if not (band[0] * width <= mid_x <= band[1] * width):
        return False, "unknown"

    # --- Visualization (only if frame is given) ---
    if frame is not None:
        # Yellow horizontal = bottom acceptance band
        cv2.line(frame, (0, min_y), (width, min_y), (0, 255, 255), 2)

        # Red verticals = left/right acceptance thresholds
        x_left = int(config.LEFT_EDGE_X_MAX * width)
        x_right = int(config.RIGHT_EDGE_X_MIN * width)
        cv2.line(frame, (x_left, height), (x_left, min_y), (0, 0, 255), 2)
        cv2.line(frame, (x_right, height), (x_right, min_y), (0, 0, 255), 2)

        # Green rectangle = accepted mid band for current lane
        x_band1 = int(band[0] * width)
        x_band2 = int(band[1] * width)
        cv2.rectangle(frame, (x_band1, min_y), (x_band2, height), (0, 255, 0), 2)

        # Mark detected mid_x
        if mid_x is not None:
            cv2.circle(frame, (int(mid_x), height - 10), 6, (255, 0, 0), -1)

    return True, tag


def frame_index_to_ms(idx):
    return int(round(idx * 1000.0 / config.FPS))
