import os

def rename_frame_files(folder_path):
    # Supported extensions
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.txt'}

    # Check if folder exists
    if not os.path.isdir(folder_path):
        print(f"Invalid folder path: {folder_path}")
        return

    # Process files
    for filename in os.listdir(folder_path):
        name, ext = os.path.splitext(filename)
        if 'frame' in name and ext.lower() in valid_extensions:
            old_path = os.path.join(folder_path, filename)
            new_filename = f"{name}b{ext}"
            new_path = os.path.join(folder_path, new_filename)
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_filename}")

# Example usage:
rename_frame_files("/mnt/d/txleanwork/work files/others/brace")
