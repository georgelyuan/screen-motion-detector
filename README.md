# Screen Motion Detector

A Python script that monitors a specific region of your screen for motion and automatically captures screenshots when motion is detected. Perfect for monitoring security cameras, dashboards, or any other screen content that needs motion-based capture.

## Features

- Real-time motion detection using OpenCV
- Automatic screenshot capture when motion is detected
- Configurable motion sensitivity (default threshold: 25)
- Visual feedback with red bounding box around motion areas
- Performance monitoring with timing measurements
- Efficient JPEG compression (95% quality)
- Support for multiple monitors
- Automatic creation of output directory
- Unique filenames with timestamps

## Installation

1. Clone this repository:
```bash
git clone https://github.com/georgelyuan/screen-motion-detector.git
cd screen-motion-detector
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python3 motion_detector.py
```

The script will:
1. List available monitors
2. Select monitor 2 by default (1920x1200)
3. Start monitoring for motion
4. Save screenshots to the `motion_captures` directory when motion is detected

### Parameters

- `monitor_number`: The monitor to capture (default: 2)
- `threshold`: Motion detection sensitivity (default: 25)
  - Higher values = less sensitive to motion
  - Lower values = more sensitive to motion

### Output

Screenshots are saved as JPEG files with:
- Filename format: `motion_YYYYMMDD_HHMMSS_mmm.jpg`
- Red bounding box around detected motion
- Timing information in console output

## Requirements

- Python 3.6+
- OpenCV (cv2)
- mss (for screen capture)
- PIL (Python Imaging Library)

## License

MIT License 