import sys
import os
from pathlib import Path

def verify():
    print("--- DOE Architecture Verification ---")
    
    # Check Python Path (should be in .venv)
    executable = sys.executable
    print(f"Python Executable: {executable}")
    
    if ".venv" in executable:
        print("✅ SUCCESS: Running from Virtual Environment.")
    else:
        print("❌ WARNING: Not running from Virtual Environment!")
        
    # Check for .env file
    env_path = Path(".env")
    if env_path.exists():
        print("✅ SUCCESS: .env file found.")
    else:
        print("❌ ERROR: .env file missing.")
        
    # Check directory structure
    dirs = ["directives", "execution", ".tmp"]
    for d in dirs:
        if Path(d).is_dir():
            print(f"✅ SUCCESS: Directory mapping '{d}/' exists.")
        else:
            print(f"❌ ERROR: Directory mapping '{d}/' missing.")

    print("--------------------------------------")

if __name__ == "__main__":
    verify()
