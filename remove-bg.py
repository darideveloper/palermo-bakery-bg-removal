"""
Description:
    This script processes images in the 'uploads' directory, removes their background 
    using an AI model (InSPyReNet), and saves the transparent images as PNGs in 
    the 'uploads-no-bg' directory.

How it works:
    1. Uses an SQLite database ('processing_status.db') to track completed files, 
       allowing resumption if interrupted.
    2. Scans the 'uploads' directory for supported images (.jpg, .jpeg, .png, .webp).
    3. Uses the `transparent_background` library to remove backgrounds.
    4. Saves the results as .png files in the 'uploads-no-bg' directory, 
       replicating the original subfolder structure.

Related Folders:
    - Source: ./uploads
    - Output: ./uploads-no-bg
    - DB: processing_status.db

Related Scripts:
    - add-white-bg.py (runs after this script to add a white background to the transparent PNGs)

Recommended Run Order:
    1. Clean up scripts (remove-images.py, remove-no-white-ivory-cakes.py)
    2. remove-bg.py (This script)
    3. add-white-bg.py
    4. remove-scaled-suffix.py

Example Input:
    - 'uploads/2026/05/cake.jpg' (original image with background)

Example Output:
    - 'uploads-no-bg/2026/05/cake.png' (transparent background image)
"""
import os
import sqlite3
import time
from pathlib import Path
from transparent_background import Remover
from PIL import Image
from tqdm import tqdm

# --- CONFIGURATION ---
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
# Note: Using Path objects for better cross-platform compatibility
SOURCE_DIR = Path(CURRENT_PATH) / "uploads"
OUTPUT_DIR = Path(CURRENT_PATH) / "uploads-no-bg"
DB_NAME = "processing_status.db"
VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def init_db():
    print(f"DEBUG: Connecting to database {DB_NAME}...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_files (
            file_path TEXT PRIMARY KEY,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    return conn


def is_processed(conn, file_path):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status FROM processed_files WHERE file_path = ?", (str(file_path),)
    )
    result = cursor.fetchone()
    return result is not None and result[0] == "completed"


def mark_as_done(conn, file_path):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO processed_files (file_path, status) VALUES (?, ?)",
        (str(file_path), "completed"),
    )
    conn.commit()


def run_processor():
    print("--- 🚀 Starting Background Removal Pipeline ---")

    # 1. Initialize
    db_conn = init_db()
    print("DEBUG: Loading AI Model (InSPyReNet)... this may take a moment.")
    remover = Remover()
    print("DEBUG: Model loaded successfully.")

    # 2. Scan Phase
    print(f"🔍 Scanning: {SOURCE_DIR}")
    all_tasks = []

    if not SOURCE_DIR.exists():
        print(f"❌ ERROR: Source directory '{SOURCE_DIR}' does not exist.")
        return

    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith(VALID_EXTENSIONS):
                input_path = Path(root) / file
                if not is_processed(db_conn, input_path):
                    all_tasks.append(input_path)
                else:
                    # Optional: uncomment for verbose skipped files
                    # print(f"INFO: Skipping {file} (already processed)")
                    pass

    total_files = len(all_tasks)
    if total_files == 0:
        print("✨ Status: Everything is already up to date!")
        return

    print(f"📦 Queue: {total_files} files scheduled for conversion.")

    # 3. Conversion Phase
    # tqdm is wrapped around the loop, but we use tqdm.write for logs to prevent breaking the bar
    pbar = tqdm(all_tasks, desc="Processing", unit="img")

    for input_path in pbar:
        try:
            start_time = time.time()

            # Replicate path structure
            relative_path = input_path.relative_to(SOURCE_DIR)
            output_path = OUTPUT_DIR / relative_path.with_suffix(".png")

            # Debug: Directory creation
            if not output_path.parent.exists():
                tqdm.write(f"DEBUG: Creating directory {output_path.parent}")
                output_path.parent.mkdir(parents=True, exist_ok=True)

            tqdm.write(f"⏳ Processing: {relative_path}")

            # Process Image
            img = Image.open(input_path).convert("RGB")
            out = remover.process(img, type="rgba")
            out.save(output_path)

            # Record success
            mark_as_done(db_conn, input_path)

            elapsed = time.time() - start_time
            tqdm.write(f"✅ Saved: {output_path} ({elapsed:.2f}s)")

        except Exception as e:
            tqdm.write(f"❌ FAILED: {input_path} | Error: {e}")
            continue

    db_conn.close()
    print("\n--- ✅ All tasks finished ---")


if __name__ == "__main__":
    run_processor()
