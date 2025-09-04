# main.py
import os
import cv2
from src.lane_detector import preprocess, detect_lines, classify_lanes, draw_debug
from src.analyzer import decide_tags, frame_index_to_ms
from src.writer import write_sections
from src import config

def main():
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    if config.SAVE_DEBUG_FRAMES:
        os.makedirs(config.DEBUG_DIR, exist_ok=True)

    frames = [f for f in os.listdir(config.FRAMES_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    frames.sort()

    sections = []
    current = None

    for i, name in enumerate(frames):
        path = os.path.join(config.FRAMES_DIR, name)
        frame = cv2.imread(path)
        if frame is None:
            continue

        edges = preprocess(frame)
        lines = detect_lines(edges)
        info = classify_lanes(lines, frame.shape[1], frame.shape[0])
        info["index"] = i  # so analyzer can name files

        # ---- ALWAYS produce a visible debug overlay periodically, AND when good
        vis = draw_debug(frame, info)  # draws your Hough groups and guides
        good, lane_tag = decide_tags(info, frame.shape[1], frame.shape[0], frame=vis)

        cur_ms = frame_index_to_ms(i)

        # Section logic
        if good and lane_tag != "unknown":
            if current is None:
                current = {'start': cur_ms, 'tags': ["good_driving", lane_tag], 'end': cur_ms}
            else:
                if lane_tag not in current['tags']:
                    current['end'] = cur_ms
                    sections.append(current)
                    current = {'start': cur_ms, 'tags': ["good_driving", lane_tag], 'end': cur_ms}
                else:
                    current['end'] = cur_ms
        else:
            if current is not None:
                current['end'] = cur_ms
                sections.append(current)
                current = None

        # Save periodic debug frames even if NOT good (for tuning)
        if config.SAVE_DEBUG_FRAMES and (good or (i % config.DEBUG_EVERY_N == 0)):
            status_str = "GOOD" if good else "BAD"
            lane_str = lane_tag
            cv2.putText(vis, f"{status_str} | {lane_str}", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(vis, f"{status_str} | {lane_str}", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2, cv2.LINE_AA)
            out_path = os.path.join(config.DEBUG_DIR, f"dbg_{i:06d}.png")
            cv2.imwrite(out_path, vis)

        if (i + 1) % 100 == 0:
            print(f"[{i+1}/{len(frames)}] processed")

    if current is not None:
        sections.append(current)

    write_sections(sections)
    print("Done. Sections written and debug frames saved.")

if __name__ == "__main__":
    main()
