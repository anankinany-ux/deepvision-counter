# Customer Counter Pro

**Modern AI-powered people counting system with real-time tracking**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-Commercial-orange)

---

## 🚀 Quick Start

### Launch the App

**Double-click:**
```
Launch Modern.command
```

**Or run from terminal:**
```bash
cd "/Users/anankinany/Desktop/ai camera project"
.venv/bin/python counter_modern.py
```

---

## ✨ Features

### 🎯 **Core Functionality**
- ✅ Real-time person detection using YOLO AI
- ✅ Accurate IN/OUT counting with track IDs
- ✅ Adjustable counting line (any position, any angle)
- ✅ Lock/Unlock line to prevent accidental changes
- ✅ Flip IN/OUT direction with one click
- ✅ Session tracking with duration timer
- ✅ Live statistics dashboard

### 🎨 **Modern Design**
- ✅ Ultra-modern 2025 UI design
- ✅ Dark theme (easy on eyes)
- ✅ Beautiful SF Pro fonts
- ✅ Color-coded statistics cards
- ✅ Smooth animations
- ✅ Professional layout

### 🔒 **Privacy & Performance**
- ✅ 100% offline operation
- ✅ No data sent to cloud
- ✅ Fast local AI processing
- ✅ Real-time FPS display
- ✅ Optimized for accuracy

---

## 📊 How It Works

1. **Position the Line**
   - Drag the blue circles to position your counting line
   - Place it where people cross (doorway, hallway, etc.)

2. **Lock the Line**
   - Click 🔓 button to lock (prevents accidental moves)
   - Button turns red 🔒 when locked

3. **Start Counting**
   - Click green **START** button
   - Watch people get detected (green boxes with #IDs)
   - Counters update when people cross the line

4. **Monitor Results**
   - **TOTAL TRAFFIC** - Blue card (everyone counted)
   - **IN** - Green card (people entering)
   - **OUT** - Red card (people leaving)
   - **CURRENTLY INSIDE** - Orange card (IN minus OUT)

5. **Session Info**
   - Session number increments each time you start
   - Duration timer shows how long you've been counting
   - Direction shows if IN/OUT is normal or reversed

---

## 🎛️ Controls

### Top Bar
- **CAMERA** - Select camera (0, 1, or 2)
- **START** - Begin counting
- **STOP** - Stop counting
- **🔓/🔒** - Lock/Unlock line
- **⇄** - Flip IN/OUT direction
- **↻** - Reset all counters

### Counting Line
- **Blue circles** - Draggable handles (numbered 1 and 2)
- **Blue line** - The counting boundary
- **IN/OUT labels** - Show which side is which

---

## 📁 Project Structure

```
ai camera project/
├── counter_modern.py          # Main application
├── Launch Modern.command      # Quick launcher
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .venv/                     # Virtual environment
└── models/                    # AI models (auto-downloaded)
```

---

## 🔧 Technical Details

### Requirements
- Python 3.8+
- OpenCV
- Ultralytics YOLO
- Tkinter (included with Python)
- PIL/Pillow

### AI Model
- YOLOv8n (nano) - Fast and accurate
- Pretrained on COCO dataset
- Person detection class (ID: 0)
- Real-time tracking with persistent IDs

### Camera Support
- USB webcams
- Built-in laptop cameras
- Multiple camera support (switch between 0, 1, 2)

---

## 💡 Tips for Best Results

### Line Placement
- Position line where people **fully cross through**
- Avoid areas where people might stop or turn around
- For doorways: horizontal line across the doorway
- For hallways: vertical line across the corridor

### Direction Setup
- **IN** should be the direction people enter
- **OUT** should be the direction people leave
- Use **FLIP** button if it's counting backwards
- Direction is shown in Session Info panel

### Accuracy Tips
- Good lighting improves detection
- Camera should have clear view of counting area
- Lock the line before starting to count
- Test with a few people first to verify direction

---

## 🎯 Use Cases

### Retail
- Count customers entering/leaving store
- Monitor peak hours
- Track occupancy levels

### Events
- Count attendees at entrances
- Monitor crowd flow
- Manage capacity limits

### Offices
- Track conference room usage
- Monitor workspace occupancy
- Analyze traffic patterns

### General
- Any space where you need to count people
- Entry/exit monitoring
- Occupancy management

---

## 🆘 Troubleshooting

### Camera Not Working
- Make sure camera is plugged in
- Close other apps using camera (Zoom, Teams, etc.)
- Try different camera number (0, 1, or 2)
- Check System Settings → Privacy → Camera permissions

### AI Model Loading Slowly
- First launch downloads the model (~6MB)
- Subsequent launches are faster
- Wait for "Ready to count" status

### Counting Not Accurate
- Reposition the line
- Lock the line before counting
- Check if direction needs flipping
- Ensure good lighting

### App Won't Start
- Make sure virtual environment is activated
- Run: `.venv/bin/pip install -r requirements.txt`
- Check Python version (3.8+)

---

## 📝 Version History

### v1.0.0 (Current)
- Modern 2025 UI design
- Adjustable counting line with lock
- Real-time person tracking
- Session management
- Dark theme with beautiful fonts
- Professional statistics dashboard

---

## 🏆 Credits

**Built with:**
- YOLOv8 by Ultralytics
- OpenCV for computer vision
- Python & Tkinter for UI
- Modern design principles

---

## 📧 Support

For questions or issues, refer to the Quick Guide panel in the app.

---

**Customer Counter Pro** - Professional people counting made simple 🎯
