import os

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
            
            # Keep if the filename contains "white" or "ivory"
            if "white" in filename_lower or "ivory" in filename_lower:
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
