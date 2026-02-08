import os
import subprocess
import glob

BASE_DIR = "/Users/gaia/HOUSEINADIS"
MUSIC_DIR = os.path.join(BASE_DIR, "music")
VIDEO_FILE = os.path.join(BASE_DIR, "dust_empire_full.mp4")
OUTPUT_FILE = os.path.join(BASE_DIR, "dust_empire_scored.mp4")
TEMP_LIST = os.path.join(BASE_DIR, "music_list.txt")
TEMP_AUDIO = os.path.join(BASE_DIR, "combined_audio.mp3")

def get_audio_files():
    # Identify files
    all_files = glob.glob(os.path.join(MUSIC_DIR, "*"))
    
    # Separate the specific mp3 requested to be first
    first_track_name = "a985c149-b352-4584-b5e4-e94b9a47ccb8.mp3"
    first_track = None
    other_tracks = []
    
    for f in all_files:
        if os.path.basename(f) == first_track_name:
            first_track = f
        else:
            other_tracks.append(f)
            
    other_tracks.sort() # Consistent order
    
    final_list = []
    if first_track:
        final_list.append(first_track)
    final_list.extend(other_tracks)
    
    return final_list

def prepare_audio_concat(files):
    print("Preparing audio concat list...")
    processed_files = []
    
    for i, file in enumerate(files):
        ext = os.path.splitext(file)[1].lower()
        if ext == ".mp4":
            # Extract audio from mp4
            temp_audio = os.path.join(BASE_DIR, f"temp_audio_{i}.mp3")
            print(f"Extracting audio from {os.path.basename(file)}...")
            subprocess.run([
                "ffmpeg", "-i", file, "-vn", "-acodec", "libmp3lame", "-y", temp_audio
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            processed_files.append(temp_audio)
        else:
            processed_files.append(file)

    with open(TEMP_LIST, "w") as f:
        for file in processed_files:
            f.write(f"file '{file}'\n")
            
    return processed_files # Return list to clean up later if needed

def combine_and_merge():
    # 1. Concatenate all audio into one file
    print("Concatenating all audio tracks...")
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", TEMP_LIST,
        "-c", "copy", "-y", TEMP_AUDIO
    ], check=True)
    
    # 2. Merge with video, looping the audio
    print(f"Merging audio with video: {VIDEO_FILE}")
    # -stream_loop -1 loops the input infinitely
    # -shortest stops when the shortest input (the video in this case, since audio is infinite) ends
    # We map 0:v (video from file 0) and 1:a (audio from file 1 - the looped audio)
    
    cmd = [
        "ffmpeg",
        "-i", VIDEO_FILE,
        "-stream_loop", "-1", "-i", TEMP_AUDIO,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", # Copy video stream without re-encoding
        "-c:a", "aac",  # Re-encode audio to aac for mp4 compatibility
        "-shortest",    # Stop when video ends
        "-y",
        OUTPUT_FILE
    ]
    
    subprocess.run(cmd, check=True)
    print(f"Scored video created: {OUTPUT_FILE}")

def main():
    if not os.path.exists(VIDEO_FILE):
        print(f"Error: Main video file not found: {VIDEO_FILE}")
        return

    files = get_audio_files()
    if not files:
        print("No music files found.")
        return
        
    print(f"Found {len(files)} audio sources.")
    
    # Create temp files and list
    prepare_audio_concat(files)
    
    # Combine and merge
    combine_and_merge()
    
    # Cleanup temp audio? Keeping for now or could delete
    # if os.path.exists(TEMP_AUDIO): os.remove(TEMP_AUDIO)

if __name__ == "__main__":
    main()
