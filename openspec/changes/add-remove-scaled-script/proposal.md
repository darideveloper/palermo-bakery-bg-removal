# Change: Add Scaled Suffix Removal Script

## Why
Some images in the `uploads-no-bg-done/` directory have invalid filenames ending with `-scaled` (e.g., `33_PHOTO-scaled.jpeg`). These need to be identified, renamed to remove the suffix, and copied to a new directory while preserving the original folder structure. This ensures a cleaner and more standard file naming convention for the final product images.

## What Changes
- Add a new Python script `remove-scaled-suffix.py` to handle the renaming and copying process.
- Create a new output directory `uploads-no-bg-done-no-scaled/` to store the processed images.
- Ensure the script replicates the source directory structure (`YYYY/MM/filename`).

## Impact
- Affected specs: `image-processing`
- Affected code: New file `remove-scaled-suffix.py`.
