"""
YOLO-based person detection with performance optimizations
"""

import cv2
import os
from ultralytics import YOLO
from src.utils.logger import logger
from src.config import config


class PersonDetector:
    """
    YOLO person detector with tracking support
    """
    
    def __init__(self, model_path='models/yolov8n.pt', confidence_threshold=0.5):
        """
        Initialize YOLO detector
        
        Parameters
        ----------
        model_path : str
            Path to YOLO model file
        confidence_threshold : float
            Minimum confidence score for detections (0.0 to 1.0)
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load YOLO model with offline mode"""
        try:
            logger.info(f"Loading YOLO model from {self.model_path}")
            
            # Ensure 100% offline operation
            if config.get('privacy', 'offline_only'):
                os.environ['YOLO_OFFLINE'] = '1'
                os.environ['ULTRALYTICS_OFFLINE'] = '1'
                logger.info("Offline mode enabled - no network calls")
            
            self.model = YOLO(self.model_path)
            
            # Disable verbose output and any telemetry
            if hasattr(self.model, 'overrides'):
                self.model.overrides['verbose'] = False
            
            logger.info("YOLO model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            return False
    
    def detect(self, frame, track=False):
        """
        Detect people in frame
        
        Parameters
        ----------
        frame : numpy.ndarray
            Input image frame
        track : bool
            If True, use tracking to maintain consistent IDs across frames
        
        Returns
        -------
        list
            List of detections, each containing:
            - bbox: [x1, y1, x2, y2]
            - confidence: float
            - class_id: int (always 0 for person)
            - track_id: int (only if track=True)
        """
        if self.model is None:
            logger.error("Model not loaded")
            return []
        
        try:
            # Run detection or tracking
            if track:
                results = self.model.track(frame, persist=True, verbose=False, conf=self.confidence_threshold)
            else:
                results = self.model(frame, verbose=False, conf=self.confidence_threshold)
            
            # Extract person detections (class 0 in COCO dataset)
            detections = []
            
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None and len(result.boxes) > 0:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        
                        # Only keep person detections (class 0)
                        if class_id != 0:
                            continue
                        
                        # Extract bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        confidence = float(box.conf[0])
                        
                        detection = {
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': confidence,
                            'class_id': class_id,
                            'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)]
                        }
                        
                        # Add track ID if available
                        if track and hasattr(box, 'id') and box.id is not None:
                            detection['track_id'] = int(box.id[0])
                        
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def draw_detections(self, frame, detections, show_ids=True, box_color=(0, 255, 0)):
        """
        Draw bounding boxes on frame
        
        Parameters
        ----------
        frame : numpy.ndarray
            Input frame
        detections : list
            List of detections from detect()
        show_ids : bool
            Whether to show track IDs
        box_color : tuple
            BGR color for bounding boxes
        
        Returns
        -------
        numpy.ndarray
            Annotated frame
        """
        annotated = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 2)
            
            # Prepare label text
            label = f"Person {confidence:.2f}"
            if show_ids and 'track_id' in det:
                label = f"ID:{det['track_id']} {confidence:.2f}"
            
            # Draw label background
            (label_width, label_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(
                annotated,
                (x1, y1 - label_height - 10),
                (x1 + label_width, y1),
                box_color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),  # Black text
                1,
                cv2.LINE_AA
            )
        
        return annotated

