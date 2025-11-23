# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-24

### Added

- **Dynamic UI Visibility**: Job dialog now shows/hides elements based on recurrence type
  - Daily: Shows only time selection
  - Weekly: Shows time + day of week selector
  - Monthly: Shows time + day of month selector (1-31)
  - Yearly/Once: Shows time + full calendar widget
- **File Chooser**: Browse button next to command entry for easy script/executable selection
  - Folder icon button opens native GTK4 file dialog
  - Smart filters for scripts (.sh, .py, .pl, .rb, .js) and executables
  - Auto-fills command entry with selected file path
- **Enhanced UI/UX**:
  - Improved spacing (18px between sections, 24px margins)
  - Better typography with title-4, dim-label, and caption classes
  - Visual separators between major sections
  - Enhanced time picker with vertical layout and labeled spinners
  - Tooltips on all input fields for better guidance
  - Pill-styled preset buttons
  - Larger dialog size (550x600, resizable)
  - Emojis in dialog title and advanced options

### Changed

- Reorganized advanced options (presets, manual entry, builder) into collapsible section
- Improved label styling and capitalization
- Enhanced button styling with better visual hierarchy
- Default recurrence changed to "Daily" (most common use case)

### Fixed

- AttributeError when opening job dialog (missing callback methods)
- Proper datetime import organization

## [0.1.0] - 2025-11-23

### Added

- Initial release
- GTK4/Adwaita-based desktop application for managing cron jobs
- Add, edit, and delete cron jobs
- Visual cron expression builder
- Quick preset buttons for common schedules
- Validation and next run preview
- Modern, clean interface
- Support for comments on cron jobs

[0.2.0]: https://github.com/goal651/cron_gui/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/goal651/cron_gui/releases/tag/v0.1.0
