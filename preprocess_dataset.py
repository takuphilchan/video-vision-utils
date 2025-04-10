import os
import shutil
import random
from pathlib import Path

# -------- CONFIG --------
DATASET_DIR = "raw_dataset"  # folder containing .png, .txt, and classes.txt
OUTPUT_DIR = "preprocessed_dataset"
TRAIN_SPLIT = 0.8
IMAGE_EXTS = [".png", ".jpg", ".jpeg"]  # adjust if needed
# ------------------------

def get_image_files(folder):
    return [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in IMAGE_EXTS]

def load_classes(filepath):
    with open(filepath, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    return classes

def main():
    os.makedirs(f"{OUTPUT_DIR}/images/train", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/images/val", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/labels/train", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/labels/val", exist_ok=True)

    images = get_image_files(DATASET_DIR)
    random.shuffle(images)

    split_idx = int(len(images) * TRAIN_SPLIT)
    train_images = images[:split_idx]
    val_images = images[split_idx:]

    def move_data(image_list, subset):
        for img in image_list:
            base_name = os.path.splitext(img)[0]
            img_src = os.path.join(DATASET_DIR, img)
            label_src = os.path.join(DATASET_DIR, f"{base_name}.txt")

            if not os.path.exists(label_src):
                print(f"[Warning] Label file not found for {img}")
                continue

            shutil.copy(img_src, f"{OUTPUT_DIR}/images/{subset}/{img}")
            shutil.copy(label_src, f"{OUTPUT_DIR}/labels/{subset}/{base_name}.txt")

    move_data(train_images, "train")
    move_data(val_images, "val")

    # Generate data.yaml
    classes_path = os.path.join(DATASET_DIR, "classes.txt")
    if not os.path.exists(classes_path):
        print("classes.txt not found. Skipping data.yaml creation.")
        return

    class_names = load_classes(classes_path)
    with open(f"{OUTPUT_DIR}/data.yaml", "w") as f:
        f.write(f"train: {os.path.abspath(OUTPUT_DIR)}/images/train\n")
        f.write(f"val: {os.path.abspath(OUTPUT_DIR)}/images/val\n")
        f.write(f"\nnc: {len(class_names)}\n")
        f.write(f"names: {class_names}\n")

    print("✅ YOLO dataset prepared successfully!")

if __name__ == "__main__":
    main()
