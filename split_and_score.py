import os
import subprocess

BASE_DIR = "/Users/gaia/HOUSEINADIS"
FULL_VIDEO = os.path.join(BASE_DIR, "dust_empire_full.mp4")
AUDIO_FILE = os.path.join(BASE_DIR, "music/1755d990-c90e-4d30-929a-17c7fce1522c.mp3")

OUTPUT_TOP = os.path.join(BASE_DIR, "dust_empire_top.mp4")
OUTPUT_BOT = os.path.join(BASE_DIR, "dust_empire_bot.mp4")

def split_and_score():
    if not os.path.exists(FULL_VIDEO):
        print(f"Error: {FULL_VIDEO} not found.")
        return
    if not os.path.exists(AUDIO_FILE):
        print(f"Error: {AUDIO_FILE} not found.")
        return

    # Dimensions: 1280x1440. Split at 720.
    
    # 1. Top Half
    print(f"Generating Top Half ({OUTPUT_TOP})...")
    # crop=1280:720:0:0
    cmd_top = [
        "ffmpeg", "-y",
        "-i", FULL_VIDEO,
        "-stream_loop", "-1", "-i", AUDIO_FILE,
        "-filter_complex", "[0:v]crop=1280:720:0:0[top]",
        "-map", "[top]", "-map", "1:a",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac",
        "-shortest",
        OUTPUT_TOP
    ]
    subprocess.run(cmd_top, check=True)
    print("Top half created.")

    # 2. Bottom Half
    print(f"Generating Bottom Half ({OUTPUT_BOT})...")
    # crop=1280:720:0:720
    cmd_bot = [
        "ffmpeg", "-y",
        "-i", FULL_VIDEO,
        "-stream_loop", "-1", "-i", AUDIO_FILE,
        "-filter_complex", "[0:v]crop=1280:720:0:720[bot]",
        "-map", "[bot]", "-map", "1:a",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac",
        "-shortest",
        OUTPUT_BOT
    ]
    subprocess.run(cmd_bot, check=True)
    print("Bottom half created.")

if __name__ == "__main__":
    split_and_score()
