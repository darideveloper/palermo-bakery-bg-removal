## 1. Implementation
- [x] 1.1 Create `remove-scaled-suffix.py` with necessary imports (`os`, `sqlite3`, `pathlib`, `shutil`, `tqdm`).
- [x] 1.2 Implement SQLite state management (`init_db`, `is_processed`, `mark_as_done`) for `renaming_status.db`.
- [x] 1.3 Implement scanning logic to find files ending with `-scaled` (before the extension) in `uploads-no-bg-done`.
- [x] 1.4 Implement renaming and copying logic to `uploads-no-bg-done-no-scaled` while preserving structure.
- [x] 1.5 Add progress tracking with `tqdm`.

## 2. Validation
- [x] 2.1 Test script on a subset of data (if possible) or run locally to verify renaming results.
- [x] 2.2 Verify directory structure in `uploads-no-bg-done-no-scaled`.
- [x] 2.3 Check `renaming_status.db` for correct state tracking.
- [x] 2.4 Update `openspec/project.md` to include the new stage.
