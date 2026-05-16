"""
Description:
    This script cleans up filenames by removing the '-scaled' suffix from images 
    in the 'uploads-no-bg-done' directory and saves the renamed files to a new 
    directory ('uploads-no-bg-done-no-scaled').

How it works:
    1. Scans 'uploads-no-bg-done' for files whose names end with '-scaled' before the extension.
    2. Uses an SQLite database ('renaming_status.db') to track processed files.
    3. Copies the file to 'uploads-no-bg-done-no-scaled' with the '-scaled' suffix removed.
    4. Replicates the folder structure.

Related Folders:
    - Source: ./uploads-no-bg-done
    - Output: ./uploads-no-bg-done-no-scaled
    - DB: renaming_status.db

Related Scripts:
    - add-white-bg.py (typically run before this script to generate the finalized images)

Recommended Run Order:
    1. remove-bg.py
    2. add-white-bg.py
    3. remove-scaled-suffix.py (This script)

Example Input:
    - 'uploads-no-bg-done/2026/05/cake-scaled.jpg'

Example Output:
    - 'uploads-no-bg-done-no-scaled/2026/05/cake.jpg'
"""
import os
import sqlite3
import shutil
from pathlib import Path
from tqdm import tqdm

# --- CONFIGURATION ---
CURRENT_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = CURRENT_PATH / "uploads-no-bg-done"
OUTPUT_DIR = CURRENT_PATH / "uploads-no-bg-done-no-scaled"
DB_NAME = "renaming_status.db"

def init_db():
    """Initializes the SQLite database for tracking processed files."""
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
    """Checks if a file has already been processed."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status FROM processed_files WHERE file_path = ?", (str(file_path),)
    )
    result = cursor.fetchone()
    return result is not None and result[0] == "completed"

def mark_as_done(conn, file_path):
    """Marks a file as processed in the database."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO processed_files (file_path, status) VALUES (?, ?)",
        (str(file_path), "completed"),
    )
    conn.commit()

def run_renamer():
    print("--- 🏷️ Starting Scaled Suffix Removal Script ---")

    # 1. Initialize
    db_conn = init_db()

    if not SOURCE_DIR.exists():
        print(f"❌ ERROR: Source directory '{SOURCE_DIR}' does not exist.")
        return

    # 2. Scan Phase
    print(f"🔍 Scanning: {SOURCE_DIR}")
    all_tasks = []

    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            input_path = Path(root) / file
            
            # Identify files with -scaled suffix before extension
            # e.g., image-scaled.jpeg -> stem is 'image-scaled', suffix is '.jpeg'
            if input_path.stem.lower().endswith("-scaled"):
                if not is_processed(db_conn, input_path):
                    all_tasks.append(input_path)

    total_files = len(all_tasks)
    if total_files == 0:
        print("✨ Status: No files with '-scaled' suffix found or already processed!")
        return

    print(f"📦 Queue: {total_files} files scheduled for renaming.")

    # 3. Processing Phase
    pbar = tqdm(all_tasks, desc="Renaming", unit="img")

    for input_path in pbar:
        try:
            # Replicate path structure
            relative_path = input_path.relative_to(SOURCE_DIR)
            
            # Remove '-scaled' from the stem
            # stem: 'image-scaled' -> new_stem: 'image'
            new_stem = input_path.stem[:-7] # len("-scaled") == 7
            new_filename = new_stem + input_path.suffix
            
            output_path = OUTPUT_DIR / relative_path.parent / new_filename

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy and Rename
            shutil.copy2(input_path, output_path)

            # Record success
            mark_as_done(db_conn, input_path)
            
            # tqdm.write(f"✅ Renamed: {relative_path.name} -> {new_filename}")

        except Exception as e:
            tqdm.write(f"❌ FAILED: {input_path} | Error: {e}")
            continue

    db_conn.close()
    print("\n--- ✅ All tasks finished ---")

if __name__ == "__main__":
    run_renamer()
