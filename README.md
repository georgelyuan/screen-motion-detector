# Screen Motion Detector

A Python script that monitors a specific monitor or region of your screen for motion and saves screenshots when motion is detected. Useful for capturing motion events from security cameras, video feeds, or any other screen content.

## Features

- Monitor any connected display
- Motion detection with configurable sensitivity
- Automatic screenshot saving with timestamps
- Ignore specific regions (e.g., timestamps or overlays)
- Configurable delay between captures
- Support for multiple monitors

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- Pillow
- mss

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/screen-motion-detector.git
cd screen-motion-detector
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
python motion_detector.py
```

2. The script will show you a list of available monitors. Enter the number of the monitor you want to capture.

3. The script will start monitoring the selected display for motion. When motion is detected, screenshots will be saved in the `motion_captures` directory.

4. Press Ctrl+C to stop the script.

## Configuration

You can adjust the following parameters in the script:

- `threshold`: Sensitivity of motion detection (default: 50)
  - Lower values = more sensitive to small changes
  - Higher values = only detect larger changes
- `min_area`: Minimum area of motion to trigger detection (default: 100)
- `capture_delay`: Minimum delay between captures in seconds (default: 0.5)
- `ignore_height` and `ignore_width`: Size of the region to ignore in the bottom left corner

## License

MIT License - feel free to use this code for any purpose.

## Contributing

Feel free to submit issues and enhancement requests! 