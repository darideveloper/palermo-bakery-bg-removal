# Project Context

## Purpose
An automated image processing pipeline designed to clean up and standardize a WordPress-style `uploads` directory. It uses AI to remove backgrounds, restores a consistent white background, and manages the file library by synchronizing it with a product database (`products.csv`).

## Tech Stack
- **Language**: Python 3.x
- **Image Processing**: 
  - `transparent-background` (InSPyReNet model for high-quality background removal)
  - `Pillow` (PIL) for image manipulation (compositing, conversion, saving)
- **Database**: `SQLite3` for state management and tracking processing status
- **Utilities**: 
  - `tqdm` for interactive progress bars
  - `pathlib` for cross-platform path handling
  - `urllib.parse` for URL decoding

## Project Conventions

### Code Style
- **Naming**: Snake-case for functions and variables; upper-case for constants.
- **Path Handling**: Use `pathlib.Path` objects over string concatenation for robust path management.
- **Feedback**: Use `tqdm` for all long-running processes, preferring `tqdm.write` for logs to avoid bar flicker.

### Architecture Patterns
- **Stateful Processing**: Uses local SQLite databases (`processing_status.db`, `finalizing_status.db`) to allow for resumable pipelines and to avoid redundant processing of already completed files.
- **Staged Pipeline**: 
  1. Background Removal (`uploads` -> `uploads-no-bg`)
  2. Background Restoration (`uploads-no-bg` -> `uploads-no-bg-done`)
  3. Cleanup (`uploads` folder based on `products.csv`)
- **Structure-Preserving**: Replicates the source directory's tree structure (`YYYY/MM/filename`) in all output directories.

### Testing Strategy
- **Manual Verification**: Visual check of output images in the `uploads-no-bg-done` directory.
- **Status Checks**: Querying the `.db` files to ensure all tasks are marked as "completed".

### Git Workflow
- **Conventional Commits**: (e.g., `feat(bg-removal): integrate InSPyReNet model`).

## Domain Context
- **WordPress Integration**: The project specifically targets WordPress `wp-content/uploads` directory structures.
- **URL Mapping**: Image paths are extracted from WordPress product export CSVs (specifically the `URL` column, which may contain pipe-separated values).

## Important Constraints
- **Model Loading**: The `transparent-background` model (InSPyReNet) requires significant resources and time to load on the first run.
- **Format Consistency**: Original file extensions (JPG, PNG, WebP) must be preserved in the final output, except for intermediate transparent stages which use PNG.
- **Large Datasets**: The `uploads` directory can contain thousands of files; resumable processing via SQLite is critical.

## External Dependencies
- **AI Models**: Relies on the InSPyReNet pre-trained model downloaded by the `transparent-background` library.
- **WordPress Exports**: Relies on a CSV format with `id`, `Title`, `SKU`, and `URL` columns.
