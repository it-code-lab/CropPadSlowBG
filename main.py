import os
import subprocess
import random
import shutil

def get_random_music(bg_music_folder):
    music_files = [
        os.path.join(bg_music_folder, f)
        for f in os.listdir(bg_music_folder)
        if f.lower().endswith(('.mp3', '.wav', '.aac'))
    ]
    return random.choice(music_files) if music_files else None

def process_video(input_path, output_path, crop_top_pixels, bg_music_path):
    # Get original video resolution
    probe_cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=s=x:p=0', input_path
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    width, height = map(int, result.stdout.strip().split('x'))

    cropped_height = height - crop_top_pixels
    pad_top = (height - cropped_height) // 2

    filter_str = (
        f"crop={width}:{cropped_height}:0:{crop_top_pixels},"
        f"pad={width}:{height}:0:{pad_top},"
        f"setpts=2.0*PTS"
    )

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-i', bg_music_path,
        '-filter:v', filter_str,
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-c:a', 'aac',
        '-b:a', '192k',
        output_path
    ]
    subprocess.run(ffmpeg_cmd)
    print(f"✅ Processed: {os.path.basename(output_path)}")

def clear_folder(folder_path, extensions=None):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)
        if os.path.isfile(full_path):
            if not extensions or file.lower().endswith(extensions):
                os.remove(full_path)

def batch_process(input_folder='input', output_folder='output', bg_music_folder='god_bg', crop_top_pixels=50):
    # Clear output folder before processing
    clear_folder(output_folder)

    # Process videos
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".mp4"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"{filename}")
            bg_music = get_random_music(bg_music_folder)

            if bg_music:
                process_video(input_path, output_path, crop_top_pixels, bg_music)
                os.remove(input_path)  # delete input file after processing
            else:
                print("❌ No background music found in god_bg folder.")
                break

# Run the batch processor
batch_process()
