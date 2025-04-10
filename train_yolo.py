from ultralytics import YOLO

# Load pre-trained model (e.g., yolov8n.pt = nano, very small)
model = YOLO('yolov8n.pt')  # or yolov8s.pt / yolov8m.pt depending on your GPU

# Train on your dataset
model.train(
    data='preprocessed_dataset/data.yaml',
    epochs=150,
    imgsz=640,
    batch=8,
    name='yolo-custom',
    pretrained=True,
    patience=10
)
