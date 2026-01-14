# DeepVision Counter

<div align="center">

![DeepVision Counter](https://img.shields.io/badge/DeepVision-Counter-purple?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

**AI-Powered Real-Time People Counting System**

Professional customer counting solution using YOLOv8 neural network for accurate detection and tracking.

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Requirements](#-requirements)
- [Troubleshooting](#-troubleshooting)
- [Privacy & Security](#-privacy--security)
- [Use Cases](#-use-cases)
- [Contributing](#-contributing)
- [License](#-license)
- [Credits](#-credits)

---

## 🎯 Overview

DeepVision Counter is a professional-grade people counting application that uses state-of-the-art AI (YOLOv8) to accurately detect and track people in real-time. Perfect for retail stores, restaurants, offices, events, and any business that needs to monitor foot traffic and occupancy.

### Key Highlights

- 🤖 **AI-Powered**: Uses YOLOv8 neural network for state-of-the-art accuracy
- 🔒 **100% Private**: All processing happens locally, no cloud required
- 🌍 **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- 🎨 **Modern UI**: Professional interface with dark/light themes
- 🌐 **Multi-Language**: English and Hebrew support (easily extensible)
- ⚡ **Real-Time**: Live counting with instant updates

---

## ✨ Features

### Core Functionality
- ✅ **Real-Time People Detection** - YOLOv8 AI detects people with high accuracy
- ✅ **IN/OUT Tracking** - Separate counters for entries and exits
- ✅ **Current Occupancy** - Real-time "Currently Inside" calculation
- ✅ **Line-Based Counting** - Configurable counting line for accurate tracking

### User Experience
- ✅ **Modern UI Design** - Clean, professional interface
- ✅ **Dark/Light Themes** - Choose your preferred color scheme
- ✅ **Multi-Language Support** - English and Hebrew (easily add more)
- ✅ **FPS Counter** - Monitor performance in real-time
- ✅ **Settings Panel** - Easy configuration of all parameters

### Technical
- ✅ **Cross-Platform** - Windows, macOS, Linux support
- ✅ **Offline Operation** - No internet connection required
- ✅ **Local Processing** - All AI runs on your device
- ✅ **Privacy-First** - No data collection or tracking

---

## 📸 Screenshots

> *Screenshots coming soon - Add your app screenshots here*

---

## 🚀 Quick Start

### Windows

1. Install [Python 3.8+](https://python.org) (check "Add to PATH")
2. Double-click `build_windows/run_deepvision.bat`
3. Wait for first-time setup (~2-3 minutes)
4. App launches automatically! 🎉

### macOS

```bash
# Option 1: Use launcher
./🚀\ LAUNCH\ APP.command

# Option 2: Run directly
python3 deepvision_counter.py
```

### Linux

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python3 deepvision_counter.py
```

---

## 📦 Installation

### Prerequisites

- **Python**: 3.8 or higher
- **Camera**: USB webcam, built-in camera, or IP camera
- **RAM**: 4GB minimum (8GB recommended)
- **OS**: Windows 10+, macOS 10.15+, or Linux

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/deepvision-counter.git
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

The AI model (`yolov8n.pt`) will be automatically downloaded on first run.

---

## 💻 Usage

### First Time Setup

1. **Grant Camera Permission** - Allow camera access when prompted by your OS
2. **Launch Application** - Run the app using one of the methods above
3. **Wait for AI Model** - First launch takes 20-30 seconds (model loading)
4. **Click START** - Begin counting people
5. **Adjust Settings** - Click SETTINGS to customize detection parameters

### Daily Operation

| Action | Description |
|--------|-------------|
| **START** | Begin real-time people counting |
| **STOP** | Pause counting (camera remains active) |
| **RESET** | Reset all counters to zero |
| **SETTINGS** | Configure camera, language, theme, confidence |

### Understanding the Counts

- **IN** - People who crossed the line moving downward (entering)
- **OUT** - People who crossed the line moving upward (exiting)
- **Currently Inside** - IN minus OUT (current occupancy)

### Tips for Best Results

- 📹 Position camera overhead or at an angle for better detection
- 💡 Ensure good lighting conditions
- 📏 Adjust confidence threshold in Settings (lower = more detections)
- ⏱️ Wait for person to fully cross the counting line
- 🎯 Place counting line perpendicular to entrance/exit path

---

## ⚙️ Configuration

Settings are automatically saved in `deepvision_settings.json`:

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

### Settings Reference

| Setting | Description | Values | Default |
|---------|-------------|--------|---------|
| `language` | UI language | `"en"`, `"he"` | `"en"` |
| `theme` | Color theme | `"dark"`, `"light"` | `"dark"` |
| `camera_index` | Camera device number | `0`, `1`, `2`... | `0` |
| `confidence` | Detection threshold | `0.1` - `0.9` | `0.45` |
| `show_fps` | Display FPS counter | `true`, `false` | `true` |
| `save_data` | Save counting data | `true`, `false` | `true` |

---

## 🔧 Requirements

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 4GB | 8GB+ |
| **CPU** | Any modern CPU | Multi-core CPU |
| **GPU** | Not required | NVIDIA GPU (for faster AI) |
| **Camera** | USB webcam or built-in | HD webcam (720p+) |
| **Storage** | 500MB free | 1GB+ free |

### Software Requirements

- **Python**: 3.8 or higher
- **Operating System**: 
  - Windows 10 or newer
  - macOS 10.15 (Catalina) or newer
  - Linux (Ubuntu 18.04+, Debian 10+, or similar)

### Python Dependencies

All dependencies are listed in `requirements.txt`:
- `opencv-python>=4.8.0` - Computer vision
- `ultralytics>=8.0.0` - YOLOv8 AI model
- `Pillow>=10.0.0` - Image processing
- `numpy>=1.24.0` - Numerical operations

---

## 🐛 Troubleshooting

### Camera Not Working

<details>
<summary><b>Windows</b></summary>

1. Go to **Settings → Privacy → Camera**
2. Enable **"Allow apps to access your camera"**
3. Try different camera index (0, 1, 2) in Settings
4. Close other apps using the camera (Zoom, Teams, etc.)

</details>

<details>
<summary><b>macOS</b></summary>

1. Go to **System Settings → Privacy & Security → Camera**
2. Enable camera access for **Terminal** or **Python**
3. If still not working, reset permissions:
   ```bash
   tccutil reset Camera
   ```
4. Try different camera index in Settings

</details>

<details>
<summary><b>Linux</b></summary>

1. Check if camera is detected:
   ```bash
   ls /dev/video*
   ```
2. Install v4l-utils:
   ```bash
   sudo apt install v4l-utils
   ```
3. Test camera:
   ```bash
   v4l2-ctl --list-devices
   ```

</details>

### App Won't Start

1. **Check Python version**: `python --version` (must be 3.8+)
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Check for errors**: Look at terminal output for error messages
4. **Virtual environment**: Make sure you're in the correct virtual environment

### Counting is Inaccurate

- ✅ Position camera overhead or at an angle (not straight-on)
- ✅ Ensure good, even lighting
- ✅ Adjust confidence slider in Settings (lower = more detections, higher = fewer but more accurate)
- ✅ Make sure people fully cross the counting line
- ✅ Avoid placing line near walls or obstacles
- ✅ Wait a moment after person crosses before counting

### Performance Issues

- **Slow FPS**: Lower camera resolution or upgrade hardware
- **High CPU Usage**: Normal for AI processing, consider GPU acceleration
- **Memory Issues**: Close other applications, ensure 4GB+ RAM available

---

## 🔒 Privacy & Security

DeepVision Counter is designed with privacy as a core principle:

- ✅ **100% Offline** - No internet connection required
- ✅ **Local Processing** - All AI runs on your computer
- ✅ **No Cloud** - Your data never leaves your device
- ✅ **No Tracking** - No analytics, telemetry, or data collection
- ✅ **No Network** - No external connections made
- ✅ **Open Source** - Code is transparent and auditable

Your privacy is guaranteed. All processing happens locally on your machine.

---

## 🎯 Use Cases

DeepVision Counter is perfect for:

| Industry | Use Case |
|----------|----------|
| **Retail** | Track foot traffic, analyze peak hours, optimize staffing |
| **Restaurants** | Monitor capacity, manage wait times, track busy periods |
| **Offices** | Manage occupancy limits, track workspace usage |
| **Events** | Count attendees, monitor venue capacity |
| **Libraries** | Track visitor patterns, analyze usage |
| **Gyms** | Monitor current occupancy, track peak times |
| **Museums** | Visitor counting, exhibit popularity analysis |
| **Hotels** | Lobby traffic monitoring, capacity management |

---

## 🤝 Contributing

Contributions are welcome and appreciated! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs** - Found a bug? Open an issue!
- 💡 **Suggest Features** - Have an idea? Share it in discussions!
- 📝 **Improve Documentation** - Help make the docs better
- 🔧 **Submit Pull Requests** - Fix bugs or add features
- 🌐 **Add Translations** - Help translate to more languages
- ⭐ **Star the Repo** - Show your support!

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

This means:
- ✅ Free to use for personal and commercial projects
- ✅ Free to modify and distribute
- ✅ No warranty provided

---

## 🙏 Credits

DeepVision Counter is built with amazing open-source technologies:

- **[Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)** - State-of-the-art object detection
- **[OpenCV](https://opencv.org/)** - Computer vision library
- **[Python Tkinter](https://docs.python.org/3/library/tkinter.html)** - GUI framework
- **[Pillow](https://python-pillow.org/)** - Image processing

---

## 📞 Support

- 📖 **Documentation**: Check the `docs/` folder for detailed guides
- 🐛 **Bug Reports**: [Open an issue](https://github.com/YOUR_USERNAME/deepvision-counter/issues)
- 💬 **Discussions**: [Start a discussion](https://github.com/YOUR_USERNAME/deepvision-counter/discussions)
- ⭐ **Star Us**: If you find this useful, please star the repo!

---

<div align="center">

**Made with ❤️ for businesses worldwide**

[⭐ Star on GitHub](https://github.com/YOUR_USERNAME/deepvision-counter) • [📖 Documentation](docs/) • [🐛 Report Bug](https://github.com/YOUR_USERNAME/deepvision-counter/issues)

</div>
