"""
File cleanup utilities
"""
import os
from pathlib import Path
from typing import Union


def cleanup_old_files(directory: Union[str, Path], max_files: int = 20) -> None:
    """
    Remove oldest files in directory if count exceeds max_files
    """
    directory = Path(directory)
    
    if not directory.exists():
        return
    
    # Get all files sorted by modification time
    files = sorted(
        directory.glob('*'),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    # Remove oldest files if exceeding max
    if len(files) > max_files:
        for file in files[max_files:]:
            try:
                file.unlink()
            except Exception as e:
                print(f"Error deleting {file}: {e}")
