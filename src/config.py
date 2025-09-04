import os

# === INPUT ===
# Folder containing your RGB frames (PNG/JPG). Relative to this file.
FRAMES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frames_rgb"))

# Frames per second of your original RGB video (used for ms timestamps).
FPS = 30.0  # <-- change if your video had a different fps

# === OUTPUT ===
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
ANNOTATION_PATH = os.path.join(OUTPUT_DIR, "annotations.txt")
DEBUG_DIR = os.path.join(OUTPUT_DIR, "debug_frames")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "sections.txt")

# Save annotated preview frames?
SAVE_DEBUG_FRAMES = True

# === ROI (region of interest) ===
ROI_TOP_RATIO = 0.45        # keep bottom 55% of the frame (road area)
BOTTOM_CROP_RATIO = 0.06    # crop out bottom strip (timestamp text area), e.g., last 6%

# === Hough/Canny parameters (tweak if needed) ===
CANNY_LOW = 50
CANNY_HIGH = 150
HOUGH_THRESHOLD = 60
HOUGH_MIN_LINE = 60
HOUGH_MAX_GAP = 40

# === Lane classification heuristics ===
SLOPE_THRESH = 0.4          # abs(slope) must be > this to be "vertical-ish"
LONG_LINE_THRESH = 140      # pixels; outer boundary should be relatively long
CENTER_BAND = 0.38, 0.62   # x-range (as fraction of width) considered "near center" for dashed
DASH_MIN = 18               # min short-segment length (pixels)
DASH_MAX = 110              # max short-segment length (pixels)
DASH_Y_SEP = 36             # min vertical separation between counted dashed segments (pixels)

# --- Geometry gates for GOOD DRIVING ---
# Where the outer (continuous) line should hit the bottom edge
LEFT_EDGE_X_MAX = 0.35      # <= 30% of width from left
RIGHT_EDGE_X_MIN = 0.65     # >= 70% of width from left

# How close to the center the dashed line must be to count as "middle"
MID_BAND_FOR_GOOD = (0.30, 0.70)  # tighter than CENTER_BAND used for detection

# Minimum horizontal separation between middle dashed x and the outer-line bottom x
MIN_CENTER_SEP = 0.12       # 12% of image width

# Fraction of the bottom vertical region to accept intersections for "good driving"
BOTTOM_ACCEPT_BAND = 0.30    # consider only bottom 10% of frame for outer line intersections

# Save a debug frame every N frames even when not "good"
DEBUG_EVERY_N = 30  # tweak as you like (e.g., 10 for more density)


# If robot is in left lane → center dash should be right
MID_BAND_LEFT_LANE  = (0.40, 0.95)   # right half  
# If robot is in right lane → center dash should be left
MID_BAND_RIGHT_LANE = (0.05, 0.60)   # left half
