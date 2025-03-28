import cv2
import numpy as np
from PIL import Image
import mss
import time
import os
from datetime import datetime

class MotionDetector:
    """
    A class to detect motion in a specific region of the screen and save screenshots.
    
    This class uses OpenCV to compare consecutive screen captures and detect motion
    by calculating the mean squared error between frames. When motion is detected
    above a specified threshold, it saves a screenshot of the current screen state.
    
    The motion detection algorithm:
    1. Captures the specified screen region
    2. Converts the image to grayscale
    3. Compares with the previous frame using mean squared error
    4. Triggers if the error exceeds the threshold (default: 25)
    """
    
    def __init__(self, monitor_number=2, threshold=25):
        """
        Initialize the motion detector.
        
        Args:
            monitor_number (int): The monitor number to capture (default: 2)
            threshold (float): Motion detection threshold (default: 25)
                             Higher values mean less sensitive to motion
        """
        self.sct = mss.mss()
        self.monitor_number = monitor_number
        self.threshold = threshold
        self.min_area = 100
        self.prev_frame = None
        self.output_dir = "motion_captures"
        self.last_capture_time = 0
        self.capture_delay = 0.1  # Minimum delay between captures in seconds
        
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
        #print(f"Capture time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def create_mask(self, frame):
        """Create a mask to ignore the bottom left corner and right edge"""
        height, width = frame.shape[:2]
        # Create a black mask (0) with white region (255) to ignore
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Define the region to ignore (bottom left corner)
        ignore_height = 150  # Height of the ignored region
        ignore_width = 1600  # Width of the ignored region
        mask[height-ignore_height:height, 0:ignore_width] = 255
        
        # Define the region to ignore (right edge)
        right_ignore_width = 450  # Width of the ignored region on the right
        mask[0:height, width-right_ignore_width:width] = 255

        # Define the region to ignore (top portion)
        top_ignore_height = 140  # Height of the ignored region at the top
        mask[0:top_ignore_height, 0:width] = 255

        
        return mask

    def find_largest_motion_region(self, diff, mask):
        """Find the largest region of motion"""
        # Apply threshold
        _, thresh = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)
        
        # Apply mask to ignore bottom left corner
        thresh = cv2.bitwise_and(thresh, thresh, mask=cv2.bitwise_not(mask))
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, None
        
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) < self.min_area:
            return None, None
            
        # Get bounding box
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h), largest_contour

    def detect_motion(self, current_frame):
        """
        Detect motion by comparing current frame with previous frame.
        
        Args:
            current_frame (numpy.ndarray): Current frame in grayscale
            
        Returns:
            bool: True if motion is detected, False otherwise
            tuple: Bounding box coordinates (x, y, w, h) if motion detected, None otherwise
        """
        if self.prev_frame is None:
            self.prev_frame = current_frame
            return False, None

        # Calculate difference between current and previous frame
        diff = cv2.absdiff(current_frame, self.prev_frame)
        
        # Create and apply mask
        mask = self.create_mask(current_frame)
        
        # Find largest motion region
        bbox, contour = self.find_largest_motion_region(diff, mask)
        
        # Update previous frame
        self.prev_frame = current_frame
        
        return bbox is not None, bbox

    def save_screenshot(self, frame, bounding_box=None):
        """
        Save the current frame as a screenshot with optional motion bounding box.
        
        Args:
            frame (numpy.ndarray): The frame to save
            bounding_box (tuple): Optional bounding box coordinates (x, y, w, h)
            
        The screenshot is saved as a JPEG file with:
        - 95% quality for good balance of quality and file size
        - Filename format: motion_YYYYMMDD_HHMMSS_mmm.jpg
        - Timing measurement for performance monitoring
        """
        current_time = time.time()
        if current_time - self.last_capture_time >= self.capture_delay:
            # Start timing
            save_start = time.time()
            
            # Create a copy of the frame for visualization
            vis_frame = frame.copy()
            
            # Draw red bounding box if motion was detected
            if bounding_box:
                x, y, w, h = bounding_box
                cv2.rectangle(vis_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            
            # Draw purple bounding boxes around masked regions
            height, width = vis_frame.shape[:2]
            ignore_height = 150  # Height of the ignored region
            ignore_width = 1600  # Width of the ignored region

            
            # Bottom left corner mask (timestamp region)

            cv2.rectangle(vis_frame, 
                         (0, height-ignore_height), 
                         (ignore_width, height), 
                         (255, 0, 255),  # Purple color
                         2)
            
            # Right edge mask
            right_ignore_width = 450
            cv2.rectangle(vis_frame, 
                         (width-right_ignore_width, 0), 
                         (width, height), 
                         (255, 0, 255),  # Purple color
                         2)
            
            # top 
            top_ignore_height = 140  # Height of the ignored region at the top
            # draw a rectangle on the top of the screen
            cv2.rectangle(vis_frame, 
                         (0, 0), 
                         (width, top_ignore_height), 
                         (255, 0, 255),  # Purple color
                         2)
            
            # Use datetime with milliseconds for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]  # Truncate to 3 decimal places
            filename = os.path.join(self.output_dir, f"motion_{timestamp}.jpg")
            
            # Save with JPEG compression (95% quality, much faster than PNG)
            cv2.imwrite(filename, vis_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            # Calculate and print timing
            save_time = time.time() - save_start
            print(f"Saved screenshot: {filename} (took {save_time:.3f} seconds)")
            
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
                motion_detected, bbox = self.detect_motion(frame)
                if motion_detected:
                    print("Motion detected!")
                    self.save_screenshot(frame, bbox)
                
                # Small delay to reduce CPU usage
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nStopping motion detection...")

if __name__ == "__main__":
    # First, create a temporary detector to list monitors
    temp_detector = MotionDetector(0)
    monitors = temp_detector.list_monitors()
    
    # Default to monitor 2, but keep the selection code for future use
    monitor_number = 2  # Default to monitor 2
    # Uncomment the following lines to enable monitor selection
    # while True:
    #     try:
    #         monitor_number = int(input("\nEnter the monitor number to capture: "))
    #         if 0 <= monitor_number < len(monitors):
    #             break
    #         print("Invalid monitor number. Please try again.")
    #     except ValueError:
    #         print("Please enter a valid number.")
    
    # Create and run the motion detector with the selected monitor
    detector = MotionDetector(monitor_number=monitor_number)
    detector.run() 