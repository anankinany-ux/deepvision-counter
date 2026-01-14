"""
Customer Counter Pro - Advanced Features Module
Multi-Zone, Heat Map, Weather, Conversion Tracking, Staff Detection, Video Playback
"""

import cv2
import numpy as np
from datetime import datetime, timedelta
import json
import os
import threading
import requests
from collections import deque
import sqlite3

# ============================================================================
# MULTI-ZONE TRACKING
# ============================================================================

class ZoneManager:
    """Manage multiple counting zones/lines"""
    
    def __init__(self):
        self.zones = {}
        self.active_zone = None
        self.load_zones()
    
    def add_zone(self, name, point1, point2, color=(255, 165, 0)):
        """Add a new counting zone"""
        self.zones[name] = {
            'name': name,
            'point1': list(point1),
            'point2': list(point2),
            'color': color,
            'count_in': 0,
            'count_out': 0,
            'enabled': True,
            'direction_reversed': False
        }
        self.save_zones()
        return name
    
    def remove_zone(self, name):
        """Remove a zone"""
        if name in self.zones:
            del self.zones[name]
            if self.active_zone == name:
                self.active_zone = list(self.zones.keys())[0] if self.zones else None
            self.save_zones()
    
    def get_zone(self, name):
        """Get zone by name"""
        return self.zones.get(name)
    
    def get_all_zones(self):
        """Get all zones"""
        return self.zones
    
    def check_crossing(self, zone_name, track_id, center, prev_center):
        """Check if object crossed the line in this zone"""
        if zone_name not in self.zones:
            return None
        
        zone = self.zones[zone_name]
        if not zone['enabled']:
            return None
        
        # Line crossing detection
        p1 = zone['point1']
        p2 = zone['point2']
        
        # Calculate which side of line the points are on
        def side_of_line(point, line_p1, line_p2):
            return ((line_p2[0] - line_p1[0]) * (point[1] - line_p1[1]) - 
                   (line_p2[1] - line_p1[1]) * (point[0] - line_p1[0]))
        
        if prev_center is None:
            return None
        
        prev_side = side_of_line(prev_center, p1, p2)
        curr_side = side_of_line(center, p1, p2)
        
        # Crossed the line
        if prev_side * curr_side < 0:
            direction = 1 if curr_side > 0 else -1
            if zone['direction_reversed']:
                direction *= -1
            
            # Update zone counts
            if direction > 0:
                zone['count_in'] += 1
                return 'IN'
            else:
                zone['count_out'] += 1
                return 'OUT'
        
        return None
    
    def reset_zone_counts(self, zone_name=None):
        """Reset counts for a zone or all zones"""
        if zone_name:
            if zone_name in self.zones:
                self.zones[zone_name]['count_in'] = 0
                self.zones[zone_name]['count_out'] = 0
        else:
            for zone in self.zones.values():
                zone['count_in'] = 0
                zone['count_out'] = 0
    
    def save_zones(self):
        """Save zones to file"""
        try:
            with open('zones_config.json', 'w') as f:
                json.dump(self.zones, f, indent=2)
        except:
            pass
    
    def load_zones(self):
        """Load zones from file"""
        try:
            if os.path.exists('zones_config.json'):
                with open('zones_config.json', 'r') as f:
                    self.zones = json.load(f)
                    if self.zones:
                        self.active_zone = list(self.zones.keys())[0]
        except:
            # Create default zone
            self.add_zone("Main Entrance", [640, 300], [640, 420], (255, 165, 0))
            self.active_zone = "Main Entrance"


# ============================================================================
# HEAT MAP VISUALIZATION
# ============================================================================

class HeatMapTracker:
    """Track and visualize customer movement heat maps"""
    
    def __init__(self, frame_size=(1280, 720), grid_size=20):
        self.frame_size = frame_size
        self.grid_size = grid_size
        self.grid_rows = frame_size[1] // grid_size
        self.grid_cols = frame_size[0] // grid_size
        self.heat_map = np.zeros((self.grid_rows, self.grid_cols), dtype=np.float32)
        self.enabled = False
        self.decay_rate = 0.95  # Heat decay over time
        self.max_heat = 1.0
    
    def add_detection(self, center_x, center_y):
        """Add a detection point to heat map"""
        if not self.enabled:
            return
        
        grid_x = int(center_x / self.grid_size)
        grid_y = int(center_y / self.grid_size)
        
        if 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows:
            self.heat_map[grid_y, grid_x] += 0.1
            self.max_heat = max(self.max_heat, self.heat_map[grid_y, grid_x])
    
    def decay_heat(self):
        """Gradually decay heat over time"""
        if self.enabled:
            self.heat_map *= self.decay_rate
    
    def get_heat_overlay(self, frame):
        """Generate heat map overlay on frame"""
        if not self.enabled:
            return frame
        
        # Create colored heat map
        heat_normalized = (self.heat_map / max(self.max_heat, 1.0) * 255).astype(np.uint8)
        heat_colored = cv2.applyColorMap(heat_normalized, cv2.COLORMAP_JET)
        heat_resized = cv2.resize(heat_colored, (frame.shape[1], frame.shape[0]))
        
        # Blend with original frame
        overlay = cv2.addWeighted(frame, 0.7, heat_resized, 0.3, 0)
        return overlay
    
    def reset(self):
        """Reset heat map"""
        self.heat_map = np.zeros((self.grid_rows, self.grid_cols), dtype=np.float32)
        self.max_heat = 1.0
    
    def toggle(self):
        """Toggle heat map on/off"""
        self.enabled = not self.enabled
        return self.enabled


# ============================================================================
# CONVERSION RATE TRACKING
# ============================================================================

class ConversionTracker:
    """Track sales conversions and calculate conversion rates"""
    
    def __init__(self):
        self.db = sqlite3.connect('customer_analytics.db', check_same_thread=False)
        self.create_tables()
        self.today_sales = 0
        self.load_today_sales()
    
    def create_tables(self):
        """Create sales tracking table"""
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                date DATE,
                hour INTEGER,
                amount REAL DEFAULT 0
            )
        ''')
        self.db.commit()
    
    def register_sale(self, amount=0):
        """Register a sale/conversion"""
        now = datetime.now()
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO sales (timestamp, date, hour, amount)
            VALUES (?, ?, ?, ?)
        ''', (now.isoformat(), now.date().isoformat(), now.hour, amount))
        self.db.commit()
        self.today_sales += 1
        return self.today_sales
    
    def get_conversion_rate(self, total_customers):
        """Calculate conversion rate"""
        if total_customers == 0:
            return 0.0
        return (self.today_sales / total_customers) * 100
    
    def get_today_stats(self):
        """Get today's sales statistics"""
        cursor = self.db.cursor()
        today = datetime.now().date().isoformat()
        cursor.execute('''
            SELECT COUNT(*), COALESCE(SUM(amount), 0)
            FROM sales
            WHERE date = ?
        ''', (today,))
        count, total = cursor.fetchone()
        return {'count': count or 0, 'total': total or 0}
    
    def load_today_sales(self):
        """Load today's sales count"""
        stats = self.get_today_stats()
        self.today_sales = stats['count']
    
    def reset_today(self):
        """Reset today's counter (for testing)"""
        self.today_sales = 0


# ============================================================================
# STAFF DETECTION / FILTERING
# ============================================================================

class StaffFilter:
    """Filter staff from customer counts"""
    
    def __init__(self):
        self.staff_zones = []
        self.enabled = False
        self.staff_ids = set()  # Track IDs identified as staff
        self.load_config()
    
    def add_staff_zone(self, x1, y1, x2, y2):
        """Add a zone where staff typically are (e.g., behind counter)"""
        self.staff_zones.append({
            'x1': x1, 'y1': y1,
            'x2': x2, 'y2': y2
        })
        self.save_config()
    
    def is_in_staff_zone(self, center_x, center_y):
        """Check if person is in a staff zone"""
        if not self.enabled:
            return False
        
        for zone in self.staff_zones:
            if (zone['x1'] <= center_x <= zone['x2'] and 
                zone['y1'] <= center_y <= zone['y2']):
                return True
        return False
    
    def mark_as_staff(self, track_id):
        """Mark a track ID as staff"""
        self.staff_ids.add(track_id)
    
    def is_staff(self, track_id):
        """Check if track ID is staff"""
        return track_id in self.staff_ids
    
    def toggle(self):
        """Toggle staff filtering"""
        self.enabled = not self.enabled
        return self.enabled
    
    def save_config(self):
        """Save staff zones"""
        try:
            with open('staff_config.json', 'w') as f:
                json.dump({'zones': self.staff_zones, 'enabled': self.enabled}, f)
        except:
            pass
    
    def load_config(self):
        """Load staff zones"""
        try:
            if os.path.exists('staff_config.json'):
                with open('staff_config.json', 'r') as f:
                    data = json.load(f)
                    self.staff_zones = data.get('zones', [])
                    self.enabled = data.get('enabled', False)
        except:
            pass


# ============================================================================
# WEATHER INTEGRATION
# ============================================================================

class WeatherTracker:
    """Track weather and correlate with traffic"""
    
    def __init__(self, api_key=None, location='auto'):
        self.api_key = api_key or "demo"  # Free tier: api.openweathermap.org
        self.location = location
        self.current_weather = None
        self.last_update = None
        self.update_interval = 1800  # 30 minutes
        self.enabled = False
    
    def fetch_weather(self):
        """Fetch current weather (requires internet)"""
        if not self.enabled or not self.api_key or self.api_key == "demo":
            return None
        
        try:
            # Using free weather API - wttr.in (no key needed!)
            response = requests.get(f'https://wttr.in/?format=j1', timeout=5)
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    'temp_c': float(data['current_condition'][0]['temp_C']),
                    'temp_f': float(data['current_condition'][0]['temp_F']),
                    'condition': data['current_condition'][0]['weatherDesc'][0]['value'],
                    'humidity': int(data['current_condition'][0]['humidity']),
                    'updated': datetime.now()
                }
                self.current_weather = weather_data
                self.last_update = datetime.now()
                return weather_data
        except:
            pass
        
        return None
    
    def get_weather_string(self):
        """Get formatted weather string"""
        if not self.enabled or not self.current_weather:
            return "Weather: Off"
        
        w = self.current_weather
        return f"{w['condition']} {w['temp_c']}°C / {w['temp_f']}°F"
    
    def update_if_needed(self):
        """Update weather if interval passed"""
        if not self.enabled:
            return
        
        if not self.last_update or (datetime.now() - self.last_update).seconds > self.update_interval:
            threading.Thread(target=self.fetch_weather, daemon=True).start()
    
    def toggle(self):
        """Toggle weather tracking"""
        self.enabled = not self.enabled
        if self.enabled and not self.current_weather:
            self.fetch_weather()
        return self.enabled


# ============================================================================
# VIDEO RECORDING & PLAYBACK
# ============================================================================

class VideoRecorder:
    """Record and playback video with annotations"""
    
    def __init__(self):
        self.recording = False
        self.video_writer = None
        self.recordings_dir = "recordings"
        self.current_file = None
        self.recordings_list = []
        self.load_recordings_list()
        
        # Create recordings directory
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
    
    def start_recording(self, frame_size, fps=30):
        """Start recording video"""
        if self.recording:
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_file = os.path.join(self.recordings_dir, f"recording_{timestamp}.mp4")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(self.current_file, fourcc, fps, frame_size)
        
        if self.video_writer.isOpened():
            self.recording = True
            return True
        return False
    
    def write_frame(self, frame):
        """Write frame to video"""
        if self.recording and self.video_writer:
            self.video_writer.write(frame)
    
    def stop_recording(self):
        """Stop recording video"""
        if self.recording and self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            self.recording = False
            self.recordings_list.append(self.current_file)
            self.save_recordings_list()
            return self.current_file
        return None
    
    def load_recordings_list(self):
        """Load list of recordings"""
        if os.path.exists(self.recordings_dir):
            self.recordings_list = [
                os.path.join(self.recordings_dir, f) 
                for f in os.listdir(self.recordings_dir) 
                if f.endswith('.mp4')
            ]
            self.recordings_list.sort(reverse=True)  # Newest first
    
    def save_recordings_list(self):
        """Save recordings metadata"""
        try:
            with open(os.path.join(self.recordings_dir, 'metadata.json'), 'w') as f:
                json.dump({'recordings': self.recordings_list}, f)
        except:
            pass
    
    def get_recordings(self):
        """Get list of available recordings"""
        self.load_recordings_list()
        return self.recordings_list


# ============================================================================
# EMAIL REPORTS
# ============================================================================

class EmailReporter:
    """Automated email reporting system"""
    
    def __init__(self):
        self.enabled = False
        self.smtp_config = {
            'server': '',
            'port': 587,
            'username': '',
            'password': '',
            'from_email': '',
            'to_emails': []
        }
        self.schedule = {
            'daily': False,
            'weekly': False,
            'time': '08:00'
        }
        self.load_config()
    
    def configure_smtp(self, server, port, username, password, from_email, to_emails):
        """Configure SMTP settings"""
        self.smtp_config = {
            'server': server,
            'port': port,
            'username': username,
            'password': password,
            'from_email': from_email,
            'to_emails': to_emails if isinstance(to_emails, list) else [to_emails]
        }
        self.save_config()
    
    def send_report(self, customer_tracker):
        """Send email report with statistics"""
        if not self.enabled or not self.smtp_config['server']:
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Get analytics data
            analytics = customer_tracker.get_analytics()
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = ', '.join(self.smtp_config['to_emails'])
            msg['Subject'] = f"Customer Counter Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Email body
            body = f"""
            Customer Counter Pro - Daily Report
            ====================================
            
            Date: {datetime.now().strftime('%Y-%m-%d')}
            
            Today's Statistics:
            - Total Customers: {analytics['today_total']}
            - Average Visit Time: {analytics['avg_duration'] / 60:.1f} minutes
            - Longest Visit: {analytics['max_duration'] / 60:.1f} minutes
            - Currently Inside: {analytics['current_occupancy']}
            
            Have a great day!
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def save_config(self):
        """Save email configuration"""
        try:
            with open('email_config.json', 'w') as f:
                json.dump({
                    'smtp': self.smtp_config,
                    'schedule': self.schedule,
                    'enabled': self.enabled
                }, f, indent=2)
        except:
            pass
    
    def load_config(self):
        """Load email configuration"""
        try:
            if os.path.exists('email_config.json'):
                with open('email_config.json', 'r') as f:
                    data = json.load(f)
                    self.smtp_config = data.get('smtp', self.smtp_config)
                    self.schedule = data.get('schedule', self.schedule)
                    self.enabled = data.get('enabled', False)
        except:
            pass

