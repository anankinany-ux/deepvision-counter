"""
Main GUI window for Customer Counter Pro
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import threading

from src.camera import Camera
from src.detector import PersonDetector
from src.counter import PeopleCounter
from src.utils.database import CounterDatabase
from src.config import config
from src.utils.logger import logger


class MainWindow:
    """Main application window with video display and controls"""
    
    def __init__(self, root):
        """
        Initialize main window
        
        Parameters
        ----------
        root : tk.Tk
            Root Tkinter window
        """
        self.root = root
        self.root.title(config.get('app', 'window_title'))
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Application state
        self.is_running = False
        self.camera = None
        self.detector = None
        self.counter = None
        self.database = None
        self.session_id = None
        self.start_time = None
        
        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = datetime.now()
        
        # Setup GUI
        self.setup_ui()
        
        # Initialize components
        self.init_components()
        
        logger.info("Main window initialized")
    
    def setup_ui(self):
        """Setup user interface"""
        # Configure window
        self.root.geometry("1200x750")
        self.root.resizable(True, True)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left side - Video display
        self.setup_video_panel(main_frame)
        
        # Right side - Stats and controls
        self.setup_control_panel(main_frame)
        
        # Bottom - Status bar
        self.setup_status_bar(main_frame)
    
    def setup_video_panel(self, parent):
        """Setup video display panel"""
        video_frame = ttk.LabelFrame(parent, text="Live Video Feed", padding="5")
        video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Video canvas
        self.video_canvas = tk.Canvas(video_frame, bg='black', width=800, height=600)
        self.video_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Camera controls below video
        control_frame = ttk.Frame(video_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(control_frame, text="Camera:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.camera_var = tk.StringVar(value="0")
        self.camera_combo = ttk.Combobox(control_frame, textvariable=self.camera_var, 
                                         values=["0", "1", "2"], width=10, state='readonly')
        self.camera_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="● Start", command=self.start_counting)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="■ Stop", command=self.stop_counting, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
    
    def setup_control_panel(self, parent):
        """Setup control and stats panel"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Stats display
        stats_frame = ttk.LabelFrame(control_frame, text="Live Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Total counter
        ttk.Label(stats_frame, text="Total Counted:", font=('Arial', 10)).pack(anchor=tk.W)
        self.total_label = ttk.Label(stats_frame, text="0", font=('Arial', 24, 'bold'), foreground='blue')
        self.total_label.pack(anchor=tk.W, pady=(0, 10))
        
        # IN counter
        ttk.Label(stats_frame, text="IN:", font=('Arial', 10)).pack(anchor=tk.W)
        self.in_label = ttk.Label(stats_frame, text="0", font=('Arial', 18, 'bold'), foreground='green')
        self.in_label.pack(anchor=tk.W, pady=(0, 10))
        
        # OUT counter
        ttk.Label(stats_frame, text="OUT:", font=('Arial', 10)).pack(anchor=tk.W)
        self.out_label = ttk.Label(stats_frame, text="0", font=('Arial', 18, 'bold'), foreground='red')
        self.out_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Current (net) counter
        ttk.Label(stats_frame, text="Current Inside:", font=('Arial', 10)).pack(anchor=tk.W)
        self.current_label = ttk.Label(stats_frame, text="0", font=('Arial', 20, 'bold'), foreground='orange')
        self.current_label.pack(anchor=tk.W)
        
        # Control buttons
        button_frame = ttk.LabelFrame(control_frame, text="Controls", padding="10")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Reset Counter", command=self.reset_counter).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Export Report", command=self.export_report).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Settings", command=self.open_settings).pack(fill=tk.X, pady=5)
        
        # Session info
        info_frame = ttk.LabelFrame(control_frame, text="Session Info", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(info_frame, text="Uptime:", font=('Arial', 9)).pack(anchor=tk.W)
        self.uptime_label = ttk.Label(info_frame, text="00:00:00", font=('Arial', 10))
        self.uptime_label.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(info_frame, text="Today's Total:", font=('Arial', 9)).pack(anchor=tk.W)
        self.today_label = ttk.Label(info_frame, text="0", font=('Arial', 12))
        self.today_label.pack(anchor=tk.W)
    
    def setup_status_bar(self, parent):
        """Setup status bar at bottom"""
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.fps_label = ttk.Label(status_frame, text="FPS: 0")
        self.fps_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.time_label = ttk.Label(status_frame, text=datetime.now().strftime("%H:%M:%S"))
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        # Update clock
        self.update_clock()
    
    def init_components(self):
        """Initialize camera, detector, counter, and database"""
        try:
            # Initialize detector
            model_path = config.get('detection', 'model')
            confidence = config.get('detection', 'confidence_threshold')
            self.detector = PersonDetector(model_path, confidence)
            
            # Initialize database if enabled
            if config.get('data', 'save_to_database'):
                db_path = config.get('data', 'database_path')
                self.database = CounterDatabase(db_path)
            
            logger.info("Components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize components:\n{e}")
    
    def start_counting(self):
        """Start camera and counting"""
        if self.is_running:
            return
        
        try:
            # Get camera source
            camera_source = self.camera_var.get()
            try:
                camera_source = int(camera_source)
            except ValueError:
                pass  # Keep as string (file path or URL)
            
            # Initialize camera
            self.camera = Camera(camera_source)
            if not self.camera.connect():
                messagebox.showerror("Camera Error", "Failed to connect to camera")
                return
            
            # Initialize counter with frame dimensions
            line_pos = config.get('counting', 'line_position')
            direction = config.get('counting', 'direction')
            self.counter = PeopleCounter(
                line_position=line_pos,
                direction=direction,
                frame_height=self.camera.frame_height,
                frame_width=self.camera.frame_width
            )
            
            # Start database session
            if self.database:
                self.session_id = self.database.start_session()
            
            # Update UI state
            self.is_running = True
            self.start_time = datetime.now()
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.camera_combo.config(state='disabled')
            self.status_label.config(text="Running")
            
            # Start video processing thread
            self.process_thread = threading.Thread(target=self.process_video, daemon=True)
            self.process_thread.start()
            
            logger.info("Counting started")
            
        except Exception as e:
            logger.error(f"Error starting counting: {e}")
            messagebox.showerror("Start Error", f"Failed to start counting:\n{e}")
            self.is_running = False
    
    def stop_counting(self):
        """Stop camera and counting"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Wait for thread to finish
        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=2.0)
        
        # Release camera
        if self.camera:
            self.camera.release()
            self.camera = None
        
        # End database session
        if self.database and self.session_id:
            stats = self.counter.get_stats()
            self.database.end_session(self.session_id, stats['in'], stats['out'])
            self.session_id = None
        
        # Update UI state
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.camera_combo.config(state='readonly')
        self.status_label.config(text="Stopped")
        
        logger.info("Counting stopped")
    
    def process_video(self):
        """Video processing loop (runs in separate thread)"""
        while self.is_running:
            ret, frame = self.camera.read()
            
            if not ret:
                logger.warning("Failed to read frame, attempting reconnect...")
                if not self.camera.reconnect():
                    self.root.after(0, self.stop_counting)
                    break
                continue
            
            try:
                # Run detection with tracking
                use_tracking = config.get('counting', 'tracking_enabled')
                detections = self.detector.detect(frame, track=use_tracking)
                
                # Update counter
                stats = self.counter.update(detections)
                
                # Log events to database
                if self.database and self.counter.events:
                    for event in self.counter.get_recent_events(limit=1):
                        self.database.log_event(
                            event['direction'],
                            event['track_id'],
                            count_total=event['count_total']
                        )
                
                # Draw annotations
                if config.get('display', 'show_boxes'):
                    frame = self.detector.draw_detections(
                        frame, detections,
                        show_ids=config.get('display', 'show_ids'),
                        box_color=tuple(config.get('display', 'box_color'))
                    )
                
                if config.get('display', 'show_line'):
                    frame = self.counter.draw_line(
                        frame,
                        color=tuple(config.get('display', 'line_color'))
                    )
                
                # Update display
                self.root.after(0, self.update_video_display, frame)
                self.root.after(0, self.update_stats_display, stats)
                
                # Calculate FPS
                self.frame_count += 1
                if (datetime.now() - self.fps_start_time).total_seconds() >= 1.0:
                    self.fps = self.frame_count
                    self.frame_count = 0
                    self.fps_start_time = datetime.now()
                    self.root.after(0, self.update_fps_display)
                
            except Exception as e:
                logger.error(f"Error processing frame: {e}")
    
    def update_video_display(self, frame):
        """Update video canvas with new frame"""
        # Resize frame to fit canvas
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            frame_resized = cv2.resize(frame, (canvas_width, canvas_height))
        else:
            frame_resized = frame
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        image = Image.fromarray(frame_rgb)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image=image)
        
        # Update canvas
        self.video_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.video_canvas.image = photo  # Keep reference
    
    def update_stats_display(self, stats):
        """Update statistics labels"""
        self.in_label.config(text=str(stats['in']))
        self.out_label.config(text=str(stats['out']))
        self.current_label.config(text=str(stats['current']))
        self.total_label.config(text=str(stats['total']))
        
        # Update uptime
        if self.start_time:
            uptime = datetime.now() - self.start_time
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            seconds = uptime.seconds % 60
            self.uptime_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def update_fps_display(self):
        """Update FPS label"""
        self.fps_label.config(text=f"FPS: {self.fps}")
    
    def update_clock(self):
        """Update clock in status bar"""
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)
    
    def reset_counter(self):
        """Reset all counters"""
        if self.counter:
            result = messagebox.askyesno("Reset Counter", "Are you sure you want to reset all counters?")
            if result:
                self.counter.reset()
                logger.info("Counter reset by user")
    
    def export_report(self):
        """Export data to CSV"""
        if not self.database:
            messagebox.showinfo("Export", "Database not enabled")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            success = self.database.export_to_csv(filename)
            if success:
                messagebox.showinfo("Export", f"Report exported successfully to:\n{filename}")
            else:
                messagebox.showerror("Export Error", "Failed to export report")
    
    def open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog coming soon!\n\nFor now, edit config/settings.yaml manually.")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            result = messagebox.askyesno("Exit", "Counting is still running. Stop and exit?")
            if not result:
                return
            self.stop_counting()
        
        self.root.destroy()


def launch_gui():
    """Launch the GUI application"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

