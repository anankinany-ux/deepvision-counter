"""
People counting logic with IN/OUT tracking using virtual line crossing
"""

import cv2
from datetime import datetime
from src.utils.logger import logger


class PeopleCounter:
    """
    Count people crossing a virtual line with direction detection
    """
    
    def __init__(self, line_position=0.5, direction='vertical', frame_height=720, frame_width=1280):
        """
        Initialize people counter
        
        Parameters
        ----------
        line_position : float
            Position of counting line (0.0 to 1.0)
            For vertical: 0.5 means middle of frame height
            For horizontal: 0.5 means middle of frame width
        direction : str
            'vertical' for horizontal line (counts vertical movement)
            'horizontal' for vertical line (counts horizontal movement)
        frame_height : int
            Frame height in pixels
        frame_width : int
            Frame width in pixels
        """
        self.line_position = line_position
        self.direction = direction
        self.frame_height = frame_height
        self.frame_width = frame_width
        
        # Calculate line coordinates
        self._update_line_coords()
        
        # Tracking data: {track_id: {'last_pos': y or x, 'counted': bool}}
        self.tracks = {}
        
        # Counters
        self.count_in = 0
        self.count_out = 0
        self.count_total = 0
        
        # History for events
        self.events = []
        
        logger.info(f"Counter initialized: {direction} line at {line_position}")
    
    def _update_line_coords(self):
        """Update line coordinates based on frame size"""
        if self.direction == 'vertical':
            # Horizontal line across frame (detects vertical movement)
            self.line_coord = int(self.frame_height * self.line_position)
            self.line_start = (0, self.line_coord)
            self.line_end = (self.frame_width, self.line_coord)
        else:
            # Vertical line down frame (detects horizontal movement)
            self.line_coord = int(self.frame_width * self.line_position)
            self.line_start = (self.line_coord, 0)
            self.line_end = (self.line_coord, self.frame_height)
    
    def update_frame_size(self, height, width):
        """
        Update frame dimensions and recalculate line position
        
        Parameters
        ----------
        height : int
            New frame height
        width : int
            New frame width
        """
        self.frame_height = height
        self.frame_width = width
        self._update_line_coords()
    
    def update(self, detections):
        """
        Update counter with new detections
        
        Parameters
        ----------
        detections : list
            List of detections from PersonDetector with 'track_id' and 'center'
        
        Returns
        -------
        dict
            Counter statistics
        """
        # Get current tracked IDs
        current_ids = set()
        
        for det in detections:
            if 'track_id' not in det:
                continue
            
            track_id = det['track_id']
            center_x, center_y = det['center']
            current_ids.add(track_id)
            
            # Get relevant coordinate based on direction
            current_pos = center_y if self.direction == 'vertical' else center_x
            
            # Check if this is a new track
            if track_id not in self.tracks:
                self.tracks[track_id] = {
                    'last_pos': current_pos,
                    'counted': False
                }
                continue
            
            # Get previous position
            last_pos = self.tracks[track_id]['last_pos']
            
            # Check if not yet counted and crossed the line
            if not self.tracks[track_id]['counted']:
                if self._crossed_line(last_pos, current_pos):
                    # Determine direction
                    if current_pos > last_pos:
                        # Moving down/right (IN)
                        self.count_in += 1
                        direction = 'IN'
                    else:
                        # Moving up/left (OUT)
                        self.count_out += 1
                        direction = 'OUT'
                    
                    self.count_total = self.count_in - self.count_out
                    self.tracks[track_id]['counted'] = True
                    
                    # Log event
                    event = {
                        'timestamp': datetime.now(),
                        'track_id': track_id,
                        'direction': direction,
                        'count_total': self.count_total
                    }
                    self.events.append(event)
                    
                    logger.info(f"Person {track_id} counted: {direction} | Total: {self.count_total}")
            
            # Update last position
            self.tracks[track_id]['last_pos'] = current_pos
        
        # Clean up old tracks that are no longer detected
        disappeared_ids = set(self.tracks.keys()) - current_ids
        for track_id in disappeared_ids:
            del self.tracks[track_id]
        
        return self.get_stats()
    
    def _crossed_line(self, last_pos, current_pos):
        """
        Check if object crossed the counting line
        
        Parameters
        ----------
        last_pos : int
            Previous position
        current_pos : int
            Current position
        
        Returns
        -------
        bool
            True if line was crossed
        """
        # Check if line is between last and current position
        return (last_pos < self.line_coord <= current_pos) or \
               (last_pos > self.line_coord >= current_pos)
    
    def draw_line(self, frame, color=(0, 0, 255), thickness=2):
        """
        Draw counting line on frame
        
        Parameters
        ----------
        frame : numpy.ndarray
            Input frame
        color : tuple
            BGR color for line
        thickness : int
            Line thickness
        
        Returns
        -------
        numpy.ndarray
            Frame with line drawn
        """
        annotated = frame.copy()
        cv2.line(annotated, self.line_start, self.line_end, color, thickness)
        
        # Draw text labels
        if self.direction == 'vertical':
            # Label above and below line
            cv2.putText(annotated, "OUT", (10, self.line_coord - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(annotated, "IN", (10, self.line_coord + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        else:
            # Label left and right of line
            cv2.putText(annotated, "OUT", (self.line_coord - 60, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(annotated, "IN", (self.line_coord + 10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return annotated
    
    def get_stats(self):
        """
        Get current counting statistics
        
        Returns
        -------
        dict
            Current counts
        """
        return {
            'in': self.count_in,
            'out': self.count_out,
            'current': self.count_total,
            'total': self.count_in + self.count_out
        }
    
    def reset(self):
        """Reset all counters"""
        self.count_in = 0
        self.count_out = 0
        self.count_total = 0
        self.tracks = {}
        self.events = []
        logger.info("Counter reset")
    
    def get_recent_events(self, limit=10):
        """
        Get recent counting events
        
        Parameters
        ----------
        limit : int
            Maximum number of events to return
        
        Returns
        -------
        list
            Recent events
        """
        return self.events[-limit:]

