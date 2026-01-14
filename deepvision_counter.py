#!/usr/bin/env python3
"""
DeepVision Counter - Modern Stable Version
Built on stable foundation with professional features
Cross-platform: Works on Windows, macOS, and Linux
"""

import tkinter as tk
from tkinter import messagebox, ttk
import cv2
import threading
from datetime import datetime
import time
from ultralytics import YOLO
import os
import sys
import json
import platform

# Global model
model = None

def get_system_font():
    """Get the best available font for the current OS"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return "SF Pro Display"
    elif system == "Windows":
        return "Segoe UI"
    else:  # Linux
        return "Ubuntu"

def get_mono_font():
    """Get the best monospace font for the current OS"""
    system = platform.system()
    if system == "Darwin":
        return "SF Mono"
    elif system == "Windows":
        return "Consolas"
    else:
        return "Ubuntu Mono"

# Cross-platform fonts
FONT_FAMILY = get_system_font()
MONO_FONT = get_mono_font()

class DeepVisionCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("DeepVision Counter")
        self.root.geometry("1500x950")
        
        # Load settings
        self.load_settings()
        
        # Apply theme
        self.apply_theme()
        
        # State
        self.is_running = False
        self.cap = None
        self.count_in = 0
        self.count_out = 0
        self.tracks = {}
        self.line_y = 400  # Horizontal line position
        
        # Load AI model in background
        self.model_loaded = False
        threading.Thread(target=self.load_model, daemon=True).start()
        
        self.create_ui()
        
    def load_settings(self):
        """Load user settings from file"""
        self.settings_file = "deepvision_settings.json"
        default_settings = {
            "language": "en",
            "theme": "dark",
            "camera_index": 0,
            "confidence": 0.45,
            "show_fps": True,
            "save_data": True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = {**default_settings, **json.load(f)}
            else:
                self.settings = default_settings
        except:
            self.settings = default_settings
        
        # Language translations
        self.translations = {
            'en': {
                'start': 'START',
                'stop': 'STOP',
                'reset': 'RESET',
                'settings': 'SETTINGS',
                'live_feed': 'LIVE FEED',
                'statistics': 'STATISTICS',
                'in': 'IN',
                'out': 'OUT',
                'ai_ready': '✅ AI Model Ready',
                'loading': '⏳ Loading AI Model...',
                'counting_active': '🔴 COUNTING ACTIVE',
                'stopped': '⏸ Stopped',
                'counters_reset': '🔄 Counters Reset',
                'camera_error': 'Camera Error',
                'camera_error_msg': 'Cannot access camera.\n\nSolutions:\n• Grant camera permissions in System Settings\n• Close other apps using the camera',
                'not_ready': 'Not Ready',
                'model_loading': 'AI model is still loading. Please wait...',
                # Settings
                'app_settings': 'Application Settings',
                'language_label': 'Language:',
                'theme_label': 'Theme:',
                'camera_label': 'Camera:',
                'confidence_label': 'Detection Confidence:',
                'show_fps_label': 'Show FPS:',
                'save_data_label': 'Save Count Data:',
                'save_settings': 'Save Settings',
                'close': 'Close',
                'light': 'Light',
                'dark': 'Dark',
            },
            'he': {
                'start': 'התחל',
                'stop': 'עצור',
                'reset': 'אפס',
                'settings': 'הגדרות',
                'live_feed': 'שידור חי',
                'statistics': 'סטטיסטיקות',
                'in': 'נכנסו',
                'out': 'יצאו',
                'ai_ready': '✅ AI מודל מוכן',
                'loading': '⏳ טוען מודל AI...',
                'counting_active': '🔴 ספירה פעילה',
                'stopped': '⏸ נעצר',
                'counters_reset': '🔄 מונים אופסו',
                'camera_error': 'שגיאת מצלמה',
                'camera_error_msg': 'לא ניתן לגשת למצלמה.\n\nפתרונות:\n• אשר הרשאות מצלמה בהגדרות המערכת\n• סגור אפליקציות אחרות המשתמשות במצלמה',
                'not_ready': 'לא מוכן',
                'model_loading': 'מודל ה-AI עדיין נטען. אנא המתן...',
                # Settings
                'app_settings': 'הגדרות האפליקציה',
                'language_label': 'שפה:',
                'theme_label': 'ערכת נושא:',
                'camera_label': 'מצלמה:',
                'confidence_label': 'רמת זיהוי:',
                'show_fps_label': 'הצג FPS:',
                'save_data_label': 'שמור נתונים:',
                'save_settings': 'שמור הגדרות',
                'close': 'סגור',
                'light': 'בהיר',
                'dark': 'כהה',
            }
        }
    
    def get_text(self, key):
        """Get translated text"""
        lang = self.settings.get('language', 'en')
        return self.translations[lang].get(key, key)
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def apply_theme(self):
        """Apply color theme"""
        if self.settings['theme'] == 'dark':
            self.colors = {
                'bg': '#0d0d12',
                'surface': '#1a1a2e',
                'card': '#16213e',
                'accent': '#d946ef',
                'success': '#22c55e',
                'danger': '#f43f5e',
                'warning': '#eab308',
                'text': '#ffffff',
                'text_dim': '#a0a0a0',
            }
        else:
            self.colors = {
                'bg': '#f5f5f5',
                'surface': '#ffffff',
                'card': '#e8e8e8',
                'accent': '#c026d3',
                'success': '#16a34a',
                'danger': '#dc2626',
                'warning': '#ca8a04',
                'text': '#1a1a1a',
                'text_dim': '#6b6b6b',
            }
        
        self.root.configure(bg=self.colors['bg'])
        
    def load_model(self):
        """Load YOLO model in background"""
        global model
        try:
            model = YOLO("yolov8n.pt")
            self.model_loaded = True
            self.safe_update_status(self.get_text('ai_ready'), self.colors['success'])
        except Exception as e:
            self.safe_update_status(f"❌ Model Error: {str(e)[:30]}", self.colors['danger'])
    
    def safe_update_status(self, text, color):
        """Thread-safe status update"""
        try:
            if self.root.winfo_exists():
                self.root.after(0, lambda: self.status_label.config(text=text, fg=color))
        except:
            pass
    
    def create_ui(self):
        """Create modern UI with 2025 design trends"""
        # Top bar with glassmorphism effect
        top_bar = tk.Frame(self.root, bg=self.colors['surface'], height=90)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        
        # Left side - Logo
        left_frame = tk.Frame(top_bar, bg=self.colors['surface'])
        left_frame.pack(side=tk.LEFT, padx=30, pady=20)
        
        tk.Label(left_frame, text="DEEP VISION", bg=self.colors['surface'], 
                fg=self.colors['accent'], font=(FONT_FAMILY, 24, 'bold')).pack()
        
        # Right side - Controls
        controls_frame = tk.Frame(top_bar, bg=self.colors['surface'])
        controls_frame.pack(side=tk.RIGHT, padx=30, pady=15)
        
        # All buttons in one row for visibility
        btn_row = tk.Frame(controls_frame, bg=self.colors['surface'])
        btn_row.pack()
        
        self.start_btn = self.create_button(btn_row, self.get_text('start'), 
                                                   self.start_counting, self.colors['success'])
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = self.create_button(btn_row, self.get_text('stop'), 
                                                  self.stop_counting, self.colors['danger'])
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.config(state='disabled')
        
        reset_btn = self.create_button(btn_row, self.get_text('reset'), 
                                              self.reset_counts, self.colors['warning'])
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Settings button - BRIGHT MAGENTA to stand out
        settings_btn = self.create_button(btn_row, self.get_text('settings'), 
                                                 self.show_settings, self.colors['accent'])
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Language toggle button - BRIGHT MAGENTA
        lang_btn = self.create_button(btn_row, 
                                            'EN' if self.settings['language'] == 'he' else 'עב',
                                            self.toggle_language, self.colors['accent'])
        lang_btn.pack(side=tk.LEFT, padx=5)
        self.lang_btn = lang_btn
        
        # Main content area
        content = tk.Frame(self.root, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Left: Video feed with modern card
        video_card = tk.Frame(content, bg=self.colors['surface'], 
                             highlightthickness=2, highlightbackground=self.colors['accent'])
        video_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Video header
        video_header = tk.Frame(video_card, bg=self.colors['surface'], height=50)
        video_header.pack(fill=tk.X)
        video_header.pack_propagate(False)
        
        tk.Label(video_header, text=self.get_text('live_feed'), 
                bg=self.colors['surface'], fg=self.colors['text'],
                font=(FONT_FAMILY, 16, 'bold')).pack(side=tk.LEFT, padx=20, pady=15)
        
        # FPS counter (right aligned)
        self.fps_label = tk.Label(video_header, text="FPS: --", 
                                 bg=self.colors['surface'], fg=self.colors['text_dim'],
                                 font=(MONO_FONT, 11))
        self.fps_label.pack(side=tk.RIGHT, padx=20)
        
        # Video display
        self.video_label = tk.Label(video_card, bg='black')
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Right: Statistics with modern cards
        stats_card = tk.Frame(content, bg=self.colors['surface'], width=350,
                             highlightthickness=2, highlightbackground=self.colors['accent'])
        stats_card.pack(side=tk.RIGHT, fill=tk.Y)
        stats_card.pack_propagate(False)
        
        # Stats header
        tk.Label(stats_card, text=self.get_text('statistics'), 
                bg=self.colors['surface'], fg=self.colors['text'],
                font=(FONT_FAMILY, 16, 'bold')).pack(pady=20)
        
        # IN counter card (with subtle shadow effect)
        in_container = tk.Frame(stats_card, bg=self.colors['surface'])
        in_container.pack(fill=tk.X, padx=20, pady=15)
        
        in_card = tk.Frame(in_container, bg=self.colors['success'], height=120)
        in_card.pack(fill=tk.X)
        in_card.pack_propagate(False)
        
        tk.Label(in_card, text=self.get_text('in'), bg=self.colors['success'], 
                fg='white', font=(FONT_FAMILY, 14, 'bold')).pack(pady=(15, 5))
        self.in_label = tk.Label(in_card, text="0", bg=self.colors['success'], 
                                fg='white', font=(FONT_FAMILY, 42, 'bold'))
        self.in_label.pack()
        
        # OUT counter card
        out_container = tk.Frame(stats_card, bg=self.colors['surface'])
        out_container.pack(fill=tk.X, padx=20, pady=15)
        
        out_card = tk.Frame(out_container, bg=self.colors['danger'], height=120)
        out_card.pack(fill=tk.X)
        out_card.pack_propagate(False)
        
        tk.Label(out_card, text=self.get_text('out'), bg=self.colors['danger'], 
                fg='white', font=(FONT_FAMILY, 14, 'bold')).pack(pady=(15, 5))
        self.out_label = tk.Label(out_card, text="0", bg=self.colors['danger'], 
                                 fg='white', font=(FONT_FAMILY, 42, 'bold'))
        self.out_label.pack()
        
        # NET counter (currently inside)
        net_container = tk.Frame(stats_card, bg=self.colors['surface'])
        net_container.pack(fill=tk.X, padx=20, pady=15)
        
        net_card = tk.Frame(net_container, bg=self.colors['accent'], height=90)
        net_card.pack(fill=tk.X)
        net_card.pack_propagate(False)
        
        tk.Label(net_card, text="CURRENTLY INSIDE", bg=self.colors['accent'], 
                fg='white', font=(FONT_FAMILY, 12, 'bold')).pack(pady=(10, 2))
        self.net_label = tk.Label(net_card, text="0", bg=self.colors['accent'], 
                                 fg='white', font=(FONT_FAMILY, 32, 'bold'))
        self.net_label.pack()
        
        # Modern status bar
        status_bar = tk.Frame(self.root, bg=self.colors['surface'], height=45)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(status_bar, text=self.get_text('loading'),
                                     bg=self.colors['surface'], fg=self.colors['warning'],
                                     font=(FONT_FAMILY, 12))
        self.status_label.pack(side=tk.LEFT, padx=25, pady=12)
    
    def create_button(self, parent, text, command, color):
        """Create a canvas-based button (macOS can't override these colors!)"""
        canvas = tk.Canvas(parent, width=130, height=48, bg=self.colors['surface'],
                          highlightthickness=0, cursor='hand2')
        
        # Draw button rectangle
        rect = canvas.create_rectangle(3, 3, 127, 45, fill=color, outline='',
                                      width=0, tags='btn_bg')
        txt = canvas.create_text(65, 24, text=text, fill='white',
                                font=(FONT_FAMILY, 12, 'bold'), tags='btn_text')
        
        # Store state
        canvas.btn_enabled = True
        canvas.btn_color = color
        canvas.btn_command = command
        
        # Click handler
        def on_click(e):
            if canvas.btn_enabled and canvas.btn_command:
                canvas.btn_command()
        
        # Hover effects
        def on_enter(e):
            if canvas.btn_enabled:
                lighter = self.lighten_color(color)
                canvas.itemconfig('btn_bg', fill=lighter)
        
        def on_leave(e):
            if canvas.btn_enabled:
                canvas.itemconfig('btn_bg', fill=color)
        
        canvas.bind('<Button-1>', on_click)
        canvas.bind('<Enter>', on_enter)
        canvas.bind('<Leave>', on_leave)
        
        # Add config method for compatibility
        def config(state=None, **kwargs):
            if state is not None:
                if state == 'disabled':
                    canvas.btn_enabled = False
                    canvas.itemconfig('btn_bg', fill='#555555')
                    canvas.itemconfig('btn_text', fill='#888888')
                    canvas.config(cursor='')
                else:
                    canvas.btn_enabled = True
                    canvas.itemconfig('btn_bg', fill=color)
                    canvas.itemconfig('btn_text', fill='white')
                    canvas.config(cursor='hand2')
        
        canvas.config = config
        
        return canvas
    
    def lighten_color(self, color):
        """Lighten a hex color for hover effects"""
        if color == self.colors['success'] or color == "#22c55e": return "#4ade80"
        if color == self.colors['danger'] or color == "#f43f5e": return "#fb7185"
        if color == self.colors['warning'] or color == "#eab308": return "#fde047"
        if color == self.colors['accent'] or color == "#d946ef": return "#e879f9"
        return color
    
    def toggle_language(self):
        """Toggle between English and Hebrew"""
        self.settings['language'] = 'he' if self.settings['language'] == 'en' else 'en'
        self.save_settings()
        
        # Show message
        msg = "Language updated! Restart the app to see changes." if self.settings['language'] == 'en' else "השפה עודכנה! הפעל מחדש את האפליקציה."
        messagebox.showinfo("Language", msg)
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('app_settings'))
        dialog.geometry("450x500")
        dialog.configure(bg=self.colors['surface'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (225)
        y = (dialog.winfo_screenheight() // 2) - (250)
        dialog.geometry(f"450x500+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg=self.colors['accent'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=self.get_text('app_settings'), 
                bg=self.colors['accent'], fg='white',
                font=(FONT_FAMILY, 18, 'bold')).pack(pady=18)
        
        # Content with padding
        content = tk.Frame(dialog, bg=self.colors['surface'])
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Language
        lang_frame = tk.Frame(content, bg=self.colors['surface'])
        lang_frame.pack(fill=tk.X, pady=10)
        tk.Label(lang_frame, text=self.get_text('language_label'), 
                bg=self.colors['surface'], fg=self.colors['text'],
                font=(FONT_FAMILY, 12)).pack(side=tk.LEFT)
        lang_combo = ttk.Combobox(lang_frame, values=['English', 'עברית'], 
                                 state='readonly', width=15)
        lang_combo.current(0 if self.settings['language'] == 'en' else 1)
        lang_combo.pack(side=tk.RIGHT)
        
        # Theme
        theme_frame = tk.Frame(content, bg=self.colors['surface'])
        theme_frame.pack(fill=tk.X, pady=10)
        tk.Label(theme_frame, text=self.get_text('theme_label'), 
                bg=self.colors['surface'], fg=self.colors['text'],
                font=(FONT_FAMILY, 12)).pack(side=tk.LEFT)
        theme_combo = ttk.Combobox(theme_frame, 
                                   values=[self.get_text('dark'), self.get_text('light')], 
                                   state='readonly', width=15)
        theme_combo.current(0 if self.settings['theme'] == 'dark' else 1)
        theme_combo.pack(side=tk.RIGHT)
        
        # Camera
        cam_frame = tk.Frame(content, bg=self.colors['surface'])
        cam_frame.pack(fill=tk.X, pady=10)
        tk.Label(cam_frame, text=self.get_text('camera_label'), 
                bg=self.colors['surface'], fg=self.colors['text'],
                font=(FONT_FAMILY, 12)).pack(side=tk.LEFT)
        cam_combo = ttk.Combobox(cam_frame, values=['0', '1', '2'], 
                                state='readonly', width=15)
        cam_combo.set(str(self.settings['camera_index']))
        cam_combo.pack(side=tk.RIGHT)
        
        # Confidence
        conf_frame = tk.Frame(content, bg=self.colors['surface'])
        conf_frame.pack(fill=tk.X, pady=15)
        tk.Label(conf_frame, text=self.get_text('confidence_label'), 
                bg=self.colors['surface'], fg=self.colors['text'],
                font=(FONT_FAMILY, 12)).pack(anchor=tk.W)
        conf_var = tk.DoubleVar(value=self.settings['confidence'])
        conf_scale = tk.Scale(conf_frame, from_=0.1, to=0.9, resolution=0.05,
                             orient=tk.HORIZONTAL, variable=conf_var,
                             bg=self.colors['surface'], fg=self.colors['text'],
                             highlightthickness=0, length=350)
        conf_scale.pack(fill=tk.X, pady=5)
        
        # Checkboxes
        fps_var = tk.BooleanVar(value=self.settings['show_fps'])
        tk.Checkbutton(content, text=self.get_text('show_fps_label'),
                      variable=fps_var, bg=self.colors['surface'],
                      fg=self.colors['text'], selectcolor=self.colors['card'],
                      font=(FONT_FAMILY, 11)).pack(anchor=tk.W, pady=8)
        
        save_var = tk.BooleanVar(value=self.settings['save_data'])
        tk.Checkbutton(content, text=self.get_text('save_data_label'),
                      variable=save_var, bg=self.colors['surface'],
                      fg=self.colors['text'], selectcolor=self.colors['card'],
                      font=(FONT_FAMILY, 11)).pack(anchor=tk.W, pady=8)
        
        # Buttons at bottom
        btn_frame = tk.Frame(dialog, bg=self.colors['surface'])
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=25, pady=25)
        
        def save_and_close():
            # Update settings
            self.settings['language'] = 'en' if lang_combo.current() == 0 else 'he'
            self.settings['theme'] = 'dark' if theme_combo.current() == 0 else 'light'
            self.settings['camera_index'] = int(cam_combo.get())
            self.settings['confidence'] = conf_var.get()
            self.settings['show_fps'] = fps_var.get()
            self.settings['save_data'] = save_var.get()
            self.save_settings()
            
            msg = "Settings saved! Restart app to apply all changes." if self.settings['language'] == 'en' else "ההגדרות נשמרו! הפעל מחדש להחלת שינויים."
            messagebox.showinfo("Success", msg)
            dialog.destroy()
        
        save_btn = self.create_button(btn_frame, self.get_text('save_settings'),
                                      save_and_close, self.colors['success'])
        save_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = self.create_button(btn_frame, self.get_text('close'),
                                       dialog.destroy, self.colors['danger'])
        close_btn.pack(side=tk.LEFT, padx=5)
    
    def start_counting(self):
        """Start people counting"""
        if not self.model_loaded:
            messagebox.showwarning("Not Ready", "AI model is still loading. Please wait...")
            return
        
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Camera Error", 
                    "Cannot access camera.\n\n" +
                    "Solutions:\n" +
                    "• Grant camera permissions in System Settings\n" +
                    "• Close other apps using the camera")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Camera error: {str(e)}")
            return
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.safe_update_status("🔴 COUNTING ACTIVE", "#22c55e")
        
        threading.Thread(target=self.process_video, daemon=True).start()
    
    def stop_counting(self):
        """Stop counting"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.safe_update_status("⏸ Stopped", "#eab308")
    
    def reset_counts(self):
        """Reset all counters"""
        self.count_in = 0
        self.count_out = 0
        self.tracks = {}
        self.update_display_counts()
        self.safe_update_status("🔄 Counters Reset", "#eab308")
    
    def process_video(self):
        """Main video processing loop"""
        global model
        
        while self.is_running:
            try:
                if not self.root.winfo_exists():
                    break
                
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Run YOLO detection
                results = model.track(frame, persist=True, verbose=False, conf=0.45)
                
                # Draw counting line
                h, w = frame.shape[:2]
                line_y = int(h * 0.5)  # Middle of frame
                cv2.line(frame, (0, line_y), (w, line_y), (255, 128, 0), 3)
                cv2.putText(frame, "IN", (10, line_y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                           0.8, (0, 255, 0), 2)
                cv2.putText(frame, "OUT", (10, line_y + 30), cv2.FONT_HERSHEY_SIMPLEX,
                           0.8, (0, 0, 255), 2)
                
                # Process detections
                if results and len(results) > 0 and results[0].boxes:
                    for box in results[0].boxes:
                        if int(box.cls[0]) != 0:  # Only people
                            continue
                        
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)),
                                    (0, 255, 0), 2)
                        
                        # Track crossing
                        if hasattr(box, 'id') and box.id is not None:
                            track_id = int(box.id[0])
                            
                            if track_id not in self.tracks:
                                self.tracks[track_id] = cy
                            else:
                                prev_y = self.tracks[track_id]
                                
                                # Check if crossed line
                                if prev_y < line_y and cy >= line_y:
                                    self.count_in += 1
                                    self.safe_update_counts()
                                elif prev_y > line_y and cy <= line_y:
                                    self.count_out += 1
                                    self.safe_update_counts()
                                
                                self.tracks[track_id] = cy
                
                # Display frame
                self.display_frame(frame)
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"Processing error: {e}")
                break
        
        if self.cap:
            self.cap.release()
    
    def display_frame(self, frame):
        """Display video frame"""
        try:
            if not self.root.winfo_exists():
                return
            
            import cv2
            from PIL import Image, ImageTk
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (800, 600))
            img = Image.fromarray(frame_resized)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.root.after(0, lambda: self.update_video_label(imgtk))
        except:
            pass
    
    def update_video_label(self, imgtk):
        """Update video label (main thread)"""
        try:
            if self.video_label.winfo_exists():
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)
        except:
            pass
    
    def safe_update_counts(self):
        """Thread-safe counter update"""
        try:
            if self.root.winfo_exists():
                self.root.after(0, self.update_display_counts)
        except:
            pass
    
    def update_display_counts(self):
        """Update counter display (main thread)"""
        try:
            if self.in_label.winfo_exists():
                self.in_label.config(text=str(self.count_in))
            if self.out_label.winfo_exists():
                self.out_label.config(text=str(self.count_out))
        except:
            pass

def main():
    root = tk.Tk()
    app = DeepVisionCounter(root)
    root.mainloop()

if __name__ == "__main__":
    main()

