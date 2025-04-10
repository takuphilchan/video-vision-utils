from ultralytics import YOLO
import cv2
import numpy as np

# Constants
VIDEO_PATH = 'test_vids/brace.mp4'
MODEL_PATH = 'runs/detect/yolo-custom3/weights/best.pt'
OUTPUT_PATH = 'output_brace.mp4'
FEATHER = 25  # for Gaussian blur
SIDE_PAD_RATIO = 0.1  # 10% of bbox width to sample side pixels
MAX_SKIP_FRAMES = 5  # max frames to interpolate without detection

# Load YOLO model
model = YOLO(MODEL_PATH)

# Open video
cap = cv2.VideoCapture(VIDEO_PATH)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)
width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (width, height))

# Detection results as generator
results = model(VIDEO_PATH, stream=True)

# Store previous boxes
previous_boxes = []
skip_counter = 0

# Process frames
for r in results:
    frame = r.orig_img.copy()
    h, w = frame.shape[:2]
    current_boxes = []

    # If detections exist, update box list
    if r.boxes and len(r.boxes) > 0:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            current_boxes.append((x1, y1, x2, y2))
        previous_boxes = current_boxes.copy()
        skip_counter = 0
    else:
        if skip_counter < MAX_SKIP_FRAMES and previous_boxes:
            current_boxes = previous_boxes.copy()
            skip_counter += 1
        else:
            previous_boxes = []
            skip_counter = 0
            out.write(frame)
            continue  # nothing to inpaint

    # For each box, blend in content from left and right
    for x1, y1, x2, y2 in current_boxes:
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w - 1, x2), min(h - 1, y2)
        box_w = x2 - x1
        if box_w < 1 or y2 - y1 < 1:
            continue

        pad = max(1, int(box_w * SIDE_PAD_RATIO))
        left_patch = frame[y1:y2, max(0, x1 - pad):x1]
        right_patch = frame[y1:y2, x2:min(w, x2 + pad)]

        # Blend left and right patches
        if left_patch.size > 0 and right_patch.size > 0:
            patch = cv2.addWeighted(left_patch, 0.5, right_patch, 0.5, 0)
        elif left_patch.size > 0:
            patch = left_patch
        elif right_patch.size > 0:
            patch = right_patch
        else:
            continue

        patch_resized = cv2.resize(patch, (x2 - x1, y2 - y1))

        # Create feathered blend mask
        mask = np.ones((y2 - y1, x2 - x1), dtype=np.float32)
        mask = cv2.GaussianBlur(mask, (FEATHER, FEATHER), 0)
        mask = mask[..., np.newaxis]

        # Blend into original frame
        roi = frame[y1:y2, x1:x2].astype(np.float32)
        blended = (roi * (1 - mask) + patch_resized * mask).astype(np.uint8)
        frame[y1:y2, x1:x2] = blended

    out.write(frame)

# Cleanup
cap.release()
out.release()
print(f"✅ Done! Output saved to: {OUTPUT_PATH}")