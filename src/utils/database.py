"""
Database management for storing counting data and generating reports
"""

import sqlite3
import csv
from datetime import datetime, timedelta
from pathlib import Path
from src.utils.logger import logger


class CounterDatabase:
    """SQLite database for storing and retrieving counting data"""
    
    def __init__(self, db_path='data/counter_data.db'):
        """
        Initialize database connection
        
        Parameters
        ----------
        db_path : str
            Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        if not self.connect():
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Count events table (individual IN/OUT events)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS count_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    direction TEXT NOT NULL,
                    track_id INTEGER,
                    camera_id TEXT,
                    count_total INTEGER
                )
            ''')
            
            # Hourly statistics table (aggregated data)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hourly_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    hour INTEGER NOT NULL,
                    total_in INTEGER DEFAULT 0,
                    total_out INTEGER DEFAULT 0,
                    camera_id TEXT,
                    UNIQUE(date, hour, camera_id)
                )
            ''')
            
            # Sessions table (track when counting started/stopped)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    total_in INTEGER DEFAULT 0,
                    total_out INTEGER DEFAULT 0,
                    camera_id TEXT
                )
            ''')
            
            self.conn.commit()
            logger.info("Database tables created/verified")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def log_event(self, direction, track_id=None, camera_id='default', count_total=0):
        """
        Log a single counting event
        
        Parameters
        ----------
        direction : str
            'IN' or 'OUT'
        track_id : int, optional
            Person track ID
        camera_id : str
            Camera identifier
        count_total : int
            Current total count
        """
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO count_events (timestamp, direction, track_id, camera_id, count_total)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now(), direction, track_id, camera_id, count_total))
            self.conn.commit()
            
            # Update hourly stats
            self._update_hourly_stats(direction, camera_id)
            
        except Exception as e:
            logger.error(f"Error logging event: {e}")
    
    def _update_hourly_stats(self, direction, camera_id):
        """Update hourly statistics"""
        now = datetime.now()
        date = now.date()
        hour = now.hour
        
        try:
            cursor = self.conn.cursor()
            
            # Check if record exists
            cursor.execute('''
                SELECT id, total_in, total_out FROM hourly_stats
                WHERE date = ? AND hour = ? AND camera_id = ?
            ''', (date, hour, camera_id))
            
            row = cursor.fetchone()
            
            if row:
                # Update existing record
                if direction == 'IN':
                    cursor.execute('''
                        UPDATE hourly_stats SET total_in = total_in + 1
                        WHERE id = ?
                    ''', (row['id'],))
                else:
                    cursor.execute('''
                        UPDATE hourly_stats SET total_out = total_out + 1
                        WHERE id = ?
                    ''', (row['id'],))
            else:
                # Insert new record
                total_in = 1 if direction == 'IN' else 0
                total_out = 1 if direction == 'OUT' else 0
                cursor.execute('''
                    INSERT INTO hourly_stats (date, hour, total_in, total_out, camera_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (date, hour, total_in, total_out, camera_id))
            
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error updating hourly stats: {e}")
    
    def start_session(self, camera_id='default'):
        """
        Start a new counting session
        
        Returns
        -------
        int
            Session ID
        """
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (start_time, camera_id)
                VALUES (?, ?)
            ''', (datetime.now(), camera_id))
            self.conn.commit()
            session_id = cursor.lastrowid
            logger.info(f"Session {session_id} started")
            return session_id
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return None
    
    def end_session(self, session_id, total_in, total_out):
        """
        End a counting session
        
        Parameters
        ----------
        session_id : int
            Session ID
        total_in : int
            Total people in
        total_out : int
            Total people out
        """
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE sessions
                SET end_time = ?, total_in = ?, total_out = ?
                WHERE id = ?
            ''', (datetime.now(), total_in, total_out, session_id))
            self.conn.commit()
            logger.info(f"Session {session_id} ended")
        except Exception as e:
            logger.error(f"Error ending session: {e}")
    
    def get_today_stats(self, camera_id='default'):
        """
        Get today's statistics
        
        Returns
        -------
        dict
            Today's counts
        """
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            today = datetime.now().date()
            
            cursor.execute('''
                SELECT SUM(total_in) as total_in, SUM(total_out) as total_out
                FROM hourly_stats
                WHERE date = ? AND camera_id = ?
            ''', (today, camera_id))
            
            row = cursor.fetchone()
            if row:
                return {
                    'in': row['total_in'] or 0,
                    'out': row['total_out'] or 0
                }
            return {'in': 0, 'out': 0}
            
        except Exception as e:
            logger.error(f"Error getting today's stats: {e}")
            return {'in': 0, 'out': 0}
    
    def export_to_csv(self, output_path, start_date=None, end_date=None, camera_id='default'):
        """
        Export data to CSV file
        
        Parameters
        ----------
        output_path : str
            Output CSV file path
        start_date : datetime, optional
            Start date for export
        end_date : datetime, optional
            End date for export
        camera_id : str
            Camera identifier
        
        Returns
        -------
        bool
            True if export successful
        """
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            
            # Default to last 30 days if not specified
            if not end_date:
                end_date = datetime.now().date()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            cursor.execute('''
                SELECT date, hour, total_in, total_out
                FROM hourly_stats
                WHERE date BETWEEN ? AND ? AND camera_id = ?
                ORDER BY date, hour
            ''', (start_date, end_date, camera_id))
            
            rows = cursor.fetchall()
            
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Hour', 'Total IN', 'Total OUT', 'Net'])
                
                for row in rows:
                    net = row['total_in'] - row['total_out']
                    writer.writerow([
                        row['date'],
                        row['hour'],
                        row['total_in'],
                        row['total_out'],
                        net
                    ])
            
            logger.info(f"Data exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()

