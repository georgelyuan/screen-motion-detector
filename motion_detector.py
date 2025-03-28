import cv2
import numpy as np
from PIL import Image
import mss
import time
import os
from datetime import datetime

class MotionDetector:
    def __init__(self, monitor_number, threshold=50, min_area=100):
        """
        Initialize the motion detector
        :param monitor_number: The monitor number to capture
        :param threshold: threshold for motion detection (default: 50)
        :param min_area: minimum area of motion to trigger detection (default: 100)
        """
        self.sct = mss.mss()
        self.monitor_number = monitor_number
        self.threshold = threshold
        self.min_area = min_area
        self.prev_frame = None
        self.output_dir = "motion_captures"
        self.last_capture_time = 0
        self.capture_delay = 0.5  # Minimum delay between captures in seconds
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def list_monitors(self):
        """List all available monitors"""
        monitors = self.sct.monitors
        print("\nAvailable monitors:")
        for i, monitor in enumerate(monitors):
            print(f"{i}: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
        return monitors

    def capture_screen(self):
        """Capture the specified monitor"""
        screenshot = self.sct.grab(self.sct.monitors[self.monitor_number])
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def create_mask(self, frame):
        """Create a mask to ignore the bottom left corner"""
        height, width = frame.shape[:2]
        # Create a black mask (0) with white region (255) to ignore
        mask = np.zeros((height, width), dtype=np.uint8)
        # Define the region to ignore (bottom left corner)
        # Adjust these values based on your timestamp size and position
        ignore_height = 150  # Height of the ignored region
        ignore_width = 200  # Width of the ignored region
        mask[height-ignore_height:height, 0:ignore_width] = 255
        return mask

    def detect_motion(self, frame):
        """Detect motion in the current frame"""
        if self.prev_frame is None:
            self.prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return False

        # Convert current frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate difference between current and previous frame
        diff = cv2.absdiff(gray, self.prev_frame)
        
        # Apply threshold
        _, thresh = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)
        
        # Create and apply mask to ignore bottom left corner
        mask = self.create_mask(frame)
        thresh = cv2.bitwise_and(thresh, thresh, mask=cv2.bitwise_not(mask))
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check for significant motion
        for contour in contours:
            if cv2.contourArea(contour) > self.min_area:
                return True
        
        # Update previous frame
        self.prev_frame = gray
        return False

    def save_screenshot(self, frame):
        """Save the current frame as a screenshot"""
        current_time = time.time()
        if current_time - self.last_capture_time >= self.capture_delay:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"motion_{timestamp}.png")
            cv2.imwrite(filename, frame)
            print(f"Saved screenshot: {filename}")
            self.last_capture_time = current_time

    def run(self):
        """Main loop for motion detection"""
        # List available monitors
        monitors = self.list_monitors()
        
        print(f"\nCapturing monitor {self.monitor_number}: {monitors[self.monitor_number]['width']}x{monitors[self.monitor_number]['height']}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Capture current frame
                frame = self.capture_screen()
                
                # Detect motion
                if self.detect_motion(frame):
                    print("Motion detected!")
                    self.save_screenshot(frame)
                
                # Small delay to reduce CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nStopping motion detection...")

if __name__ == "__main__":
    # First, create a temporary detector to list monitors
    temp_detector = MotionDetector(0)
    monitors = temp_detector.list_monitors()
    
    # Ask user which monitor to capture
    while True:
        try:
            monitor_number = int(input("\nEnter the monitor number to capture: "))
            if 0 <= monitor_number < len(monitors):
                break
            print("Invalid monitor number. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Create and run the motion detector with the selected monitor
    detector = MotionDetector(monitor_number)
    detector.run() 