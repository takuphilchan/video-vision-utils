import cv2
import numpy as np

def track_clasp_in_video(video_path, output_path=None):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return
    
    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video properties: {frame_width}x{frame_height}, {fps} FPS, {total_frames} frames")
    
    # Setup output video if requested
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    # Adjusted bounding box coordinates, format: (x, y, width, height)
    initial_bbox = (frame_width // 2 - 10, frame_height // 2 - 75, 20, 10)
    
    # Size multiplier for the patch - increase this value to make the patch larger
    size_multiplier = 1.2  # Slightly smaller to simulate depth effect
    
    # Create tracker
    tracker = cv2.TrackerCSRT_create()
    
    # Initialize the tracker with the first frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read the first frame.")
        cap.release()
        return
    
    # Make a copy of the original frame for display
    original_frame = frame.copy()
    
    # Initialize tracker
    bbox = initial_bbox
    success = tracker.init(frame, bbox)
    
    frame_count = 0
    
    # Sample bracelet colors from first frame
    x, y, w, h = bbox
    
    # Create a mask for sampling bracelet colors (excluding the clasp area itself)
    sample_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    
    # Define a wider area around the clasp for sampling
    sample_area = (x-40, y-10, w+80, h+20)
    sx, sy, sw, sh = sample_area
    
    # Ensure coordinates are within image bounds
    sx = max(0, sx)
    sy = max(0, sy)
    sw = min(sw, frame_width - sx)
    sh = min(sh, frame_height - sy)
    
    # Set sampling area in mask
    sample_mask[sy:sy+sh, sx:sx+sw] = 255
    
    # Exclude the clasp area itself from sampling
    clasp_area = (x, y, w, h)
    cx, cy, cw, ch = clasp_area
    sample_mask[cy:cy+ch, cx:cw+ch] = 0
    
    # Sample colors from the masked area
    bracelet_pixels = frame[sample_mask == 255]
    
    if len(bracelet_pixels) > 0:
        # Calculate average color from samples
        bracelet_color = np.mean(bracelet_pixels, axis=0).astype(np.uint8)
    else:
        # Fallback if sampling fails
        bracelet_color = np.array([192, 192, 192], dtype=np.uint8)  # Silver color in BGR
    
    print(f"Sampled bracelet color (BGR): {bracelet_color}")
    
    # Define a more silver-like color (BGR format)
    silver_color = np.array([255, 255, 255], dtype=np.uint8)  # Brighter silver
    
    # Blend the sampled color with silver for a more metallic look
    silver_blend_factor = 0.99  # Higher values = more silver (range 0-1)
    enhanced_color = cv2.addWeighted(
        np.array([bracelet_color]), 1 - silver_blend_factor, 
        np.array([silver_color]), silver_blend_factor, 
        0
    )[0].astype(np.uint8)
    
    print(f"Enhanced silver color (BGR): {enhanced_color}")
    
    # Define the amount to shift the patch to the bottom-right
    shift_x = 10  # Move 10 pixels to the right
    shift_y = 10  # Move 10 pixels down
    
    # Maintain previous bbox for smoothing
    previous_bbox = None
    smoothing_factor = 0.7  # Adjust this to control the smoothing
    
    # Function to smooth bounding box
    def smooth_bbox(current_bbox, previous_bbox):
        if previous_bbox is None:
            return current_bbox  # No previous bbox to smooth with
        return (
            int(smoothing_factor * current_bbox[0] + (1 - smoothing_factor) * previous_bbox[0]),
            int(smoothing_factor * current_bbox[1] + (1 - smoothing_factor) * previous_bbox[1]),
            int(smoothing_factor * current_bbox[2] + (1 - smoothing_factor) * previous_bbox[2]),
            int(smoothing_factor * current_bbox[3] + (1 - smoothing_factor) * previous_bbox[3])
        )
    
    # Process each frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        # Make a copy to show original for comparison
        original = frame.copy()
        
        # Update tracker
        success, bbox = tracker.update(frame)
        
        # Apply smoothing to the bbox
        if success:
            bbox = smooth_bbox(bbox, previous_bbox)
            previous_bbox = bbox  # Update the previous bbox
            
            x, y, w, h = [int(v) for v in bbox]
            
            # Calculate enlarged dimensions for the patch (using size_multiplier)
            enlarged_w = int(w * size_multiplier)
            enlarged_h = int(h * size_multiplier)
            
            # Calculate center of the original box
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Adjust the top-left corner of the enlarged box (shifted)
            enlarged_x = center_x - enlarged_w // 2 + shift_x
            enlarged_y = center_y - enlarged_h // 2 + shift_y
            
            # Create a mask for the clasp with elliptical shape
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            
            # Draw filled ellipse with enlarged dimensions
            center = (center_x, center_y)
            axes = (enlarged_w // 2 + 2, enlarged_h // 2 + 2)  # Slightly larger to ensure coverage
            cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
            
            # Create a copy of the current frame for blending
            blend_frame = frame.copy()
            
            # Apply Gaussian blur to the clasp area for better edge blending (to simulate depth of field)
            blurred_frame = cv2.GaussianBlur(blend_frame, (15, 15), 0)  # Increased blur kernel size
            
            # Create gradient alpha mask for smooth transition
            gradient_mask = np.zeros(mask.shape, dtype=np.float32)
            cv2.ellipse(gradient_mask, center, axes, 0, 0, 360, 1.0, -1)
            gradient_mask = cv2.GaussianBlur(gradient_mask, (21, 21), 5.0)  # Increased blur for smoother edges
            
            # Add metallic silver highlights
            highlight_mask = np.zeros(mask.shape, dtype=np.float32)
            highlight_center = (center[0] - 2, center[1] - 2)  # Slight offset for highlight
            highlight_axes = (int(axes[0] * 0.7), int(axes[1] * 0.7))  # Larger highlight area
            cv2.ellipse(highlight_mask, highlight_center, highlight_axes, 0, 0, 360, 0.5, -1)
            highlight_mask = cv2.GaussianBlur(highlight_mask, (15, 15), 3.0)  # Increased blur for highlight
            
            # Expand dimensions to match frame shape for blending
            gradient_mask_3d = np.expand_dims(gradient_mask, axis=2)
            gradient_mask_3d = np.repeat(gradient_mask_3d, 3, axis=2)
            
            highlight_mask_3d = np.expand_dims(highlight_mask, axis=2)
            highlight_mask_3d = np.repeat(highlight_mask_3d, 3, axis=2)
            
            # Create silver color frames - use both the enhanced color and pure silver for highlights
            color_frame = np.ones_like(frame) * enhanced_color
            highlight_frame = np.ones_like(frame) * silver_color
            
            # Apply blending and reflection to simulate metallic effect and depth
            blended = (1.0 - gradient_mask_3d) * frame + gradient_mask_3d * blurred_frame
            
            frame = blended * (1.0 - highlight_mask_3d) + highlight_frame * highlight_mask_3d
            frame = frame.astype(np.uint8)
            
        else:
            # If tracker fails, estimate position (fallback mechanism)
            pass
        
        # Display comparison
        comparison = np.hstack((original, frame))
        cv2.imshow('Original vs Enlarged Silver Patch', comparison)
        
        # Write processed frame to output video
        if output_path:
            out.write(frame)
        
        # Exit if ESC pressed
        k = cv2.waitKey(100) & 0xff
        if k == 27:
            break
    
    # Clean up
    cap.release()
    if output_path:
        out.release()
    cv2.destroyAllWindows()


# Example usage
if __name__ == "__main__":
    video_path = "videos/video.mp4"  # Replace with your video file
    output_path = "track_video.mp4"
    track_clasp_in_video(video_path, output_path)
