# DeepVision Counter

**AI-Powered People Counting System**

Professional customer counting solution for retail stores, restaurants, offices, and events. Uses YOLOv8 AI for accurate real-time detection and tracking.

![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

- **Accurate AI Counting** - YOLOv8 neural network detects and tracks people in real-time
- **IN/OUT Tracking** - Separate counters for entries and exits with "Currently Inside" display
- **Multi-Language** - English and Hebrew support (easily extensible)
- **Dark/Light Themes** - Professional UI with modern design
- **100% Private** - All processing happens locally, no cloud required
- **Cross-Platform** - Works on Windows, macOS, and Linux

---

## Quick Start

### Windows

1. Install Python 3.8+ from [python.org](https://python.org) (check "Add to PATH")
2. Double-click `build_windows/run_deepvision.bat`
3. Wait for first-time setup (installs dependencies)
4. App launches automatically!

### macOS

1. Open Terminal in the project folder
2. Run: `./🚀 LAUNCH APP.command`
3. Or: `python3 deepvision_counter.py`

### Linux

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python3 deepvision_counter.py
```

---

## Manual Installation (All Platforms)

```bash
# 1. Clone or download this repository
git clone https://github.com/yourusername/deepvision-counter.git
cd deepvision-counter

# 2. Create virtual environment (recommended)
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python deepvision_counter.py
```

---

## How to Use

### First Time Setup

1. **Grant Camera Permission** - Allow camera access when prompted
2. **Click START** - Begin counting people
3. **Adjust Settings** - Click SETTINGS to customize detection

### Daily Usage

1. **START** - Begin counting
2. **STOP** - Pause counting
3. **RESET** - Reset all counters to zero
4. **SETTINGS** - Configure camera, language, theme, detection confidence

### Understanding the Counts

- **IN** - People who crossed the line moving downward (entering)
- **OUT** - People who crossed the line moving upward (exiting)
- **Currently Inside** - IN minus OUT (current occupancy)

---

## Requirements

### Hardware
- Camera (USB webcam, built-in, or IP camera)
- 4GB RAM minimum (8GB recommended)
- Any modern CPU (GPU optional, improves performance)

### Software
- Python 3.8 or higher
- Operating System: Windows 10+, macOS 10.15+, or Linux

---

## Project Structure

```
deepvision-counter/
├── deepvision_counter.py    # Main application
├── requirements.txt         # Python dependencies
├── yolov8n.pt              # AI model (auto-downloads)
├── deepvision_settings.json # User settings
│
├── build_windows/          # Windows files
│   └── run_deepvision.bat  # Windows launcher
│
├── build_mac/              # macOS files
│   └── Launch App.command  # macOS launcher
│
└── docs/                   # Documentation
```

---

## Configuration

Settings are saved in `deepvision_settings.json`:

```json
{
  "language": "en",
  "theme": "dark",
  "camera_index": 0,
  "confidence": 0.45,
  "show_fps": true,
  "save_data": true
}
```

| Setting | Description | Values |
|---------|-------------|--------|
| language | UI language | "en", "he" |
| theme | Color theme | "dark", "light" |
| camera_index | Camera device | 0, 1, 2... |
| confidence | Detection threshold | 0.1 - 0.9 |
| show_fps | Display FPS counter | true/false |
| save_data | Save counting data | true/false |

---

## Troubleshooting

### Camera Not Working

**Windows:**
- Settings → Privacy → Camera → Allow apps to access camera
- Try different camera index (0, 1, 2) in Settings

**macOS:**
- System Settings → Privacy & Security → Camera → Enable for Terminal/Python
- Try: `tccutil reset Camera` in Terminal (resets permissions)

**Linux:**
- Check camera with: `ls /dev/video*`
- Install v4l-utils: `sudo apt install v4l-utils`

### App Won't Start

1. Make sure Python 3.8+ is installed: `python --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Check for errors in terminal output

### Counting is Inaccurate

- Position camera overhead or at an angle
- Ensure good lighting
- Adjust confidence slider in Settings (lower = more detections)
- Make sure people fully cross the counting line

---

## Privacy & Security

- **100% Offline** - No internet required
- **Local Processing** - All AI runs on your computer
- **No Cloud** - Your data never leaves your device
- **No Tracking** - No analytics or telemetry

---

## Use Cases

- **Retail Stores** - Track foot traffic and peak hours
- **Restaurants** - Monitor capacity and wait times
- **Offices** - Manage occupancy limits
- **Events** - Count attendees
- **Libraries** - Track visitor patterns
- **Gyms** - Monitor current occupancy

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

MIT License - Feel free to use for personal or commercial projects.

---

## Credits

- **AI Model**: [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- **Computer Vision**: [OpenCV](https://opencv.org/)
- **UI Framework**: Python Tkinter

---

**Made with ❤️ for businesses worldwide**
