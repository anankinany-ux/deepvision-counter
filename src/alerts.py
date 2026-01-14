"""
Smart Alerts System - Local pattern-based notifications
"""

from datetime import datetime
from src.utils.logger import logger
from src.config import config


class AlertSystem:
    """
    Manage smart alerts based on traffic patterns and thresholds
    All processing done locally
    """
    
    def __init__(self):
        """Initialize alert system"""
        self.alerts_history = []
        self.last_alert_time = {}  # Prevent spam
        self.alert_cooldown = 300  # 5 minutes between same alert type
    
    def check_occupancy_limit(self, current_count):
        """
        Check if occupancy limit exceeded
        
        Parameters
        ----------
        current_count : int
            Current people inside
        
        Returns
        -------
        dict or None
            Alert details if triggered
        """
        if not config.get('alerts', 'alert_enabled'):
            return None
        
        max_occupancy = config.get('alerts', 'max_occupancy')
        
        if current_count >= max_occupancy:
            alert = {
                'type': 'occupancy',
                'severity': 'high',
                'message': f'⚠️ Occupancy limit reached! ({current_count}/{max_occupancy})',
                'timestamp': datetime.now(),
                'current': current_count,
                'limit': max_occupancy
            }
            
            if self._should_trigger_alert('occupancy'):
                self.alerts_history.append(alert)
                logger.warning(alert['message'])
                return alert
        
        return None
    
    def check_anomaly(self, analytics_result):
        """
        Check for traffic anomalies
        
        Parameters
        ----------
        analytics_result : dict
            Result from analytics.detect_anomaly()
        
        Returns
        -------
        dict or None
            Alert details if triggered
        """
        if not config.get('alerts', 'anomaly_alerts', default=True):
            return None
        
        if analytics_result and analytics_result.get('is_anomaly'):
            alert = {
                'type': 'anomaly',
                'severity': 'medium',
                'message': f'📈 {analytics_result.get("message")}',
                'timestamp': datetime.now(),
                'details': analytics_result
            }
            
            if self._should_trigger_alert('anomaly'):
                self.alerts_history.append(alert)
                logger.info(alert['message'])
                return alert
        
        return None
    
    def check_no_activity(self, minutes_since_last_count):
        """
        Check for unusual inactivity
        
        Parameters
        ----------
        minutes_since_last_count : int
            Minutes since last person detected
        
        Returns
        -------
        dict or None
            Alert details if triggered
        """
        # Only alert during business hours
        current_hour = datetime.now().hour
        if not (8 <= current_hour <= 20):  # 8am to 8pm
            return None
        
        if minutes_since_last_count > 120:  # 2 hours of no activity
            alert = {
                'type': 'inactivity',
                'severity': 'low',
                'message': f'⚠️ No activity for {minutes_since_last_count} minutes - check camera',
                'timestamp': datetime.now(),
                'minutes': minutes_since_last_count
            }
            
            if self._should_trigger_alert('inactivity'):
                self.alerts_history.append(alert)
                logger.warning(alert['message'])
                return alert
        
        return None
    
    def check_pattern_change(self, comparison_result):
        """
        Check for significant pattern changes
        
        Parameters
        ----------
        comparison_result : dict
            Result from analytics.compare_periods()
        
        Returns
        -------
        dict or None
            Alert details if triggered
        """
        if not config.get('alerts', 'pattern_alerts', default=True):
            return None
        
        if comparison_result:
            change = abs(comparison_result.get('change_percent', 0))
            
            if change > 50:  # More than 50% change
                trend = comparison_result.get('trend')
                icon = '📈' if trend == 'up' else '📉'
                
                alert = {
                    'type': 'pattern_change',
                    'severity': 'medium',
                    'message': f'{icon} Traffic {trend} {change:.0f}% compared to last period',
                    'timestamp': datetime.now(),
                    'details': comparison_result
                }
                
                if self._should_trigger_alert('pattern_change'):
                    self.alerts_history.append(alert)
                    logger.info(alert['message'])
                    return alert
        
        return None
    
    def _should_trigger_alert(self, alert_type):
        """
        Check if enough time passed since last alert of this type
        
        Parameters
        ----------
        alert_type : str
            Type of alert
        
        Returns
        -------
        bool
            True if alert should be triggered
        """
        now = datetime.now()
        
        if alert_type in self.last_alert_time:
            time_since = (now - self.last_alert_time[alert_type]).total_seconds()
            if time_since < self.alert_cooldown:
                return False
        
        self.last_alert_time[alert_type] = now
        return True
    
    def get_recent_alerts(self, limit=10):
        """
        Get recent alerts
        
        Parameters
        ----------
        limit : int
            Maximum number of alerts to return
        
        Returns
        -------
        list
            Recent alerts
        """
        return self.alerts_history[-limit:]
    
    def clear_alerts(self):
        """Clear alerts history"""
        self.alerts_history = []
        logger.info("Alerts history cleared")

