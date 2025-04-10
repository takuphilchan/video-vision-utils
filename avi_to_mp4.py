from pathlib import Path
import subprocess

def convert_avi_to_mp4(input_file, output_file):
    command = ['ffmpeg', '-i', str(input_file), str(output_file)]
    try:
        subprocess.run(command, check=True)
        print(f"Conversion successful! The file is saved as {output_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

# Relative to the script's location
base_dir = Path('runs/detect/predict4')
input_file = base_dir / 'vid.avi'
output_file = base_dir / 'vid.mp4'

convert_avi_to_mp4(input_file, output_file)
