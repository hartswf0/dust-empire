import os
import sys
import glob
import hashlib

CHUNK_SIZE = 50 * 1024 * 1024 # 50 MB
LARGE_FILES = [
    "dust_empire_full.mp4",
    "dust_empire_scored.mp4",
    "dust_empire_music_video.mp4",
    "dust_empire_top.mp4",
    "dust_empire_bot.mp4"
]

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def chunk_file(file_path):
    if not os.path.exists(file_path):
        print(f"Skipping {file_path}: File not found.")
        return

    print(f"Chunking {file_path}...")
    
    # Check if chunks already exist to avoid re-work?
    # Actually safer to re-create to ensure sync.
    
    base_name = os.path.basename(file_path)
    part_num = 0
    
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            
            part_name = f"{base_name}.part{part_num:03d}"
            print(f"  Writing {part_name}...")
            with open(part_name, "wb") as p:
                p.write(chunk)
            part_num += 1
            
    print(f"Finished chunking {file_path} into {part_num} parts.")

def reassemble_file(file_path):
    base_name = os.path.basename(file_path)
    parts = sorted(glob.glob(f"{base_name}.part*"))
    
    if not parts:
        print(f"No parts found for {base_name}")
        return

    print(f"Reassembling {file_path} from {len(parts)} parts...")
    
    with open(file_path, "wb") as outfile:
        for part in parts:
            print(f"  Reading {part}...")
            with open(part, "rb") as infile:
                outfile.write(infile.read())
                
    print(f"Finished reassembling {file_path}.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 file_manager.py [chunk|reassemble]")
        return
        
    action = sys.argv[1]
    
    if action == "chunk":
        for file in LARGE_FILES:
            chunk_file(file)
    elif action == "reassemble":
        for file in LARGE_FILES:
            reassemble_file(file)
    else:
        print("Invalid argument. Use 'chunk' or 'reassemble'.")

if __name__ == "__main__":
    main()
