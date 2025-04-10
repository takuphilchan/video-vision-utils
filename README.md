# YOLO Video Inpainting & Training

This repository contains two Python scripts that interact with YOLO (You Only Look Once) models for video processing and training. The two scripts are:

1. **`test_yolo.py`**: Performs video object detection with YOLO, and inpaints missing frames using surrounding pixels.
2. **`train_yolo.py`**: Trains a custom YOLO model on your own dataset.

## Requirements

- Python 3.8+
- Install the necessary dependencies by running:

```bash
pip install -r requirements.txt
```

### `requirements.txt` (Sample)

```txt
ultralytics
opencv-python
numpy
```

---

## 1. **`test_yolo.py`** - Object Detection and Video Inpainting

This script loads a pre-trained YOLO model and performs object detection on a given video. If no detection is found in a frame, the script interpolates using pixels from previous frames to fill in the missing content, resulting in smooth video playback. The processed video is saved to a new file.

### How it works:
- **Video Input**: Loads a video file (`test_vids/brace.mp4`) and runs YOLO object detection.
- **Model**: Uses a pre-trained YOLO model (`best.pt`).
- **Inpainting**: If no detection is found, interpolates the missing frame content by blending pixels from nearby frames.

### Parameters:
- `VIDEO_PATH`: Path to the input video (`test_vids/brace.mp4`).
- `MODEL_PATH`: Path to the pre-trained YOLO model (`best.pt`).
- `OUTPUT_PATH`: Path where the output video will be saved (`output_brace.mp4`).
- `FEATHER`: Controls the smoothness of blending (Gaussian blur).
- `SIDE_PAD_RATIO`: Side padding ratio for bounding boxes during inpainting.
- `MAX_SKIP_FRAMES`: Maximum number of frames to skip during detection interpolation.

### Usage:

```bash
python test_yolo.py
```

### Output:
- The processed video with inpainted frames will be saved as `output_brace.mp4`.

---

## 2. **`train_yolo.py`** - Train Custom YOLO Model

This script trains a custom YOLO model using your own dataset. You can use it to fine-tune YOLO on a specific task or dataset.

### How it works:
- Loads a pre-trained YOLO model (`yolov8n.pt`) and fine-tunes it on your dataset.
- Training parameters like epochs, batch size, and image size can be adjusted.

### Parameters:
- `data`: Path to a `data.yaml` file describing your dataset.
- `epochs`: Number of epochs to train for.
- `imgsz`: Image size for training.
- `batch`: Batch size for training.
- `name`: Name for the model training run.
- `pretrained`: Whether to use a pre-trained model for transfer learning.
- `patience`: Early stopping patience (for best model selection).

### Usage:

To train the model on your dataset:

```bash
python train_yolo.py
```

### Notes:
- Before training, make sure your dataset is preprocessed and the paths are correctly set in `data.yaml`.

---

## Example Workflow

1. **Object Detection (Inpainting)**:
    - Use `test_yolo.py` to process your video.
    - The script will detect objects in each frame and perform inpainting when no detection is found.

2. **Training**:
    - If you have a custom dataset, use `train_yolo.py` to train a new model.
    - After training, you can use the trained model for object detection.

---
