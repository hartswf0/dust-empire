import os
import subprocess

BASE_DIR = "/Users/gaia/HOUSEINADIS"
MUSIC_DIR = os.path.join(BASE_DIR, "music")
# 1755d990-c90e-4d30-929a-17c7fce1522c.mp3
AUDIO_FILE = os.path.join(MUSIC_DIR, "1755d990-c90e-4d30-929a-17c7fce1522c.mp3") 
OUTPUT_FILE = os.path.join(BASE_DIR, "dust_empire_music_video.mp4")
TEMP_VISUALS_LIST = os.path.join(BASE_DIR, "music_video_list.txt")
TEMP_VISUALS_CONCAT = os.path.join(BASE_DIR, "temp_visuals_concat.mp4")

# Specific video files requested
VIDEO_FILES = [
    "video_3a6832c332984f9aaa65c3c91ebfd3b7.mp4",
    "video_3ed81904e25d462ca3d7bf6fd0d7232d.mp4",
    "video_56c60a8a29464d2e8035476c4f5f4942.mp4"
]

def get_visual_files():
    files = []
    for vf in VIDEO_FILES:
        full_path = os.path.join(MUSIC_DIR, vf)
        if os.path.exists(full_path):
            files.append(full_path)
        else:
            print(f"Warning: Specific video file not found: {full_path}")
    return files

def create_concat_list(files):
    with open(TEMP_VISUALS_LIST, "w") as f:
        for file in files:
            f.write(f"file '{file}'\n")
            
def create_music_video():
    files = get_visual_files()
    if not files:
        print("No video files found.")
        return

    print(f"Found {len(files)} video clips for music video.")

    # 1. Create list
    create_concat_list(files)
    
    # 2. Concatenate visuals into one file
    print("Concatenating visual clips...")
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", TEMP_VISUALS_LIST,
        "-c", "copy", "-an", "-y", TEMP_VISUALS_CONCAT
    ], check=True)
    
    if not os.path.exists(AUDIO_FILE):
        print(f"Error: Audio file {AUDIO_FILE} not found.")
        return

    print("Merging looped visuals with specific soundtrack...")
    print(f"Using audio: {AUDIO_FILE}")
    
    # Loop visuals to match audio duration
    cmd = [
        "ffmpeg",
        "-stream_loop", "-1", "-i", TEMP_VISUALS_CONCAT,
        "-i", AUDIO_FILE,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        "-y",
        OUTPUT_FILE
    ]
    
    subprocess.run(cmd, check=True)
    print(f"Music Video created: {OUTPUT_FILE}")
    
    # Cleanup
    if os.path.exists(TEMP_VISUALS_CONCAT): os.remove(TEMP_VISUALS_CONCAT)
    if os.path.exists(TEMP_VISUALS_LIST): os.remove(TEMP_VISUALS_LIST)

if __name__ == "__main__":
    create_music_video()
