## ADDED Requirements

### Requirement: Scaled Suffix Filename Identification
The system SHALL identify all images in the source directory that contain the string `-scaled` immediately before the file extension.

#### Scenario: Image with -scaled suffix
- **WHEN** a file named `2022/01/image-scaled.jpeg` exists in the source directory
- **THEN** it MUST be flagged for renaming

#### Scenario: Image without -scaled suffix
- **WHEN** a file named `2022/01/image.jpeg` exists in the source directory
- **THEN** it MUST NOT be flagged for renaming

### Requirement: Scaled Suffix Removal and Renaming
The system SHALL copy flagged files to a destination directory, renaming them to remove the `-scaled` suffix while preserving the extension.

#### Scenario: Suffix removal success
- **WHEN** `image-scaled.jpeg` is processed
- **THEN** the output filename in the destination MUST be `image.jpeg`

### Requirement: Directory Structure Preservation
The system SHALL replicate the source directory tree structure in the destination directory.

#### Scenario: Nested path preservation
- **WHEN** `uploads-no-bg-done/2023/05/example-scaled.png` is processed
- **THEN** it MUST be saved to `uploads-no-bg-done-no-scaled/2023/05/example.png`

### Requirement: Resumable Processing State
The system SHALL maintain a state database to track processed files and avoid redundant operations.

#### Scenario: Resuming interrupted task
- **WHEN** the script is run for a second time
- **THEN** only files not marked as "completed" in the state database SHALL be processed
