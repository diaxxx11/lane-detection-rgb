<<<<<<< HEAD
# # from src import config
# # import cv2
# # import numpy as np


# # def decide_tags(classif, width, height, frame=None):
# #     """
# #     GOOD if:
# #       - >= 2 dashed middle segments detected
# #       - left outer line near left edge AND right outer line near right edge
# #       - dashed middle lies between them
# #       - bottom intercepts are inside the accepted vertical band
# #     Lane side:
# #       - If dashed middle is closer to the right half -> robot is in LEFT lane
# #       - If dashed middle is closer to the left half -> robot is in RIGHT lane
# #     """

# #     mid_x = classif.get("middle_avg_x", None)
# #     dash_ok = (classif.get("middle_dash_count", 0) >= 1) and (mid_x is not None)
# #     if not dash_ok:
# #         return False, "unknown"

# #     # --- Gather bottom intercepts above bottom band ---
# #     min_y = int(height * (1.0 - config.BOTTOM_ACCEPT_BAND))
# #     left_bxs = [
# #         bx for (bx, by) in classif.get("left_bottom_pts", [])
# #         if bx is not None and by < height and by >= min_y
# #     ]
# #     right_bxs = [
# #         bx for (bx, by) in classif.get("right_bottom_pts", [])
# #         if bx is not None and by < height and by >= min_y
# #     ]

# #     # Need one valid line on each side
# #     if not left_bxs or not right_bxs:
# #         return False, "unknown"

# #     left_ok = any(bx <= width * config.LEFT_EDGE_X_MAX for bx in left_bxs)
# #     right_ok = any(bx >= width * config.RIGHT_EDGE_X_MIN for bx in right_bxs)
# #     if not (left_ok and right_ok):
# #         return False, "unknown"

# #     # Check dashed middle between left and right boundaries
# #     min_left = min(left_bxs)
# #     max_right = max(right_bxs)
# #     if not (min_left < mid_x < max_right):
# #         return False, "unknown"

# #     # --- Decide lane band depending on mid_x ---
# #     center_x = width * 0.5
# #     if mid_x >= center_x:
# #         # Dashed line closer to right → robot is in LEFT lane
# #         band = config.MID_BAND_LEFT_LANE
# #         tag = "left_lane"
# #     else:
# #         # Dashed line closer to left → robot is in RIGHT lane
# #         band = config.MID_BAND_RIGHT_LANE
# #         tag = "right_lane"

# #     # Check if dashed mid_x falls inside expected band
# #     if not (band[0] * width <= mid_x <= band[1] * width):
# #         return False, "unknown"

# #     # --- Visualization (only if frame is given) ---
# #     if frame is not None:
# #         # Yellow horizontal = bottom acceptance band
# #         cv2.line(frame, (0, min_y), (width, min_y), (0, 255, 255), 2)

# #         # Red verticals = left/right acceptance thresholds
# #         x_left = int(config.LEFT_EDGE_X_MAX * width)
# #         x_right = int(config.RIGHT_EDGE_X_MIN * width)
# #         cv2.line(frame, (x_left, height), (x_left, min_y), (0, 0, 255), 2)
# #         cv2.line(frame, (x_right, height), (x_right, min_y), (0, 0, 255), 2)

# #         # Green rectangle = accepted mid band for current lane
# #         x_band1 = int(band[0] * width)
# #         x_band2 = int(band[1] * width)
# #         cv2.rectangle(frame, (x_band1, min_y), (x_band2, height), (0, 255, 0), 2)

# #         # Mark detected mid_x
# #         if mid_x is not None:
# #             cv2.circle(frame, (int(mid_x), height - 10), 6, (255, 0, 0), -1)

# #     return True, tag


# # def frame_index_to_ms(idx):
# #     return int(round(idx * 1000.0 / config.FPS))




# # src/analyzer.py
# import cv2
# from src import config

# def decide_tags(classif, width, height, frame=None):
#     """
#     Decide lane tags and 'good_driving'.
#     - Always try to return a lane tag (left_lane / right_lane).
#     - Add 'good_driving' if stricter conditions are satisfied.
#     """

#     tags = []
#     mid_x = classif.get("middle_avg_x", None)
#     dash_count = classif.get("middle_dash_count", 0)

#     # ---- Lane side tagging (looser) ----
#     if mid_x is not None:
#         center_x = width * 0.5
#         if mid_x >= center_x:
#             lane_tag = "left_lane"
#         else:
#             lane_tag = "right_lane"
#         tags.append(lane_tag)
#     else:
#         # fallback if dash is missing but we have outer lines
#         if classif.get("has_left_outer") and not classif.get("has_right_outer"):
#             tags.append("left_lane")
#         elif classif.get("has_right_outer") and not classif.get("has_left_outer"):
#             tags.append("right_lane")
#         else:
#             tags.append("unknown")

#     # ---- Good driving criteria (stricter) ----
#     if dash_count >= 1 and mid_x is not None:
#         # Bottom acceptance band
#         min_y = int(height * (1.0 - config.BOTTOM_ACCEPT_BAND))

#         # Bottom intercepts from classifier
#         left_bxs = [
#             bx for bx in classif.get("left_bottom_xs", [])
#             if bx is not None
#         ]
#         right_bxs = [
#             bx for bx in classif.get("right_bottom_xs", [])
#             if bx is not None
#         ]

#         if left_bxs and right_bxs:
#             min_left = min(left_bxs)
#             max_right = max(right_bxs)

#             # dashed mid_x must lie between left and right intercepts
#             if min_left < mid_x < max_right:
#                 center_x = width * 0.5
#                 if mid_x >= center_x:
#                     band = config.MID_BAND_LEFT_LANE
#                 else:
#                     band = config.MID_BAND_RIGHT_LANE

#                 if band[0] * width <= mid_x <= band[1] * width:
#                     tags.append("good_driving")

#     # ---- Debug visualization ----
#     if frame is not None:
#         # mark mid_x if found
#         if mid_x is not None:
#             cv2.circle(frame, (int(mid_x), height - 10), 6, (255, 0, 0), -1)
#         # mark bottom acceptance line
#         min_y = int(height * (1.0 - config.BOTTOM_ACCEPT_BAND))
#         cv2.line(frame, (0, min_y), (width, min_y), (0, 255, 255), 2)

#     # Return tuple
#     return "good_driving" in tags, tags[-1] if tags else "unknown"


# # def frame_index_to_ms(idx):
# #     """Convert frame index to ms using config.FPS"""
# #     return int(round(idx * 1000.0 / config.FPS))

# def frame_index_to_ms(idx):
#     """Return frame index itself instead of converting to ms"""
#     return idx






# src/analyzer.py
=======
# analyzer.py
>>>>>>> bb22f9f (last stable update)
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