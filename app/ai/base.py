from abc import ABC, abstractmethod
from app.models.frame import FramePacket
from app.models.observation import StructuredObservation

class BaseVLMEngine(ABC):
    @abstractmethod
    def analyze_frame(self, frame: FramePacket) -> StructuredObservation:
        """
        Analyze a synchronized video frame and return structured security observations.
        """
        pass
