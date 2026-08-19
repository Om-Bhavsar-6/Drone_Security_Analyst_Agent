from typing import List, Dict, Any
from app.models.alert import SeverityLevel

class SeverityScorer:
    """
    Computes a weighted risk score (0.0 - 1.0) and derives appropriate SeverityLevel.
    Distinguishes detection confidence from threat severity.
    """
    
    @staticmethod
    def calculate_risk(
        base_threat: float,
        is_night: bool = False,
        is_restricted_zone: bool = False,
        is_loitering: bool = False,
        is_repeated_anomaly: bool = False,
        risk_indicators: List[str] = None
    ) -> tuple[float, SeverityLevel]:
        risk_score = base_threat
        
        if is_night:
            risk_score += 0.25
        if is_restricted_zone:
            risk_score += 0.20
        if is_loitering:
            risk_score += 0.20
        if is_repeated_anomaly:
            risk_score += 0.15
            
        if risk_indicators:
            for ind in risk_indicators:
                if ind in ["hooded_garment", "restricted_perimeter", "face_obscured"]:
                    risk_score += 0.10
                elif ind == "wildlife_non_threat":
                    risk_score = 0.05
                    
        # Clamp to [0.0, 1.0]
        risk_score = max(0.0, min(1.0, risk_score))
        
        # Derive severity level
        if risk_score >= 0.80:
            severity = SeverityLevel.CRITICAL
        elif risk_score >= 0.60:
            severity = SeverityLevel.HIGH
        elif risk_score >= 0.30:
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
            
        return round(risk_score, 2), severity
