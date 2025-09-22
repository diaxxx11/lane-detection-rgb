import cv2
from src import config

def decide_tags(classif, width, height, frame=None):
    """
    Decide lane tags and 'good_driving'.
    Good driving = robot is inside either lane:
      - both outer continuous lines are visible (left + right)
      - a dashed center line is visible
      - and the dashed line is reasonably near the middle
    """

    mid_x = classif.get("middle_avg_x", None)
    dash_count = classif.get("middle_dash_count", 0)
    left_outer = classif.get("left_candidates", [])
    right_outer = classif.get("right_candidates", [])

    # ---- Lane side tagging ----
    if left_outer and not right_outer:
        lane_tag = "left_lane"
    elif right_outer and not left_outer:
        lane_tag = "right_lane"
    elif mid_x is not None:
        lane_tag = "left_lane" if mid_x >= width * 0.5 else "right_lane"
    else:
        lane_tag = "unknown"

    # ---- Good driving ----
    good = False
    if dash_count >= 1 and left_outer and right_outer and mid_x is not None:
        # dash must be in the acceptable mid band
        band_min, band_max = config.MID_BAND_FOR_GOOD
        frac = mid_x / width
        if band_min <= frac <= band_max:
            good = True

    # ---- Debug visualization ----
    if frame is not None:
        h = frame.shape[0]
        if mid_x is not None:
            cv2.circle(frame, (int(mid_x), h - 10), 6, (255, 0, 0), -1)
        min_y = int(height * (1.0 - config.BOTTOM_ACCEPT_BAND))
        cv2.line(frame, (0, min_y), (width, min_y), (0, 255, 255), 2)

    return good, lane_tag


def frame_index_to_ms(idx):
    """Keep frame index as ms marker (no scaling)."""
    return idx