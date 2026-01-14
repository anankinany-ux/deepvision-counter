"""
Camera management with auto-reconnect and error handling
"""

import cv2
import time
from src.utils.logger import logger


class Camera:
    """
    Robust camera handler with auto-reconnect capability
    """
    
    def __init__(self, source=0, max_reconnect_attempts=10):
        """
        Initialize camera
        
        Parameters
        ----------
        source : int or str
            Camera index (0, 1, 2) or video file path or RTSP URL
        max_reconnect_attempts : int
            Maximum number of reconnection attempts
        """
        self.source = source
        self.cap = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = max_reconnect_attempts
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 0
    
    def connect(self):
        """
        Connect to camera with retry logic
        
        Returns
        -------
        bool
            True if connection successful, False otherwise
        """
        logger.info(f"Attempting to connect to camera: {self.source}")
        
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                self.cap = cv2.VideoCapture(self.source)
                
                if self.cap.isOpened():
                    # Get camera properties
                    self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 30
                    
                    self.is_connected = True
                    self.reconnect_attempts = 0
                    logger.info(f"Camera connected successfully: {self.frame_width}x{self.frame_height} @ {self.fps}fps")
                    return True
                else:
                    raise Exception("Camera failed to open")
                    
            except Exception as e:
                self.reconnect_attempts += 1
                logger.warning(f"Connection attempt {self.reconnect_attempts} failed: {e}")
                
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    logger.info(f"Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    logger.error(f"Camera connection failed after {self.max_reconnect_attempts} attempts")
                    self.is_connected = False
                    return False
        
        return False
    
    def read(self):
        """
        Read a frame from camera
        
        Returns
        -------
        tuple
            (success, frame) - success is bool, frame is numpy array or None
        """
        if not self.is_connected or self.cap is None:
            return False, None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret:
                logger.warning("Failed to read frame from camera")
                self.is_connected = False
                return False, None
            
            return True, frame
            
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            self.is_connected = False
            return False, None
    
    def reconnect(self):
        """
        Attempt to reconnect to camera
        
        Returns
        -------
        bool
            True if reconnection successful
        """
        logger.info("Attempting to reconnect camera...")
        self.release()
        time.sleep(1)
        return self.connect()
    
    def set_resolution(self, width, height):
        """
        Set camera resolution
        
        Parameters
        ----------
        width : int
            Frame width
        height : int
            Frame height
        """
        if self.cap and self.is_connected:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            logger.info(f"Camera resolution set to {width}x{height}")
    
    def set_fps(self, fps):
        """
        Set camera FPS (may not work on all cameras)
        
        Parameters
        ----------
        fps : int
            Frames per second
        """
        if self.cap and self.is_connected:
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            logger.info(f"Camera FPS set to {fps}")
    
    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_connected = False
            logger.info("Camera released")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.release()

