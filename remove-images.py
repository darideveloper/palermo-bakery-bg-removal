"""
Description:
    This script cleans up images in the 'uploads' directory by deleting any files that are 
    NOT listed in a provided CSV file ('products.csv') AND do not contain a specific 
    keyword (e.g., '-scaled') in their filename.

How it works:
    1. Reads 'products.csv' to extract a list of allowed image paths.
    2. Recursively walks through the 'uploads' directory.
    3. Checks if each file's relative path exists in the allowed list or if its filename 
       contains the required keyword.
    4. If neither condition is met, the file is deleted.

Related Folders:
    - Source/Target: ./uploads

Related Scripts:
    - None directly, but typically run as a preliminary cleanup step before background removal.

Recommended Run Order:
    1. remove-images.py (optional: clean up unneeded files first)
    2. remove-no-white-ivory-cakes.py (optional: further filter by cake color)
    3. remove-bg.py (remove backgrounds)

Example Input:
    - 'uploads/2021/02/pink-wedding-cake.jpeg' (not in CSV, no '-scaled' -> deleted)
    - 'uploads/2021/02/cake-scaled.jpeg' (has '-scaled' -> kept)

Example Output:
    --- Cleanup Complete ---
    Files kept: 150
    Files deleted: 500
"""
import os
import csv
import urllib.parse


def get_allowed_paths_from_csv(csv_filepath):
    """
    Parses the CSV and extracts the relative paths of the images
    (e.g., '2021/02/pink-wedding-cake.jpeg').
    """
    allowed_paths = set()

    if not os.path.exists(csv_filepath):
        print(f"Error: CSV file not found at {csv_filepath}")
        return allowed_paths

    try:
        with open(csv_filepath, mode="r", encoding="utf-8") as f:
            # Using DictReader to handle column names automatically
            reader = csv.DictReader(f)
            for row in reader:
                urls_str = row.get("URL", "")
                if not urls_str:
                    continue

                # Split by '|' because some rows have multiple images
                urls = urls_str.split("|")
                for url in urls:
                    # WordPress paths usually start after '/uploads/'
                    if "/uploads/" in url:
                        # Extract everything after /uploads/
                        relative_path = url.split("/uploads/")[-1]
                        # Decode URL characters (e.g., %20 to spaces)
                        relative_path = urllib.parse.unquote(relative_path)
                        # Normalize slashes for your specific OS (Windows vs Mac/Linux)
                        normalized_path = os.path.normpath(relative_path)
                        allowed_paths.add(normalized_path)

    except Exception as e:
        print(f"Error reading CSV: {e}")

    return allowed_paths


def cleanup_images(root_directory, allowed_paths, keyword_to_keep):
    deleted_count = 0
    kept_count = 0

    # os.walk handles all levels of subfolders
    for root, dirs, files in os.walk(root_directory):
        for filename in files:
            full_path = os.path.join(root, filename)

            # Get path relative to the 'uploads' folder
            # e.g., '2021/02/image.jpg'
            rel_path = os.path.relpath(full_path, root_directory)

            # Logic: Keep if it's in the CSV OR if it contains your specific keyword
            is_in_csv = rel_path in allowed_paths
            has_keyword = keyword_to_keep in filename

            if not is_in_csv and not has_keyword:
                try:
                    # --- SAFETY: Un-comment the line below to actually delete ---
                    os.remove(full_path)
                    print(f"Deleted: {rel_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {rel_path}: {e}")
            else:
                kept_count += 1

    print(f"\n--- Cleanup Complete ---")
    print(f"Files kept: {kept_count}")
    print(f"Files deleted: {deleted_count}")


# --- SETUP ---
current_folder = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(current_folder, "products.csv")
target_folder = os.path.join(current_folder, "uploads")
required_keyword = "-scaled"  # We still check for this as a safeguard

# Run the process
allowed = get_allowed_paths_from_csv(csv_file)

if allowed:
    print(f"Found {len(allowed)} unique images in CSV. Starting cleanup...\n")
    cleanup_images(target_folder, allowed, required_keyword)
else:
    print(
        "No images found in CSV. Process aborted to prevent accidental deletion of everything."
    )
