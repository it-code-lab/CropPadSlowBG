import os
import subprocess

def process_video(input_path, output_path, crop_top_pixels, bg_music_path):
    # Get original width and height
    probe_cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=s=x:p=0', input_path
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    width, height = map(int, result.stdout.strip().split('x'))

    # Calculate new height and padding
    cropped_height = height - crop_top_pixels
    pad_top = (height - cropped_height) // 2  # center vertically

    # Build filter string
    filter_str = (
        f"crop={width}:{cropped_height}:0:{crop_top_pixels},"
        f"pad={width}:{height}:0:{pad_top},"
        f"setpts=2.0*PTS"  # slow down video by 2x
    )

    # Adjust background music to match video duration
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-i', bg_music_path,
        '-filter:v', filter_str,
        '-map', '0:v:0',        # use processed video only
        '-map', '1:a:0',        # use background music audio
        '-shortest',            # cut audio if video ends first
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        output_path
    ]

    subprocess.run(ffmpeg_cmd)
    print(f"Processed: {output_path}")

def batch_process(folder_path, crop_top_pixels=50, bg_music_path="sitar.mp3"):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".mp4") and not filename.startswith("cropped_"):
            input_path = os.path.join(folder_path, filename)
            output_path = os.path.join(folder_path, f"cropped_{filename}")
            process_video(input_path, output_path, crop_top_pixels, bg_music_path)

# 🔁 Run for current folder
batch_process(".", crop_top_pixels=50, bg_music_path="sitar.mp3")
