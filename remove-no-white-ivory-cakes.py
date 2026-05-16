"""
Description:
    This script recursively scans the 'uploads' directory and deletes any images 
    whose filenames do NOT contain the words "white" or "ivory" (case-insensitive).

How it works:
    1. Recursively walks through the 'uploads' directory.
    2. Converts each filename to lowercase.
    3. Checks if "white" or "ivory" is in the lowercase filename.
    4. Deletes the file if neither word is found.

Related Folders:
    - Source/Target: ./uploads

Related Scripts:
    - remove-images.py (another cleanup script)

Recommended Run Order:
    - Run this before background removal to save processing time.
    1. remove-images.py (optional)
    2. remove-no-white-ivory-cakes.py
    3. remove-bg.py

Example Input:
    - 'uploads/2021/pink-cake.jpg' (deleted)
    - 'uploads/2021/white-wedding-cake.jpg' (kept)

Example Output:
    Starting cleanup in: .../uploads
    Deleted: 2021/pink-cake.jpg
    --- Cleanup Complete ---
    Files kept (white/ivory): 208
    Files deleted: 906
"""
import os

# Add partial filenames to this list to always keep them (case-insensitive)
EXCEPTIONS = [
    "11ExquisiteWhiteWeddingCake",
    "Screen-Shot-2022-07-11-at-10.54.25-PM",
]

def cleanup_non_white_ivory_images(root_directory):
    deleted_count = 0
    kept_count = 0

    if not os.path.exists(root_directory):
        print(f"Error: Directory not found at {root_directory}")
        return

    # os.walk handles all levels of subfolders
    for root, dirs, files in os.walk(root_directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, root_directory)
            
            filename_lower = filename.lower()
            
            # Check if filename matches any of the exceptions
            is_exception = any(exc.lower() in filename_lower for exc in EXCEPTIONS)
            
            # Keep if the filename contains "white" or "ivory", or matches an exception
            if "white" in filename_lower or "ivory" in filename_lower or is_exception:
                kept_count += 1
            else:
                try:
                    os.remove(full_path)
                    print(f"Deleted: {rel_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {rel_path}: {e}")

    print(f"\n--- Cleanup Complete ---")
    print(f"Files kept (white/ivory): {kept_count}")
    print(f"Files deleted: {deleted_count}")

if __name__ == "__main__":
    current_folder = os.path.dirname(os.path.abspath(__file__))
    target_folder = os.path.join(current_folder, "uploads")
    
    print(f"Starting cleanup in: {target_folder}\n")
    cleanup_non_white_ivory_images(target_folder)
