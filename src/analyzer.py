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


import cv2
from src import config

def decide_tags(classif, width, height, frame=None):
    """
    Decide lane tags and 'good_driving'.
    Returns:
        good (bool): True if 'good_driving' conditions are satisfied.
        lane_tag (str): "left_lane", "right_lane", or "unknown".
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
    if dash_count >= 1:
        dash_lines = classif.get("dash_candidates", [])
        dash_slopes = [((l[3]-l[1])/(l[2]-l[0]+1e-6)) for l in dash_lines]

        if left_outer and not right_outer:
            if dash_lines and any(s < 0 for s in dash_slopes):
                good = True
        elif right_outer and not left_outer:
            if dash_lines and any(s > 0 for s in dash_slopes):
                good = True
        elif left_outer and right_outer and mid_x is not None:
            if mid_x >= width * 0.5 and any(s < 0 for s in dash_slopes):
                good = True
            elif mid_x < width * 0.5 and any(s > 0 for s in dash_slopes):
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
    """
    Return frame index itself instead of converting to ms.
    Keeps frame numbers aligned with debug frames and output.
    """
    return idx
