# analyzer.py
import cv2
from src import config

def decide_tags(classif, width, height, frame=None):
    """
    Decide lane tags and 'good_driving' for a two-lane road.
    
    Lane detection logic:
      - If both outer solids are detected → decide lane by dashed line position
      - If only left solid is seen → assume right lane
      - If only right solid is seen → assume left lane
      - Else → unknown

    Good driving:
      - Must have dashed line + both outer lines
      - Dashed must fall within config.MID_BAND_FOR_GOOD (normalized x range)
    """

    mid_x = classif.get("middle_avg_x", None)
    dash_count = classif.get("middle_dash_count", 0)
    left_bxs = classif.get("left_bottom_xs", [])
    right_bxs = classif.get("right_bottom_xs", [])

    has_left = len(left_bxs) > 0
    has_right = len(right_bxs) > 0

    # ---- Lane side tagging ----
    lane_tag = "unknown"
    if has_left and has_right:
        # Use bottom-most x coordinates of left and right lines
        left_x = left_bxs[0]  # lowest point detected on left solid
        right_x = right_bxs[0]  # lowest point detected on right solid
        mid_frame_x = width // 2
        # whichever side your car is closer to decides lane
        if abs(mid_frame_x - left_x) < abs(mid_frame_x - right_x):
            lane_tag = "left_lane"
        else:
            lane_tag = "right_lane"
    elif has_left and not has_right:
        lane_tag = "right_lane"
    elif has_right and not has_left:
        lane_tag = "left_lane"

    # ---- Good driving ----
    good = False
    if has_left and has_right and dash_count >= 1 and mid_x is not None:
        band_min, band_max = config.MID_BAND_FOR_GOOD
        frac = mid_x / width
        if band_min <= frac <= band_max:
            good = True

    # ---- Debug visualization ----
    if frame is not None:
        h = frame.shape[0]
        if mid_x is not None:
            cv2.circle(frame, (int(mid_x), h - 20), 6, (0, 0, 255), -1)  # mark dash
        # show horizontal acceptance band (for bottom region)
        min_y = int(height * (1.0 - config.BOTTOM_ACCEPT_BAND))
        cv2.line(frame, (0, min_y), (width, min_y), (0, 255, 255), 2)

    return good, lane_tag


def frame_index_to_ms(idx):
    """Keep frame index as ms marker (no scaling)."""
    return idx