import os
import datetime
from pathlib import Path

def log_error(error_message: str):
    """
    Utility function for logging errors.
    
    Args:
        error_message: The error message to log
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Generate log filename with current date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"error_log_{current_date}.log"
    
    # Write error with timestamp to log file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] ERROR: {error_message}\n")
    
    # Also print to console
    print(f"ERROR: {error_message}")