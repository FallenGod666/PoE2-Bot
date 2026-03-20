# Build Executable SOP

## Goal
Create a standalone Windows executable (`.exe`) for the PoE2-Bot system.

## Requirements
- `pyinstaller` installed in `.venv`.
- All source files in `execution/` and root directory.

## Build Steps
1. **Prepare Environment**: Ensure `.venv` is active and all dependencies are installed.
2. **Execute Build**:
   - Command: `pyinstaller --noconsole --onefile --add-data "execution;execution" --add-data "config.json;." app_gui.py`
   - *Note*: `--noconsole` hides the terminal window. `--onefile` bundles everything into a single `.exe`.
3. **Verify Output**: The executable will be generated in the `dist/` folder.

## Resource Handling in Code
When using `PyInstaller` with `--onefile`, internal paths must be handled using `sys._MEIPASS` to find bundled data files.

```python
import sys
import os

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
```

## Troubleshooting
- If the `.exe` closes immediately, rebuild without `--noconsole` to see error messages.
- Ensure all imports are correctly identified by PyInstaller.
