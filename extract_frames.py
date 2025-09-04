import cv2
import os

def extract_frames(video_path, output_folder, every_n_frames=1):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Open video
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # video ended

        # Save every nth frame
        if frame_count % every_n_frames == 0:
            frame_name = f"frame_{saved_count:06d}.png"
            cv2.imwrite(os.path.join(output_folder, frame_name), frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"✅ Extracted {saved_count} frames to {output_folder}")

if __name__ == "__main__":
    video_path = "data/rgb_data/original_video_stamped.mp4"  # <-- change to your RGB recording
    output_folder = "frames_rgb"
    extract_frames(video_path, output_folder, every_n_frames=1)  # every frame
