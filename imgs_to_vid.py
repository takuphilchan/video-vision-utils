import cv2
import os

# Path to the folder containing the images
image_folder = 'output_2'

# Get the list of images in the folder
images = [img for img in os.listdir(image_folder) if img.endswith(".jpg") or img.endswith(".png")]

# Sort images by filename (ensure correct order)
images.sort()

# Read the first image to get the frame size (width and height)
first_image = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = first_image.shape

# Define the codec and create a VideoWriter object for MP4 output
output_video_path = 'update.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use 'H264' or 'mp4v' for MP4 files
fps = 30  # Frames per second (adjust as needed)
video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

# Loop through the images and write them to the video
for image in images:
    image_path = os.path.join(image_folder, image)
    img = cv2.imread(image_path)
    video_writer.write(img)

# Release the video writer object
video_writer.release()

print(f"Video saved as {output_video_path}")
