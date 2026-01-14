"""
Smart Local Analytics Engine
All processing done locally using statistical methods (no cloud, no external AI)
"""

import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from src.utils.logger import logger


class SmartAnalytics:
    """
    Local analytics engine for pattern recognition and predictions
    Uses only statistical methods - no ML models required
    """
    
    def __init__(self, database_path='data/counter_data.db'):
        """
        Initialize analytics engine
        
        Parameters
        ----------
        database_path : str
            Path to database with historical data
        """
        self.db_path = Path(database_path)
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            logger.error(f"Analytics database connection failed: {e}")
    
    def analyze_peak_hours(self, date=None, days_back=7):
        """
        Identify peak traffic hours
        
        Parameters
        ----------
        date : datetime, optional
            Date to analyze (default: today)
        days_back : int
            Number of days to analyze
        
        Returns
        -------
        list
            Peak hours sorted by traffic
        """
        if not date:
            date = datetime.now().date()
        
        start_date = date - timedelta(days=days_back)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT hour, SUM(total_in + total_out) as total_traffic
                FROM hourly_stats
                WHERE date BETWEEN ? AND ?
                GROUP BY hour
                ORDER BY total_traffic DESC
            ''', (start_date, date))
            
            results = cursor.fetchall()
            peak_hours = [
                {'hour': row['hour'], 'traffic': row['total_traffic']}
                for row in results
            ]
            
            return peak_hours[:3]  # Top 3 peak hours
            
        except Exception as e:
            logger.error(f"Error analyzing peak hours: {e}")
            return []
    
    def predict_next_hour_traffic(self):
        """
        Predict traffic for next hour using historical average
        
        Returns
        -------
        dict
            Prediction with expected range and confidence
        """
        now = datetime.now()
        current_hour = now.hour
        current_day = now.weekday()  # 0=Monday, 6=Sunday
        
        # Get same hour, same day of week for last 4 weeks
        try:
            cursor = self.conn.cursor()
            four_weeks_ago = now.date() - timedelta(days=28)
            
            # Query for same hour and day of week
            cursor.execute('''
                SELECT total_in + total_out as total_traffic
                FROM hourly_stats
                WHERE hour = ?
                AND date >= ?
                AND strftime('%w', date) = ?
                ORDER BY date DESC
                LIMIT 4
            ''', (current_hour, four_weeks_ago, str(current_day)))
            
            results = cursor.fetchall()
            
            if len(results) < 2:
                return {
                    'prediction': None,
                    'confidence': 'Low',
                    'message': 'Not enough historical data'
                }
            
            # Calculate average and standard deviation
            traffic_values = [row['total_traffic'] for row in results]
            avg_traffic = sum(traffic_values) / len(traffic_values)
            
            # Simple standard deviation
            variance = sum((x - avg_traffic) ** 2 for x in traffic_values) / len(traffic_values)
            std_dev = variance ** 0.5
            
            # Confidence based on consistency
            if std_dev < avg_traffic * 0.2:  # Less than 20% variation
                confidence = 'High'
            elif std_dev < avg_traffic * 0.5:  # Less than 50% variation
                confidence = 'Medium'
            else:
                confidence = 'Low'
            
            return {
                'prediction': int(avg_traffic),
                'range_min': int(max(0, avg_traffic - std_dev)),
                'range_max': int(avg_traffic + std_dev),
                'confidence': confidence,
                'data_points': len(traffic_values)
            }
            
        except Exception as e:
            logger.error(f"Error predicting traffic: {e}")
            return {'prediction': None, 'confidence': 'Low', 'message': 'Error'}
    
    def detect_anomaly(self, current_count):
        """
        Detect if current traffic is anomalous
        
        Parameters
        ----------
        current_count : int
            Current traffic count
        
        Returns
        -------
        dict
            Anomaly detection result
        """
        now = datetime.now()
        current_hour = now.hour
        
        # Get historical average for this hour
        try:
            cursor = self.conn.cursor()
            two_weeks_ago = now.date() - timedelta(days=14)
            
            cursor.execute('''
                SELECT total_in + total_out as traffic
                FROM hourly_stats
                WHERE hour = ? AND date >= ?
            ''', (current_hour, two_weeks_ago))
            
            results = cursor.fetchall()
            
            if len(results) < 3:
                return {'is_anomaly': False, 'message': 'Insufficient data'}
            
            # Calculate mean and std deviation
            values = [row['traffic'] for row in results]
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            
            # Anomaly if current > mean + 2*std_dev
            threshold = mean + (2 * std_dev)
            
            is_anomaly = current_count > threshold
            
            if is_anomaly:
                percent_above = ((current_count - mean) / mean) * 100
                return {
                    'is_anomaly': True,
                    'message': f'Traffic {percent_above:.0f}% above normal',
                    'current': current_count,
                    'expected': int(mean),
                    'threshold': int(threshold)
                }
            else:
                return {'is_anomaly': False, 'current': current_count, 'expected': int(mean)}
                
        except Exception as e:
            logger.error(f"Error detecting anomaly: {e}")
            return {'is_anomaly': False, 'message': 'Error'}
    
    def compare_periods(self, days1=1, days2=1, offset=1):
        """
        Compare two time periods
        
        Parameters
        ----------
        days1 : int
            Number of days in first period
        days2 : int
            Number of days in second period
        offset : int
            Days back to start comparison
        
        Returns
        -------
        dict
            Comparison results
        """
        try:
            today = datetime.now().date()
            
            # Period 1: recent
            period1_end = today - timedelta(days=offset-1)
            period1_start = period1_end - timedelta(days=days1-1)
            
            # Period 2: comparison (e.g., last week)
            period2_end = period1_start - timedelta(days=1)
            period2_start = period2_end - timedelta(days=days2-1)
            
            cursor = self.conn.cursor()
            
            # Get totals for period 1
            cursor.execute('''
                SELECT SUM(total_in) as total_in, SUM(total_out) as total_out
                FROM hourly_stats
                WHERE date BETWEEN ? AND ?
            ''', (period1_start, period1_end))
            
            p1 = cursor.fetchone()
            period1_in = p1['total_in'] or 0
            period1_out = p1['total_out'] or 0
            period1_total = period1_in + period1_out
            
            # Get totals for period 2
            cursor.execute('''
                SELECT SUM(total_in) as total_in, SUM(total_out) as total_out
                FROM hourly_stats
                WHERE date BETWEEN ? AND ?
            ''', (period2_start, period2_end))
            
            p2 = cursor.fetchone()
            period2_in = p2['total_in'] or 0
            period2_out = p2['total_out'] or 0
            period2_total = period2_in + period2_out
            
            # Calculate changes
            if period2_total > 0:
                change_percent = ((period1_total - period2_total) / period2_total) * 100
            else:
                change_percent = 0
            
            return {
                'period1': {
                    'in': period1_in,
                    'out': period1_out,
                    'total': period1_total,
                    'start': period1_start,
                    'end': period1_end
                },
                'period2': {
                    'in': period2_in,
                    'out': period2_out,
                    'total': period2_total,
                    'start': period2_start,
                    'end': period2_end
                },
                'change_percent': change_percent,
                'trend': 'up' if change_percent > 0 else 'down' if change_percent < 0 else 'stable'
            }
            
        except Exception as e:
            logger.error(f"Error comparing periods: {e}")
            return None
    
    def get_weekly_pattern(self):
        """
        Analyze weekly traffic patterns
        
        Returns
        -------
        dict
            Weekly pattern analysis
        """
        try:
            cursor = self.conn.cursor()
            four_weeks_ago = datetime.now().date() - timedelta(days=28)
            
            cursor.execute('''
                SELECT strftime('%w', date) as day_of_week,
                       SUM(total_in + total_out) as total_traffic
                FROM hourly_stats
                WHERE date >= ?
                GROUP BY day_of_week
                ORDER BY total_traffic DESC
            ''', (four_weeks_ago,))
            
            results = cursor.fetchall()
            
            day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 
                        'Thursday', 'Friday', 'Saturday']
            
            pattern = {}
            for row in results:
                day_num = int(row['day_of_week'])
                pattern[day_names[day_num]] = row['total_traffic']
            
            if pattern:
                busiest_day = max(pattern, key=pattern.get)
                slowest_day = min(pattern, key=pattern.get)
                
                return {
                    'busiest_day': busiest_day,
                    'slowest_day': slowest_day,
                    'by_day': pattern
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting weekly pattern: {e}")
            return None
    
    def get_today_summary(self):
        """
        Get summary of today's activity
        
        Returns
        -------
        dict
            Today's statistics
        """
        try:
            cursor = self.conn.cursor()
            today = datetime.now().date()
            
            cursor.execute('''
                SELECT SUM(total_in) as total_in, SUM(total_out) as total_out
                FROM hourly_stats
                WHERE date = ?
            ''', (today,))
            
            result = cursor.fetchone()
            
            return {
                'in': result['total_in'] or 0,
                'out': result['total_out'] or 0,
                'total': (result['total_in'] or 0) + (result['total_out'] or 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting today summary: {e}")
            return {'in': 0, 'out': 0, 'total': 0}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup"""
        self.close()

