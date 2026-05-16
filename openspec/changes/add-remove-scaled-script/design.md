# Design: Scaled Suffix Removal Pipeline

## Context
The project processes WordPress uploads in stages. Some images produced in previous stages (likely from the `uploads-no-bg-done` directory) retain the `-scaled` suffix in their filenames. We need a way to reliably remove this suffix and store the renamed files in a new destination.

## Goals / Non-Goals
- **Goals**:
  - Identify files with `-scaled` suffix.
  - Rename by removing the suffix.
  - Copy to a new destination folder.
  - Preserve original directory structure.
  - Use SQLite for resumable state management.
- **Non-Goals**:
  - Delete or modify original files in `uploads-no-bg-done`.
  - Process files that don't have the `-scaled` suffix.

## Decisions
- **Decision: SQLite for State Management**
  - Justification: Consistent with previous scripts (`remove-bg.py`, `add-white-bg.py`). Ensures we don't re-copy files on subsequent runs.
- **Decision: Directory Structure Replication**
  - Justification: Essential for integration with WordPress and CSV-based cleanup logic.
- **Decision: `pathlib` for Path Management**
  - Justification: Senior standard for cross-platform robustness.

## Risks / Trade-offs
- **Risk**: Renaming might cause collisions if both `image.jpg` and `image-scaled.jpg` exist in the same folder.
- **Mitigation**: The current project logic implies that `-scaled` is often an unwanted suffix on the "best" version of the file. We will overwrite the destination if a collision occurs, or log it if it becomes an issue. For now, the script will focus on the copy-and-rename operation.

## Migration Plan
- Run the script manually to populate `uploads-no-bg-done-no-scaled`.
- Update documentation in `openspec/project.md` after successful implementation.
