# import cv2
# import numpy as np
# from src import config

# def _roi_mask(h, w):
#     mask = np.zeros((h, w), dtype=np.uint8)
#     top = int(h * config.ROI_TOP_RATIO)
#     bottom_cut = int(h * (1.0 - config.BOTTOM_CROP_RATIO))
#     polygon = np.array([[
#         (0, h), (w, h),
#         (w, top), (0, top)
#     ]], np.int32)
#     cv2.fillPoly(mask, polygon, 255)
#     # remove bottom timestamp strip
#     mask[bottom_cut:h, :] = 0
#     return mask

# def preprocess(frame_bgr):
#     gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
#     gray = cv2.GaussianBlur(gray, (5,5), 0)
#     edges = cv2.Canny(gray, config.CANNY_LOW, config.CANNY_HIGH)

#     h, w = edges.shape
#     mask = _roi_mask(h, w)
#     cropped = cv2.bitwise_and(edges, mask)

#     # strengthen edges a bit (helps Hough on faint lines)
#     kernel = np.ones((3,3), np.uint8)
#     cropped = cv2.morphologyEx(cropped, cv2.MORPH_CLOSE, kernel, iterations=1)
#     return cropped

# def detect_lines(edge_img):
#     lines = cv2.HoughLinesP(
#         edge_img,
#         rho=1,
#         theta=np.pi/180,
#         threshold=config.HOUGH_THRESHOLD,
#         minLineLength=config.HOUGH_MIN_LINE,
#         maxLineGap=config.HOUGH_MAX_GAP
#     )
#     if lines is None:
#         return []
#     return [l[0] for l in lines]  # (x1,y1,x2,y2)














import cv2
import numpy as np
from src import config

def _roi_mask(h, w):
    mask = np.zeros((h, w), dtype=np.uint8)
    top = int(h * config.ROI_TOP_RATIO)
    bottom_cut = int(h * (1.0 - config.BOTTOM_CROP_RATIO))
    polygon = np.array([[
        (0, h), (w, h),
        (w, top), (0, top)
    ]], np.int32)
    cv2.fillPoly(mask, polygon, 255)
    # remove bottom timestamp strip
    mask[bottom_cut:h, :] = 0
    return mask

def preprocess(frame_bgr):
    """Improved preprocessing: CLAHE, gamma correction, adaptive threshold, Canny, ROI mask."""
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE for contrast on gray floor
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # Gamma correction (brighten midtones if floor is dark)
    gamma = 1.2
    look_up = np.array([((i / 255.0) ** (1/gamma)) * 255 for i in range(256)]).astype("uint8")
    gray = cv2.LUT(gray, look_up)

    # Reduce noise
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive threshold (helps with variable lighting/reflections)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -5
    )

    # Canny edge detection
    edges = cv2.Canny(thresh, config.CANNY_LOW, config.CANNY_HIGH)

    # Apply ROI mask
    h, w = edges.shape
    mask = _roi_mask(h, w)
    cropped = cv2.bitwise_and(edges, mask)

    # Morphological closing to strengthen broken lines
    kernel = np.ones((3,3), np.uint8)
    cropped = cv2.morphologyEx(cropped, cv2.MORPH_CLOSE, kernel, iterations=1)

    return cropped

def detect_lines(edge_img):
    lines = cv2.HoughLinesP(
        edge_img,
        rho=1,
        theta=np.pi/180,
        threshold=config.HOUGH_THRESHOLD,
        minLineLength=config.HOUGH_MIN_LINE,
        maxLineGap=config.HOUGH_MAX_GAP
    )
    if lines is None:
        return []
    return [l[0] for l in lines]  # (x1,y1,x2,y2)

# --- Rest of the code (classify_lanes, _line_features, draw_debug, etc.)
# stays exactly the same as you pasted ---

def _line_features(line):
    x1, y1, x2, y2 = line
    dx = (x2 - x1) if (x2 - x1) != 0 else 1e-6
    slope = (y2 - y1) / dx
    length = np.hypot(x2 - x1, y2 - y1)
    mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    return slope, length, mx, my

def _bottom_x_intercept(line, height):
    """x where this (possibly extended) line hits bottom (y = height-2). None if horizontal."""
    x1, y1, x2, y2 = line
    dy = y2 - y1
    dx = x2 - x1
    if abs(dy) < 1e-6:
        return None
    y_target = height - 2
    t = (y_target - y1) / dy
    x_at_bottom = x1 + t * dx
    return float(x_at_bottom)

def classify_lanes(lines, width, height):
    """
    Returns:
      dict = {
        'has_left_outer': bool,
        'has_right_outer': bool,
        'middle_dash_count': int,
        'middle_avg_x': float or None,
        'lines_kept': list[(x1,y1,x2,y2)],
        'left_candidates': list[(x1,y1,x2,y2)],
        'right_candidates': list[(x1,y1,x2,y2)],
        'dash_candidates': list[(x1,y1,x2,y2)],
        'left_bottom_xs': list[float],   # outer-line bottom intercepts (pixels)
        'right_bottom_xs': list[float],
      }
    """
    left_cands, right_cands, dash_cands, kept = [], [], [], []
    left_bxs, right_bxs = [], []

    cx_min = config.CENTER_BAND[0] * width
    cx_max = config.CENTER_BAND[1] * width

    for L in lines:
        slope, length, mx, my = _line_features(L)
        if abs(slope) < config.SLOPE_THRESH:
            continue  # too horizontal
        kept.append(L)

        # dashed middle: short segments near image center
        if cx_min <= mx <= cx_max and config.DASH_MIN <= length <= config.DASH_MAX:
            dash_cands.append(L)

        # outer candidates: long lines, classify by which side they lean + bottom-x
        if length >= config.LONG_LINE_THRESH:
            bx = _bottom_x_intercept(L, height)
            if bx is None:
                continue
            if slope < 0:
                left_cands.append(L)
                left_bxs.append(bx)
            elif slope > 0:
                right_cands.append(L)
                right_bxs.append(bx)

    # Count dashed segments with vertical separation so we don't double-count
    if dash_cands:
        # sort by center y so separated dashes are counted
        def my_of(L):
            return (L[1] + L[3]) / 2.0
        dash_sorted = sorted(dash_cands, key=my_of)
        counted = []
        for L in dash_sorted:
            my = my_of(L)
            if not counted:
                counted.append((L, my))
            else:
                if abs(my - counted[-1][1]) >= config.DASH_Y_SEP:
                    counted.append((L, my))
        dash_count = len(counted)
        middle_avg_x = float(np.mean([(p[0][0]+p[0][2])/2.0 for p in counted])) if counted else None
        dash_cands = [p[0] for p in counted]
    else:
        dash_count = 0
        middle_avg_x = None

    out = {
        'has_left_outer': len(left_cands) > 0,
        'has_right_outer': len(right_cands) > 0,
        'middle_dash_count': dash_count,
        'middle_avg_x': middle_avg_x,
        'lines_kept': kept,
        'left_candidates': left_cands,
        'right_candidates': right_cands,
        'dash_candidates': dash_cands,
        'left_bottom_xs': left_bxs,
        'right_bottom_xs': right_bxs,
    }
    return out

def draw_debug(frame_bgr, info):
    vis = frame_bgr.copy()
    h, w, _ = vis.shape

    # ROI box + bottom cut line
    top = int(h * config.ROI_TOP_RATIO)
    bottom_cut = int(h * (1.0 - config.BOTTOM_CROP_RATIO))
    cv2.rectangle(vis, (0, top), (w, h), (255, 255, 0), 1)
    cv2.line(vis, (0, bottom_cut), (w, bottom_cut), (0, 255, 255), 1)

    # Draw Hough lines
    for (x1,y1,x2,y2) in info.get('lines_kept', []):
        cv2.line(vis, (x1,y1), (x2,y2), (0,255,0), 2)
    for L in info.get('dash_candidates', []):
        x1,y1,x2,y2 = L
        cv2.line(vis, (x1,y1), (x2,y2), (0,0,255), 3)  # dashed = red
    for L in info.get('left_candidates', []):
        x1,y1,x2,y2 = L
        cv2.line(vis, (x1,y1), (x2,y2), (255,0,0), 3)  # left outer = blue
    for L in info.get('right_candidates', []):
        x1,y1,x2,y2 = L
        cv2.line(vis, (x1,y1), (x2,y2), (0,165,255), 3)  # right outer = orange

    # Center bands
    cx_min = int(config.CENTER_BAND[0] * w)
    cx_max = int(config.CENTER_BAND[1] * w)
    cv2.line(vis, (cx_min, 0), (cx_min, h), (200,200,200), 1)
    cv2.line(vis, (cx_max, 0), (cx_max, h), (200,200,200), 1)

    # Tighter mid band for "good" check
    mid_t_min = int(config.MID_BAND_FOR_GOOD[0] * w)
    mid_t_max = int(config.MID_BAND_FOR_GOOD[1] * w)
    cv2.line(vis, (mid_t_min, 0), (mid_t_min, h), (180,180,180), 1)
    cv2.line(vis, (mid_t_max, 0), (mid_t_max, h), (180,180,180), 1)

    # Edge gates
    lx_gate = int(config.LEFT_EDGE_X_MAX * w)
    rx_gate = int(config.RIGHT_EDGE_X_MIN * w)
    cv2.line(vis, (lx_gate, h-1), (lx_gate, h-60), (255,0,0), 2)
    cv2.line(vis, (rx_gate, h-1), (rx_gate, h-60), (0,165,255), 2)

    # Mark bottom intercepts
    for bx in info.get('left_bottom_xs', []):
        cv2.circle(vis, (int(bx), h-3), 5, (255,0,0), -1)
    for bx in info.get('right_bottom_xs', []):
        cv2.circle(vis, (int(bx), h-3), 5, (0,165,255), -1)

    # Mark middle avg x
    mid_x = info.get('middle_avg_x', None)
    if mid_x is not None:
        cv2.circle(vis, (int(mid_x), int(h*0.75)), 5, (0,0,255), -1)

    return vis
