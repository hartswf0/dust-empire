import os
import subprocess
import glob

VIDEO_DIR = "/Users/gaia/HOUSEINADIS/LUCY VIDS"
OUTPUT_DIR = "/Users/gaia/HOUSEINADIS"
CONCAT_OUTPUT = os.path.join(OUTPUT_DIR, "dust_empire_full.mp4")
MOSAIC_OUTPUT = os.path.join(OUTPUT_DIR, "dust_empire_mosaic.mp4")

def get_video_files():
    # Get all mp4 files and sort them to ensure consistent order
    files = sorted(glob.glob(os.path.join(VIDEO_DIR, "*.mp4")))
    return files

def create_concat_list(files):
    list_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(list_path, "w") as f:
        for file in files:
            f.write(f"file '{file}'\n")
    return list_path

def concatenate_videos(list_path):
    print("Concatenating videos...")
    # ffmpeg command to concatenate
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        "-y", # Overwrite output
        CONCAT_OUTPUT
    ]
    subprocess.run(cmd, check=True)
    print(f"Concatenation complete: {CONCAT_OUTPUT}")

def create_mosaic(files):
    print("Creating video mosaic...")
    # We need exactly 12 videos for a 4x3 grid
    if len(files) < 12:
        print("Not enough videos for a 4x3 mosaic (need 12). Using what we have.")
        # Logic to handle fewer videos could be added, but for now we assume 12 or use blank inputs
    
    # Construct complex filtergraph
    # Scale all inputs to a common size (e.g., 320x240 for a manageably sized output)
    # 4 columns x 3 rows
    
    inputs = []
    filter_complex = ""
    
    # We'll use the first 12 files
    mosaic_files = files[:12]
    
    for i, file in enumerate(mosaic_files):
        inputs.extend(["-i", file])
        filter_complex += f"[{i}:v]scale=320:240[v{i}];"
    
    # xstack layout
    # 0 1 2 3
    # 4 5 6 7
    # 8 9 10 11
    
    filter_complex += (
        "[v0][v1][v2][v3]"
        "[v4][v5][v6][v7]"
        "[v8][v9][v10][v11]"
        "xstack=inputs=12:layout="
        "0_0|w0_0|w0+w1_0|w0+w1+w2_0|"
        "0_h0|w4_h0|w4+w5_h0|w4+w5+w6_h0|"
        "0_h0+h4|w8_h0+h4|w8+w9_h0+h4|w8+w9+w10_h0+h4"
        "[v]"
    )
    
    cmd = [
        "ffmpeg",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast", # Use fast preset for speed
        "-y",
        MOSAIC_OUTPUT
    ]
    
    subprocess.run(cmd, check=True)
    print(f"Mosaic complete: {MOSAIC_OUTPUT}")

def main():
    files = get_video_files()
    if not files:
        print("No video files found in " + VIDEO_DIR)
        return

    print(f"Found {len(files)} video files.")

    # 1. Concatenation
    # list_path = create_concat_list(files)
    # concatenate_videos(list_path)
    
    # 2. Basic Mosaic
    # if len(files) >= 12:
    #      create_mosaic(files)

    # 3. Phase 2: Split and Advanced Mosaic
    split_files = split_videos_top_bot(files)
    
    if len(split_files) >= 24:
        create_advanced_mosaic(split_files)
        create_vertical_strip(split_files)
        generate_metadata(split_files)
    else:
        print("Not enough split files for advanced mosaic.")

def split_videos_top_bot(files):
    print("Splitting videos into Top and Bottom halves...")
    split_files = []
    
    for file in files:
        base_name = os.path.splitext(os.path.basename(file))[0]
        top_name = os.path.join(OUTPUT_DIR, f"{base_name}_top.mp4")
        bot_name = os.path.join(OUTPUT_DIR, f"{base_name}_bot.mp4")
        
        # Crop Top: width=iw, height=ih/2, x=0, y=0
        cmd_top = [
            "ffmpeg", "-i", file,
            "-filter:v", "crop=iw:ih/2:0:0",
            "-c:v", "libx264", "-crf", "23", "-preset", "fast",
            "-an", "-y", # Remove audio for splits to simplify tiling
            top_name
        ]
        
        # Crop Bottom: width=iw, height=ih/2, x=0, y=ih/2
        cmd_bot = [
            "ffmpeg", "-i", file,
            "-filter:v", "crop=iw:ih/2:0:ih/2",
            "-c:v", "libx264", "-crf", "23", "-preset", "fast",
            "-an", "-y",
            bot_name
        ]
        
        # Run commands if files don't exist or to overwrite
        print(f"Processing {base_name}...")
        # Check if files exist to save time on re-runs, or overwrite based on flag?
        # For now, let's assume we want to ensure they exist.
        if not os.path.exists(top_name):
             subprocess.run(cmd_top, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not os.path.exists(bot_name):
             subprocess.run(cmd_bot, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        split_files.append(top_name)
        split_files.append(bot_name)
        
    return split_files

def create_advanced_mosaic(files):
    output_file = os.path.join(OUTPUT_DIR, "dust_empire_split_mosaic.mp4")
    print(f"Creating 24-panel advanced mosaic: {output_file}")
    
    # Needs 24 inputs
    # Grid: 6 columns x 4 rows
    # Layout:
    # 0  1  2  3  4  5
    # 6  7  8  9  10 11
    # 12 13 14 15 16 17
    # 18 19 20 21 22 23
    
    inputs = []
    filter_complex = ""
    
    # Use first 24 files
    mosaic_files = files[:24]
    
    for i, file in enumerate(mosaic_files):
        inputs.extend(["-i", file])
        # Scale down for grid - keeping aspect ratio (which is now different because of crop)
        # Original was 1280x1440 (8:9) -> Split is 1280x720 (16:9)
        # Scale to 320x180
        filter_complex += f"[{i}:v]scale=320:180[v{i}];"

    # xstack layout for 6x4
    # Columns: 6
    layout = ""
    
    # Row 0
    layout += "0_0|w0_0|w0+w1_0|w0+w1+w2_0|w0+w1+w2+w3_0|w0+w1+w2+w3+w4_0|"
    # Row 1 (h0)
    layout += "0_h0|w6_h0|w6+w7_h0|w6+w7+w8_h0|w6+w7+w8+w9_h0|w6+w7+w8+w9+w10_h0|"
    # Row 2 (h0+h6)
    layout += "0_h0+h6|w12_h0+h6|w12+w13_h0+h6|w12+w13+w14_h0+h6|w12+w13+w14+w15_h0+h6|w12+w13+w14+w15+w16_h0+h6|"
    # Row 3 (h0+h6+h12)
    layout += "0_h0+h6+h12|w18_h0+h6+h12|w18+w19_h0+h6+h12|w18+w19+w20_h0+h6+h12|w18+w19+w20+w21_h0+h6+h12|w18+w19+w20+w21+w22_h0+h6+h12"

    filter_complex += "".join([f"[v{i}]" for i in range(24)])
    filter_complex += f"xstack=inputs=24:layout={layout}[v]"
    
    cmd = [
        "ffmpeg",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-y",
        output_file
    ]
    subprocess.run(cmd, check=True)
    print("Advanced mosaic complete.")

def create_vertical_strip(files):
    output_file = os.path.join(OUTPUT_DIR, "dust_empire_vertical_strip.mp4")
    print(f"Creating vertical video strip: {output_file}")
    
    inputs = []
    filter_complex = ""
    mosaic_files = files[:24]
    
    for i, file in enumerate(mosaic_files):
        inputs.extend(["-i", file])
        filter_complex += f"[{i}:v]scale=320:180[v{i}];"
        
    filter_complex += "".join([f"[v{i}]" for i in range(24)])
    filter_complex += f"vstack=inputs=24[v]"
    
    cmd = [
        "ffmpeg",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-y",
        output_file
    ]
    
    subprocess.run(cmd, check=True)
    print("Vertical strip complete.")

def generate_metadata(files):
    print("Generating metadata for mobile interface...")
    import json
    
    clips = []
    
    # 1. Source Clips (LUCY VIDS)
    source_files = sorted(glob.glob(os.path.join(VIDEO_DIR, "*.mp4")))
    for file in source_files:
        clips.append({
            "filename": os.path.basename(file),
            "path": file,
            "type": "source",
            "download_url": os.path.join("LUCY VIDS", os.path.basename(file))
        })
        
    # 2. Extra (music videos)
    extra_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "music", "*.mp4")))
    for file in extra_files:
        clips.append({
            "filename": os.path.basename(file),
            "path": file,
            "type": "extra",
            "download_url": os.path.join("music", os.path.basename(file))
        })

    # 3. Split Clips (Top/Bottom) - using files passed in argument which are top/bot splits
    # Or rescan to be safe
    split_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "*_top.mp4")) + glob.glob(os.path.join(OUTPUT_DIR, "*_bot.mp4")))
    # Filter out the main "dust_empire" ones which are films
    split_files = [f for f in split_files if "dust_empire" not in os.path.basename(f)]
    
    for file in split_files:
        basename = os.path.basename(file)
        segment_type = "top" if "_top.mp4" in basename else "bottom"
        clips.append({
            "filename": basename,
            "path": file,
            "type": segment_type,
            "download_url": basename
        })

    # 4. Films (Full length)
    films = [
        "dust_empire_full.mp4",
        "dust_empire_top.mp4",
        "dust_empire_bot.mp4",
        "dust_empire_split_mosaic.mp4", 
        "dust_empire_music_video.mp4"
    ]
    
    for film in films:
        film_path = os.path.join(OUTPUT_DIR, film)
        if os.path.exists(film_path):
            clips.append({
                "filename": film,
                "path": film_path,
                "type": "film",
                "download_url": film
            })
        
    js_content = f"const CLIPS = {json.dumps(clips, indent=2)};"
    
    with open(os.path.join(OUTPUT_DIR, "clips.js"), "w") as f:
        f.write(js_content)
    print(f"Metadata written to clips.js ({len(clips)} items)")

if __name__ == "__main__":
    main()
