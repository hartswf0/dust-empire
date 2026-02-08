import os
import subprocess

BASE_DIR = "/Users/gaia/HOUSEINADIS"
VIDEO_FILE = os.path.join(BASE_DIR, "dust_empire_full.mp4")
AUDIO_FILE = os.path.join(BASE_DIR, "music", "1755d990-c90e-4d30-929a-17c7fce1522c.mp3")
OUTPUT_FILE = os.path.join(BASE_DIR, "dust_empire_scored.mp4")

def update_soundtrack():
    if not os.path.exists(VIDEO_FILE):
        print(f"Error: Video file not found: {VIDEO_FILE}")
        return
        
    if not os.path.exists(AUDIO_FILE):
        print(f"Error: Audio file not found: {AUDIO_FILE}")
        return

    print(f"Updating soundtrack for {VIDEO_FILE}...")
    print(f"Using audio: {AUDIO_FILE}")
    
    # Loop audio to match video length
    cmd = [
        "ffmpeg",
        "-i", VIDEO_FILE,
        "-stream_loop", "-1", "-i", AUDIO_FILE,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", 
        "-c:a", "aac",
        "-shortest",
        "-y",
        OUTPUT_FILE
    ]
    
    subprocess.run(cmd, check=True)
    print(f"Updated scored video created: {OUTPUT_FILE}")

if __name__ == "__main__":
    update_soundtrack()
