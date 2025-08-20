#!/usr/bin/env python3
"""
Test script for folder processing and renaming functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from pdf_field_filler import find_most_recent_folder, rename_folder_to_completion

def test_folder_processing():
    """Test the folder processing and renaming functionality."""
    
    print("=" * 70)
    print("Folder Processing and Renaming Test")
    print("=" * 70)
    
    # Test finding most recent folder
    print("\n1. Finding most recent folder...")
    folder_path = find_most_recent_folder()
    
    if folder_path:
        print(f"✅ Found most recent folder: {folder_path.name}")
        print(f"   Path: {folder_path}")
        
        # Test renaming (we'll rename it back)
        print(f"\n2. Testing folder renaming...")
        original_name = folder_path.name
        
        # Rename to completion
        success = rename_folder_to_completion(folder_path)
        
        if success:
            print("✅ Folder renamed successfully!")
            
            # Find the renamed folder
            downloads_path = Path.home() / "Downloads"
            renamed_folders = [f for f in downloads_path.iterdir() if f.is_dir() and f.name.startswith("completion")]
            
            if renamed_folders:
                latest_completion = max(renamed_folders, key=lambda f: f.stat().st_mtime)
                print(f"   Renamed to: {latest_completion.name}")
                
                # Rename it back to original name
                print(f"\n3. Renaming back to original name...")
                try:
                    original_path = latest_completion.rename(downloads_path / original_name)
                    print(f"✅ Renamed back to: {original_name}")
                except Exception as e:
                    print(f"❌ Failed to rename back: {e}")
            else:
                print("❌ Could not find renamed folder")
        else:
            print("❌ Folder renaming failed!")
    else:
        print("❌ No folder found in Downloads")
    
    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)

if __name__ == "__main__":
    test_folder_processing()
