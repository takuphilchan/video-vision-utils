import cv2
import os

def video_to_images(video_path, output_folder, frame_skip=1):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Load the video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        # Save every `frame_skip`-th frame
        if frame_count % frame_skip == 0:
            filename = os.path.join(output_folder, f"frame_{saved_count:05d}.png")
            cv2.imwrite(filename, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Done. {saved_count} frames saved to {output_folder}")

# Example usage:
video_to_images("output_2.mp4", "output_2", frame_skip=1)
