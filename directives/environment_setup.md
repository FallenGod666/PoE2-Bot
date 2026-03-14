# Environment Setup and Management

## Goal
Ensure all development and execution occurs within a controlled virtual environment to prevent dependency conflicts and ensure reproducibility.

## Requirements
- Virtual environment directory: `.venv/`
- All Python execution MUST use `.venv/Scripts/python.exe` (on Windows).
- All dependencies MUST be installed via `pip` within the `.venv`.

## SOP: Dependency Installation
1. **Identify Dependency**: Know the package name and required version.
2. **Check Current Environment**: Verify that the `.venv` is active or that the tool being used is pointing to the `.venv` interpreter.
3. **Execute Installation**:
   - Command: `.venv/Scripts/python.exe -m pip install <package_name>`
4. **Update Requirements**: Immediately update `requirements.txt` after any successful installation.
   - Command: `.venv/Scripts/python.exe -m pip freeze > requirements.txt`

## SOP: Script Execution
1. **Prepare Execution**: Ensure all scripts are located in the `execution/` directory.
2. **Run Script**:
   - Command: `.venv/Scripts/python.exe execution/<script_name>.py`

## Error Handling
- If a `ModuleNotFoundError` occurs, verify the package is installed in the `.venv`.
- If permission issues occur, ensure no other process is using files in `.venv`.
