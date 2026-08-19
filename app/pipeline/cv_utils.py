import os
from pathlib import Path
import numpy as np
try:
    import cv2
except ImportError:
    cv2 = None

from app.models.frame import FramePacket
from app.models.observation import StructuredObservation
from app.core.logging import logger

FRAMES_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "rendered_frames"

class DroneCVRenderer:
    """
    OpenCV-powered Computer Vision engine for Drone Surveillance.
    Handles synthetic optical frame generation, telemetry HUD overlays,
    bounding box rendering, and visual frame export.
    """
    def __init__(self, output_dir: Path = FRAMES_OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_and_annotate_frame(self, frame: FramePacket, observation: StructuredObservation) -> str:
        """
        Renders a simulated video frame with OpenCV, drawing:
        1. Synthetic aerial background corresponding to location & time-of-day
        2. Telemetry HUD (GPS, Altitude, Heading, Battery)
        3. Visual bounding boxes for detected objects (Vehicles, People, Animals)
        4. Threat Alert banners
        """
        if cv2 is None:
            logger.warning("OpenCV (cv2) not available. Skipping frame image generation.")
            return ""

        width, height = 640, 480
        hour = frame.timestamp.hour
        is_night = hour >= 22 or hour <= 5

        # 1. Base Canvas (Night vs Day background simulation)
        if is_night:
            canvas = np.full((height, width, 3), (25, 20, 15), dtype=np.uint8) # Dark asphalt/night
            # Draw ground grid
            for y in range(0, height, 40):
                cv2.line(canvas, (0, y), (width, y), (40, 35, 30), 1)
        else:
            canvas = np.full((height, width, 3), (80, 130, 90), dtype=np.uint8) # Daytime perimeter terrain
            # Draw road/bay
            cv2.rectangle(canvas, (100, 150), (540, 450), (90, 95, 100), -1)

        # 2. Draw Simulated Entities with Bounding Boxes
        for idx, obj in enumerate(observation.objects):
            if obj.object_type == "person":
                box = (260, 200, 340, 360)
                color = (0, 0, 220) if is_night else (0, 165, 255) # Red for night threat
                cv2.rectangle(canvas, (box[0], box[1]), (box[2], box[3]), color, 2)
                cv2.putText(canvas, f"{obj.label} ({int(obj.confidence*100)}%)", (box[0], box[1] - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
            elif obj.object_type == "vehicle":
                box = (180, 220, 460, 380)
                color = (255, 140, 0) # Cyan/Blue for vehicle
                cv2.rectangle(canvas, (box[0], box[1]), (box[2], box[3]), color, 2)
                cv2.putText(canvas, f"{obj.label} [{obj.attributes.get('color', '')}]", (box[0], box[1] - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
            elif obj.object_type == "animal":
                box = (380, 180, 480, 280)
                color = (0, 255, 127) # Green for wildlife
                cv2.rectangle(canvas, (box[0], box[1]), (box[2], box[3]), color, 2)
                cv2.putText(canvas, f"{obj.label} (Wildlife)", (box[0], box[1] - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

        # 3. Telemetry HUD Overlay (Top Banner)
        cv2.rectangle(canvas, (0, 0), (width, 40), (10, 10, 15), -1)
        cv2.line(canvas, (0, 40), (width, 40), (0, 200, 255), 1)

        hud_text_left = f"DRONE-01 | {frame.telemetry.location_tag.upper()} | ALT: {frame.telemetry.altitude:.1f}m"
        hud_text_right = f"{frame.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        
        cv2.putText(canvas, hud_text_left, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 230, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, hud_text_right, (430, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1, cv2.LINE_AA)

        # 4. Crosshair in Center
        cx, cy = width // 2, height // 2
        cv2.drawMarker(canvas, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 1)

        # 5. Save to disk
        out_filename = f"{frame.frame_id}.jpg"
        out_path = self.output_dir / out_filename
        cv2.imwrite(str(out_path), canvas)
        logger.debug(f"OpenCV rendered frame saved to: {out_path}")
        return str(out_path)

drone_cv_renderer = DroneCVRenderer()
