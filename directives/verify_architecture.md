# Directive: Verify Architecture

## Goal
Verify that the 3-layer architecture (DOE) is correctly set up and that the virtual environment is being used.

## Inputs
- None

## Tools/Scripts
- `execution/verify_installation.py`

## Steps
1. Run `execution/verify_installation.py` using the project's virtual environment.
2. Observe the output to ensure:
    - Python version is expected.
    - Script is running from within the `.venv`.
    - `.env` file is present.

## Expected Output
- A status report on the environment health.
- Confirmation of virtual environment usage.
