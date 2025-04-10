import cv2
import numpy as np

# Load the image
image_path = 'img/frame_00000.jpg'
img = cv2.imread(image_path)

# Create a mask where the logo is (rough bounding box based on image size)
mask = np.zeros(img.shape[:2], dtype=np.uint8)

# Define the logo area manually (adjust as needed)
# Format: (x1, y1) = top-left corner, (x2, y2) = bottom-right corner
x1, y1 = 330, 220
x2, y2 = 390, 270
mask[y1:y2, x1:x2] = 255

# Inpaint to remove the logo
result = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

# Save the output
cv2.imwrite('removed/cleaned_bracelet.jpg', result)
print("Logo removed and saved as 'cleaned_bracelet.jpg'")
