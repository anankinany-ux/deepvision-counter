"""
Visual chart generation for reports
All processing done locally using matplotlib
"""

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
from src.utils.logger import logger


class ChartGenerator:
    """Generate visual charts and reports from counting data"""
    
    def __init__(self, database_path='data/counter_data.db'):
        """
        Initialize chart generator
        
        Parameters
        ----------
        database_path : str
            Path to database
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
            logger.error(f"Charts database connection failed: {e}")
    
    def generate_hourly_chart(self, date=None, output_path='hourly_traffic.png'):
        """
        Generate hourly traffic bar chart
        
        Parameters
        ----------
        date : datetime, optional
            Date to chart (default: today)
        output_path : str
            Where to save the chart
        
        Returns
        -------
        str
            Path to generated chart
        """
        if not date:
            date = datetime.now().date()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT hour, total_in, total_out
                FROM hourly_stats
                WHERE date = ?
                ORDER BY hour
            ''', (date,))
            
            results = cursor.fetchall()
            
            if not results:
                logger.warning(f"No data for {date}")
                return None
            
            # Prepare data
            hours = [row['hour'] for row in results]
            ins = [row['total_in'] for row in results]
            outs = [row['total_out'] for row in results]
            
            # Create chart
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x = range(len(hours))
            width = 0.35
            
            # Bar charts
            ax.bar([i - width/2 for i in x], ins, width, label='IN', color='#4CAF50')
            ax.bar([i + width/2 for i in x], outs, width, label='OUT', color='#F44336')
            
            # Formatting
            ax.set_xlabel('Hour of Day', fontsize=12)
            ax.set_ylabel('People Count', fontsize=12)
            ax.set_title(f'Hourly Traffic - {date.strftime("%B %d, %Y")}', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels([f'{h}:00' for h in hours])
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Hourly chart saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating hourly chart: {e}")
            return None
    
    def generate_comparison_chart(self, days=7, output_path='comparison.png'):
        """
        Generate daily comparison chart
        
        Parameters
        ----------
        days : int
            Number of days to include
        output_path : str
            Where to save the chart
        
        Returns
        -------
        str
            Path to generated chart
        """
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT date, SUM(total_in) as total_in, SUM(total_out) as total_out
                FROM hourly_stats
                WHERE date BETWEEN ? AND ?
                GROUP BY date
                ORDER BY date
            ''', (start_date, end_date))
            
            results = cursor.fetchall()
            
            if not results:
                logger.warning(f"No data for period")
                return None
            
            # Prepare data
            dates = [datetime.strptime(str(row['date']), '%Y-%m-%d') for row in results]
            totals = [row['total_in'] + row['total_out'] for row in results]
            
            # Create chart
            fig, ax = plt.subplots(figsize=(12, 6))
            
            ax.plot(dates, totals, marker='o', linewidth=2, markersize=8, color='#2196F3')
            ax.fill_between(dates, totals, alpha=0.3, color='#2196F3')
            
            # Formatting
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Total Traffic', fontsize=12)
            ax.set_title(f'Daily Traffic - Last {days} Days', fontsize=14, fontweight='bold')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Comparison chart saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating comparison chart: {e}")
            return None
    
    def generate_heatmap(self, weeks=4, output_path='heatmap.png'):
        """
        Generate weekly heatmap showing busiest times
        
        Parameters
        ----------
        weeks : int
            Number of weeks to analyze
        output_path : str
            Where to save the chart
        
        Returns
        -------
        str
            Path to generated chart
        """
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=weeks*7)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT date, hour, total_in + total_out as traffic
                FROM hourly_stats
                WHERE date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            results = cursor.fetchall()
            
            if not results:
                logger.warning("No data for heatmap")
                return None
            
            # Create matrix: 24 hours x 7 days
            import numpy as np
            heatmap_data = np.zeros((24, 7))
            counts = np.zeros((24, 7))
            
            for row in results:
                date_obj = datetime.strptime(str(row['date']), '%Y-%m-%d')
                day_of_week = date_obj.weekday()  # 0=Monday
                hour = row['hour']
                traffic = row['traffic']
                
                heatmap_data[hour][day_of_week] += traffic
                counts[hour][day_of_week] += 1
            
            # Average traffic
            with np.errstate(divide='ignore', invalid='ignore'):
                heatmap_data = np.where(counts > 0, heatmap_data / counts, 0)
            
            # Create heatmap
            fig, ax = plt.subplots(figsize=(10, 12))
            
            im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
            
            # Labels
            day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            hour_labels = [f'{h:02d}:00' for h in range(24)]
            
            ax.set_xticks(range(7))
            ax.set_yticks(range(24))
            ax.set_xticklabels(day_labels)
            ax.set_yticklabels(hour_labels)
            
            # Title
            ax.set_title(f'Traffic Heatmap - Last {weeks} Weeks', fontsize=14, fontweight='bold')
            
            # Colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Average Traffic', rotation=270, labelpad=20)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Heatmap saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating heatmap: {e}")
            return None
    
    def generate_full_report(self, output_dir='data/reports'):
        """
        Generate complete visual report with multiple charts
        
        Parameters
        ----------
        output_dir : str
            Directory to save report files
        
        Returns
        -------
        list
            Paths to generated charts
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        charts = []
        
        # Generate all charts
        hourly = self.generate_hourly_chart(
            output_path=output_path / f'hourly_{timestamp}.png'
        )
        if hourly:
            charts.append(hourly)
        
        comparison = self.generate_comparison_chart(
            days=7,
            output_path=output_path / f'weekly_{timestamp}.png'
        )
        if comparison:
            charts.append(comparison)
        
        heatmap = self.generate_heatmap(
            weeks=4,
            output_path=output_path / f'heatmap_{timestamp}.png'
        )
        if heatmap:
            charts.append(heatmap)
        
        logger.info(f"Generated {len(charts)} charts in {output_dir}")
        return charts
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup"""
        self.close()

