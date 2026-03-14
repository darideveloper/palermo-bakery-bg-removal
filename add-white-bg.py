import os
import sqlite3
import time
from pathlib import Path
from PIL import Image
from tqdm import tqdm

# --- CONFIGURATION ---
CURRENT_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = CURRENT_PATH / "uploads"  # Original files (to check extensions)
NO_BG_DIR = CURRENT_PATH / "uploads-no-bg"  # Transparent PNGs
FINAL_DIR = CURRENT_PATH / "uploads-no-bg-done"  # Result: White BG + Original Extension
DB_NAME = "finalizing_status.db"


def init_db():
    tqdm.write(f"DEBUG: Connecting to database {DB_NAME}...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS finalized_files (
            file_path TEXT PRIMARY KEY,
            status TEXT
        )
    """
    )
    conn.commit()
    return conn


def is_finalized(conn, file_path):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status FROM finalized_files WHERE file_path = ?", (str(file_path),)
    )
    return cursor.fetchone() is not None


def mark_as_finalized(conn, file_path):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO finalized_files (file_path, status) VALUES (?, ?)",
        (str(file_path), "completed"),
    )
    conn.commit()


def run_finalizer():
    print("--- 🎨 Starting White Background Restoration ---")
    db_conn = init_db()

    # 1. Scan the NO_BG_DIR for work to do
    print(f"🔍 Scanning: {NO_BG_DIR}")
    all_tasks = []

    if not NO_BG_DIR.exists():
        print(
            f"❌ ERROR: Directory '{NO_BG_DIR}' not found. Run the removal script first."
        )
        return

    for root, _, files in os.walk(NO_BG_DIR):
        for file in files:
            if file.lower().endswith(".png"):
                no_bg_path = Path(root) / file
                if not is_finalized(db_conn, no_bg_path):
                    all_tasks.append(no_bg_path)

    if not all_tasks:
        print("✨ Everything is already finalized!")
        return

    # 2. Process
    pbar = tqdm(all_tasks, desc="Finalizing", unit="img")

    for no_bg_path in pbar:
        try:
            start_time = time.time()

            # Replicate path structure
            relative_path = no_bg_path.relative_to(NO_BG_DIR)

            # --- EXTENSION LOGIC ---
            # Find the original file in SOURCE_DIR to match the extension
            original_file_base = SOURCE_DIR / relative_path.with_suffix("")

            # Search for any file with the same name but different extension
            original_matches = list(
                original_file_base.parent.glob(f"{original_file_base.name}.*")
            )

            if not original_matches:
                tqdm.write(f"⚠️ Skipping: Could not find original for {relative_path}")
                continue

            # Take the first match and get its extension
            original_ext = original_matches[0].suffix
            output_path = FINAL_DIR / relative_path.with_suffix(original_ext)

            # Create subfolders
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # --- IMAGE EDITING ---
            tqdm.write(
                f"🖌️ Adding white BG: {relative_path.name} -> {output_path.suffix}"
            )

            foreground = Image.open(no_bg_path).convert("RGBA")
            # Create a white background of the same size
            background = Image.new("RGBA", foreground.size, (255, 255, 255, 255))

            # Composite foreground onto white background
            final_img = Image.alpha_composite(background, foreground)

            # Convert to RGB (required for JPG) or keep RGBA based on target
            if output_path.suffix.lower() in [".jpg", ".jpeg"]:
                final_img = final_img.convert("RGB")

            final_img.save(output_path)

            mark_as_finalized(db_conn, no_bg_path)
            tqdm.write(
                f"✅ Success: {output_path.name} ({time.time() - start_time:.2f}s)"
            )

        except Exception as e:
            tqdm.write(f"❌ FAILED: {no_bg_path.name} | Error: {e}")


run_finalizer()
