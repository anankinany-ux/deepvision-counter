# Developer Documentation
## Customer Counter Pro - Technical Reference

Complete technical documentation for developers and contributors.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [Core Components](#core-components)
5. [API Reference](#api-reference)
6. [Development Setup](#development-setup)
7. [Testing](#testing)
8. [Contributing](#contributing)

---

## Project Structure

```
ai-camera-project/
├── counter_modern.py         # Main application file
├── requirements.txt          # Python dependencies
├── yolov8n.pt               # YOLO model weights
│
├── config/                   # Configuration files
│   └── settings.yaml
│
├── data/                     # Application data
│   ├── customer_analytics.db
│   ├── counter_data.db
│   └── logs/
│
├── models/                   # AI models
│   └── yolov8n.pt
│
├── assets/                   # Icons and resources
│   ├── icon.icns            # Mac icon
│   └── icon.ico             # Windows icon
│
├── build_mac.sh             # Mac build script
├── build_windows.bat        # Windows build script
├── create_dmg.sh            # DMG creator
├── installer_windows.iss    # Windows installer
├── counter_modern.spec      # PyInstaller spec
│
├── README.md                # Project overview
├── USER_MANUAL.md           # User documentation
├── DEVELOPER_DOCS.md        # This file
├── DEPLOYMENT_GUIDE.md      # Deployment info
├── CODE_PROTECTION_GUIDE.md # Security guide
├── DISTRIBUTION_SETUP.md    # Sales & marketing
└── VIDEO_TUTORIAL_SCRIPTS.md # Tutorial scripts
```

---

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────┐
│           User Interface (Tkinter)           │
│  ┌─────────┐ ┌─────────┐ ┌──────────────┐ │
│  │ Controls│ │ Video   │ │  Statistics  │ │
│  └─────────┘ └─────────┘ └──────────────┘ │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│         Application Logic Layer             │
│  ┌──────────────┐  ┌──────────────────────┐│
│  │ ModernCounter│  │  CustomerTracker     ││
│  └──────────────┘  └──────────────────────┘│
│  ┌──────────────┐  ┌──────────────────────┐│
│  │ AlertManager │  │  ToolTip / UI Helpers││
│  └──────────────┘  └──────────────────────┘│
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│            AI/Processing Layer              │
│  ┌──────────────┐  ┌──────────────────────┐│
│  │ YOLO Model   │  │  Tracking Algorithm  ││
│  │ (Ultralytics)│  │  (ByteTrack/SORT)    ││
│  └──────────────┘  └──────────────────────┘│
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│            Data/Storage Layer               │
│  ┌──────────────┐  ┌──────────────────────┐│
│  │ SQLite DB    │  │  Config Files (JSON) ││
│  └──────────────┘  └──────────────────────┘│
└─────────────────────────────────────────────┘
```

### Threading Model

```
Main Thread (Tkinter GUI)
    ├── Video Preview Thread
    ├── Video Processing Thread (when counting)
    ├── Uptime Update Thread (when counting)
    └── AI Model Loading Thread (at startup)
```

### Data Flow

```
Camera → OpenCV → YOLO Detection → Tracking → Line Crossing
                                               Detection → Database
                                                         ↓
                      GUI ← Analytics ← CustomerTracker ← 
```

---

## Database Schema

### customer_sessions Table

Stores individual customer visit sessions.

```sql
CREATE TABLE customer_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER,              -- Tracking ID from AI
    entry_time TIMESTAMP,          -- ISO format
    exit_time TIMESTAMP,           -- ISO format
    duration_seconds INTEGER,      -- Visit duration
    date DATE,                     -- ISO format (YYYY-MM-DD)
    hour INTEGER,                  -- 0-23
    session_number INTEGER         -- Counter session number
);

-- Indexes for performance
CREATE INDEX idx_date ON customer_sessions(date);
CREATE INDEX idx_track_id ON customer_sessions(track_id);
CREATE INDEX idx_hour ON customer_sessions(hour);
```

### Example Data

| id  | track_id | entry_time           | exit_time            | duration_seconds | date       | hour | session_number |
|-----|----------|----------------------|----------------------|------------------|------------|------|----------------|
| 1   | 5        | 2024-12-19T10:15:23  | 2024-12-19T10:28:45  | 802              | 2024-12-19 | 10   | 1              |
| 2   | 12       | 2024-12-19T10:16:01  | 2024-12-19T10:19:30  | 209              | 2024-12-19 | 10   | 1              |

---

## Core Components

### 1. ModernCounter Class

Main application class managing the GUI and application state.

**Key Attributes:**
- `root`: Tkinter root window
- `is_running`: Boolean counting state
- `cap`: OpenCV VideoCapture object
- `tracks`: Dictionary of tracked objects
- `count_in`, `count_out`: Counter values
- `customer_tracker`: CustomerTracker instance
- `alert_manager`: AlertManager instance

**Key Methods:**
- `setup_modern_ui()`: Initialize GUI
- `start_counting()`: Begin counting session
- `stop_counting()`: End counting session
- `process_video()`: Main video processing loop
- `check_crossing()`: Detect line crossings

### 2. CustomerTracker Class

Manages customer data and analytics.

**Database Operations:**
- `customer_entered(track_id, session_number)`: Record entry
- `customer_exited(track_id)`: Record exit
- `get_current_occupancy()`: Get live count
- `get_today_analytics()`: Get today's stats

**Analytics Methods:**
- `get_hourly_traffic(date)`: Hourly breakdown
- `get_daily_traffic(days)`: Multi-day trends
- `get_peak_hours()`: Identify busiest times
- `get_vip_customers()`: Frequent visitors
- `get_traffic_patterns()`: Pattern analysis
- `predict_next_hour_traffic()`: Simple prediction

**Data Export:**
- `export_to_csv(filepath, date_range)`: Export to CSV

### 3. AlertManager Class

Manages smart alerts and notifications.

**Configuration:**
- `occupancy_enabled`, `occupancy_threshold`
- `long_dwell_enabled`, `long_dwell_minutes`
- `peak_hour_enabled`, `peak_hour_threshold`

**Alert Methods:**
- `check_occupancy_alert(current_occupancy)`
- `check_long_dwell_alert(customer_tracker)`
- `check_peak_hour_alert(hourly_count)`

### 4. ToolTip Class

Provides hover tooltips for UI elements.

**Usage:**
```python
button = tk.Button(parent, text="Click me")
ToolTip(button, "This button does something cool")
```

---

## API Reference

### Line Crossing Detection

```python
def check_crossing(self, x1, y1, x2, y2):
    """
    Check if movement from (x1, y1) to (x2, y2) crosses the counting line.
    
    Args:
        x1, y1: Previous position
        x2, y2: Current position
    
    Returns:
        (crossed: bool, direction: int)
        direction: 1 for IN, -1 for OUT
    """
```

**Algorithm:**
Uses line segment intersection with cross product for direction.

### Coordinate Conversion

```python
def canvas_to_frame_coords(self, cx, cy):
    """Convert canvas coordinates to frame coordinates"""
    
def frame_to_canvas_coords(self, fx, fy):
    """Convert frame coordinates to canvas coordinates"""
```

**Needed because:**
- Canvas size != Frame size (video gets resized)
- Line is drawn on frame coordinates
- Mouse events are in canvas coordinates

### Performance Optimization

```python
# Frame skipping
self.frame_skip_rate = 2  # Process every Nth frame

# Frame rate limiting
self.min_frame_interval = 1.0 / 30  # 30 FPS max

# Analytics caching
self.cache_duration = 5  # Cache for 5 seconds
```

---

## Development Setup

### Prerequisites

```bash
# Python 3.8+
python --version

# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

See `requirements.txt`:
- opencv-python>=4.8.0
- ultralytics>=8.0.0
- Pillow>=10.0.0
- matplotlib>=3.7.0
- numpy>=1.24.0
- lap>=0.5.0
- PyYAML>=6.0

### Running in Development

```bash
# Run directly
python counter_modern.py

# Or use launcher
chmod +x "Launch Modern.command"
./"Launch Modern.command"
```

### Debug Mode

Enable console output for debugging:

```python
# In counter_modern.py, change:
console=False  # to
console=True   # in PyInstaller spec
```

---

## Testing

### Manual Testing Checklist

#### Camera & Video
- [ ] Camera 0 works
- [ ] Camera 1 works (if external)
- [ ] Video preview smooth
- [ ] No memory leaks during long sessions

#### Counting Accuracy
- [ ] Single person detected and counted
- [ ] Multiple people counted correctly
- [ ] Direction (IN/OUT) correct
- [ ] No double counting
- [ ] Line position saves and loads

#### UI/UX
- [ ] All buttons work
- [ ] Tooltips appear
- [ ] Keyboard shortcuts functional
- [ ] Light/dark themes work
- [ ] Animations smooth

#### Analytics
- [ ] CSV export works
- [ ] Reports display correctly
- [ ] Alerts trigger appropriately
- [ ] Database saves data

#### Performance
- [ ] CPU usage reasonable (<50%)
- [ ] No UI freezing
- [ ] Frame rate stable
- [ ] Memory usage stable

### Automated Testing

Create `test_counter.py`:

```python
import unittest
from counter_modern import ModernCounter, CustomerTracker

class TestCustomerTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = CustomerTracker()
    
    def test_customer_entry(self):
        entry_time = self.tracker.customer_entered(1, 1)
        self.assertIsNotNone(entry_time)
        self.assertEqual(self.tracker.get_current_occupancy(), 1)
    
    def test_customer_exit(self):
        self.tracker.customer_entered(1, 1)
        exit_data = self.tracker.customer_exited(1)
        self.assertIsNotNone(exit_data)
        self.assertEqual(self.tracker.get_current_occupancy(), 0)

if __name__ == '__main__':
    unittest.main()
```

---

## Contributing

### Code Style

Follow PEP 8 with these specifics:
- Indentation: 4 spaces
- Line length: 100 characters max
- Docstrings: Google style

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add: feature description"

# Push and create PR
git push origin feature/your-feature-name
```

### Commit Message Convention

- `Add:` New feature
- `Fix:` Bug fix
- `Update:` Modify existing feature
- `Refactor:` Code restructuring
- `Docs:` Documentation changes
- `Test:` Add/update tests

### Pull Request Process

1. Ensure code passes all tests
2. Update documentation
3. Add entry to CHANGELOG.md
4. Request review from maintainer
5. Address review feedback
6. Squash commits if requested

---

## Performance Optimization Tips

### 1. Frame Processing

```python
# Skip frames for better performance
if frame_count % self.frame_skip_rate != 0:
    continue  # Skip AI processing

# Reduce resolution if needed
frame = cv2.resize(frame, (960, 540))  # From 1920x1080
```

### 2. Database Queries

```python
# Cache frequently accessed data
if time.time() - self.last_cache_time < self.cache_duration:
    return self.cached_data

# Use indexes for fast lookups
CREATE INDEX idx_date ON customer_sessions(date);
```

### 3. Memory Management

```python
# Periodic cleanup
def cleanup_old_tracking_data(self):
    # Remove old crossings
    old_keys = [k for k, v in self.recent_crossings.items() 
               if current_time - v > 10]
    for key in old_keys:
        del self.recent_crossings[key]
```

---

## Troubleshooting Development Issues

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check virtual environment
which python  # Should point to venv
```

### Camera Access Issues

```bash
# List available cameras
python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"
```

### PyInstaller Build Errors

```bash
# Clean build
rm -rf build dist *.spec

# Verbose build to see errors
pyinstaller --debug all counter_modern.spec
```

---

## Future Enhancements

Planned features and improvements:

1. **Multi-Camera Support**
   - Track across multiple entry points
   - Consolidated analytics

2. **Cloud Sync** (Optional)
   - Backup data to cloud
   - Multi-location management

3. **Mobile App**
   - View real-time stats
   - Receive push notifications

4. **Advanced AI**
   - Gender/age estimation (optional)
   - Emotion detection
   - Dwell time heatmaps

5. **Integrations**
   - POS system integration
   - Calendar/booking systems
   - CRM platforms

---

## Resources

### Documentation
- [OpenCV Docs](https://docs.opencv.org/)
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [Tkinter Reference](https://docs.python.org/3/library/tkinter.html)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### Community
- GitHub Issues: Report bugs
- Discussions: Ask questions
- Discord: Join the community

### Learning
- "Python GUI Programming with Tkinter" by Alan D. Moore
- "Hands-On Image Processing with Python" by Sandipan Dey
- OpenCV course on Udemy

---

**Questions?** Create an issue on GitHub or email dev@customercounterpro.com

**Last Updated:** December 2024 | **Version:** 1.0.0

