#!/usr/bin/env python3
"""
File Picker Handler Script

This script waits for a native file picker or file viewer window to appear
(e.g., from an upload dialog or open file dialog) and then simulates pressing
the Enter or Return key to confirm the default file selection.

Platform-independent solution supporting both Windows and macOS.
"""

import time
import logging
import platform
import pyautogui
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure pyautogui for safety
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions

try:
    import pygetwindow as gw
    HAS_PYGETWINDOW = True
except ImportError:
    HAS_PYGETWINDOW = False
    logger.warning("pygetwindow not available. Using fallback detection method.")


class FilePickerHandler:
    """
    Handles native file picker dialogs by waiting for them to appear
    and then simulating Enter key press to confirm selection.
    """
    
    def __init__(self, timeout: int = 10, check_interval: float = 0.5):
        """
        Initialize the file picker handler.
        
        Args:
            timeout: Maximum time to wait for dialog (seconds)
            check_interval: Time between checks (seconds)
        """
        self.timeout = timeout
        self.check_interval = check_interval
        self.system = platform.system().lower()
        
        logger.info(f"FilePickerHandler initialized for {self.system}")
        logger.info(f"Timeout: {timeout}s, Check interval: {check_interval}s")
    
    def _get_initial_window_count(self) -> int:
        """
        Get the initial number of windows open.
        
        Returns:
            Number of windows currently open
        """
        if HAS_PYGETWINDOW:
            try:
                return len(gw.getAllWindows())
            except Exception as e:
                logger.warning(f"Could not get window count: {e}")
                return 0
        return 0
    
    def _detect_new_window(self) -> bool:
        """
        Detect if a new window has appeared.
        
        Returns:
            True if a new window is detected, False otherwise
        """
        if not HAS_PYGETWINDOW:
            return False
            
        try:
            current_windows = gw.getAllWindows()
            # Check if any new windows appeared
            # This is a simple heuristic - in practice you might want more sophisticated detection
            return len(current_windows) > self._initial_window_count
        except Exception as e:
            logger.warning(f"Error detecting new window: {e}")
            return False
    
    def _detect_file_dialog_by_title(self) -> bool:
        """
        Detect file dialog by looking for common dialog titles.
        
        Returns:
            True if a file dialog is detected, False otherwise
        """
        if not HAS_PYGETWINDOW:
            return False
            
        try:
            windows = gw.getAllWindows()
            file_dialog_keywords = [
                'save as', 'open', 'file', 'upload', 'download',
                'choose file', 'select file', 'browse'
            ]
            
            for window in windows:
                title = window.title.lower()
                if any(keyword in title for keyword in file_dialog_keywords):
                    logger.info(f"Detected file dialog: {window.title}")
                    return True
                    
        except Exception as e:
            logger.warning(f"Error detecting file dialog by title: {e}")
            
        return False
    
    def _press_enter_safely(self) -> bool:
        """
        Safely press the Enter key.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Pressing Enter key to confirm file selection...")
            pyautogui.press('enter')
            logger.info("Enter key pressed successfully")
            return True
        except Exception as e:
            logger.error(f"Error pressing Enter key: {e}")
            return False
    
    def wait_and_confirm(self, initial_window_count: Optional[int] = None) -> bool:
        """
        Wait for a file picker dialog to appear and then press Enter to confirm.
        
        Args:
            initial_window_count: Optional initial window count for detection
            
        Returns:
            True if successful, False if timeout or error
        """
        logger.info("Starting file picker detection...")
        
        # Set initial window count
        if initial_window_count is not None:
            self._initial_window_count = initial_window_count
        else:
            self._initial_window_count = self._get_initial_window_count()
        
        logger.info(f"Initial window count: {self._initial_window_count}")
        
        start_time = time.time()
        elapsed_time = 0
        
        while elapsed_time < self.timeout:
            logger.debug(f"Checking for file dialog... (elapsed: {elapsed_time:.1f}s)")
            
            # Try multiple detection methods
            dialog_detected = False
            
            # Method 1: Check for new windows
            if self._detect_new_window():
                logger.info("New window detected")
                dialog_detected = True
            
            # Method 2: Check for file dialog by title
            if self._detect_file_dialog_by_title():
                logger.info("File dialog detected by title")
                dialog_detected = True
            
            # Method 3: Platform-specific detection
            if self.system == "windows":
                dialog_detected = self._detect_windows_file_dialog()
            elif self.system == "darwin":  # macOS
                dialog_detected = self._detect_macos_file_dialog()
            
            if dialog_detected:
                logger.info("File dialog detected! Pressing Enter to confirm...")
                return self._press_enter_safely()
            
            # Wait before next check
            time.sleep(self.check_interval)
            elapsed_time = time.time() - start_time
        
        logger.warning(f"Timeout reached ({self.timeout}s). No file dialog detected.")
        return False
    
    def _detect_windows_file_dialog(self) -> bool:
        """
        Windows-specific file dialog detection.
        
        Returns:
            True if file dialog is detected, False otherwise
        """
        if not HAS_PYGETWINDOW:
            return False
            
        try:
            windows = gw.getAllWindows()
            # Look for common Windows file dialog window classes
            dialog_classes = [
                '#32770',  # Common dialog
                'ComboBoxEx32',
                'ComboBox',
                'Edit',
                'Button'
            ]
            
            for window in windows:
                # Check if window has file dialog characteristics
                if any(cls in str(window) for cls in dialog_classes):
                    logger.info(f"Windows file dialog detected: {window.title}")
                    return True
                    
        except Exception as e:
            logger.warning(f"Error in Windows file dialog detection: {e}")
            
        return False
    
    def _detect_macos_file_dialog(self) -> bool:
        """
        macOS-specific file dialog detection.
        
        Returns:
            True if file dialog is detected, False otherwise
        """
        if not HAS_PYGETWINDOW:
            return False
            
        try:
            windows = gw.getAllWindows()
            # Look for common macOS file dialog indicators
            dialog_indicators = [
                'save', 'open', 'choose', 'file'
            ]
            
            for window in windows:
                title = window.title.lower()
                if any(indicator in title for indicator in dialog_indicators):
                    logger.info(f"macOS file dialog detected: {window.title}")
                    return True
                    
        except Exception as e:
            logger.warning(f"Error in macOS file dialog detection: {e}")
            
        return False


def main():
    """
    Main function for standalone execution.
    """
    print("File Picker Handler")
    print("=" * 50)
    
    # Create handler with default settings
    handler = FilePickerHandler(timeout=10, check_interval=0.5)
    
    print(f"Waiting up to {handler.timeout} seconds for file dialog...")
    print("Move mouse to corner to abort (failsafe)")
    print()
    
    # Wait for user to trigger file dialog
    print("Please trigger a file dialog (e.g., click 'Choose File' button)...")
    
    # Start detection
    success = handler.wait_and_confirm()
    
    if success:
        print("✅ Successfully confirmed file selection!")
    else:
        print("❌ No file dialog detected or confirmation failed")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main()) 