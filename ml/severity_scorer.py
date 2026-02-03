"""
Severity Scoring Logic for Accident Incidents
Calculates severity based on multiple factors
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"  
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class SeverityFactors:
    """Factors considered in severity scoring"""
    vehicle_count: int = 0
    pedestrian_involved: bool = False
    is_rollover: bool = False
    is_multi_vehicle: bool = False
    fire_smoke_detected: bool = False
    estimated_speed: Optional[float] = None  # km/h
    detection_confidence: float = 0.0
    traffic_density: str = "normal"  # low, normal, high


class SeverityScorer:
    """
    Calculates severity level for detected incidents.
    Uses weighted scoring based on multiple factors.
    """
    
    # Scoring weights
    WEIGHTS = {
        "pedestrian": 3.0,
        "rollover": 2.5,
        "multi_vehicle": 2.0,
        "fire_smoke": 3.5,
        "vehicle_count": 0.5,  # per vehicle above 1
        "high_speed": 2.0,      # if speed > 60 km/h
        "high_traffic": 1.0
    }
    
    # Severity thresholds
    THRESHOLDS = {
        "CRITICAL": 6.0,
        "HIGH": 4.0,
        "MEDIUM": 2.0,
        "LOW": 0.0
    }
    
    def __init__(self, custom_weights: Optional[dict] = None):
        """Initialize scorer with optional custom weights"""
        self.weights = self.WEIGHTS.copy()
        if custom_weights:
            self.weights.update(custom_weights)
    
    def calculate_severity(self, factors: SeverityFactors) -> tuple:
        """
        Calculate severity level based on incident factors.
        
        Args:
            factors: SeverityFactors dataclass with incident details
            
        Returns:
            Tuple of (SeverityLevel, score, breakdown)
        """
        score = 0.0
        breakdown = {}
        
        # Pedestrian involvement (highest weight)
        if factors.pedestrian_involved:
            points = self.weights["pedestrian"]
            score += points
            breakdown["pedestrian_involved"] = points
        
        # Rollover detection
        if factors.is_rollover:
            points = self.weights["rollover"]
            score += points
            breakdown["rollover"] = points
        
        # Multi-vehicle pile-up
        if factors.is_multi_vehicle:
            points = self.weights["multi_vehicle"]
            score += points
            breakdown["multi_vehicle"] = points
        
        # Fire/smoke detection
        if factors.fire_smoke_detected:
            points = self.weights["fire_smoke"]
            score += points
            breakdown["fire_smoke"] = points
        
        # Vehicle count (additional vehicles beyond 1)
        if factors.vehicle_count > 1:
            extra_vehicles = factors.vehicle_count - 1
            points = extra_vehicles * self.weights["vehicle_count"]
            score += points
            breakdown["extra_vehicles"] = points
        
        # High-speed collision
        if factors.estimated_speed and factors.estimated_speed > 60:
            points = self.weights["high_speed"]
            score += points
            breakdown["high_speed"] = points
        
        # High traffic area
        if factors.traffic_density == "high":
            points = self.weights["high_traffic"]
            score += points
            breakdown["high_traffic"] = points
        
        # Apply confidence scaling
        score *= min(factors.detection_confidence, 1.0) + 0.5
        
        # Determine severity level
        if score >= self.THRESHOLDS["CRITICAL"]:
            level = SeverityLevel.CRITICAL
        elif score >= self.THRESHOLDS["HIGH"]:
            level = SeverityLevel.HIGH
        elif score >= self.THRESHOLDS["MEDIUM"]:
            level = SeverityLevel.MEDIUM
        else:
            level = SeverityLevel.LOW
        
        logger.info(f"Severity calculated: {level.value} (score: {score:.2f})")
        
        return level, score, breakdown
    
    def quick_severity(
        self,
        vehicle_count: int,
        pedestrian_involved: bool = False,
        is_rollover: bool = False,
        confidence: float = 0.8
    ) -> SeverityLevel:
        """
        Quick severity calculation with minimal parameters.
        
        Args:
            vehicle_count: Number of vehicles involved
            pedestrian_involved: Whether pedestrian is involved
            is_rollover: Whether rollover is detected
            confidence: Detection confidence
            
        Returns:
            SeverityLevel enum
        """
        factors = SeverityFactors(
            vehicle_count=vehicle_count,
            pedestrian_involved=pedestrian_involved,
            is_rollover=is_rollover,
            detection_confidence=confidence
        )
        
        level, _, _ = self.calculate_severity(factors)
        return level
    
    def get_priority_score(self, severity: SeverityLevel) -> int:
        """
        Get numeric priority score for sorting/ordering.
        Higher = more urgent.
        """
        priority_map = {
            SeverityLevel.CRITICAL: 4,
            SeverityLevel.HIGH: 3,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 1
        }
        return priority_map.get(severity, 0)
    
    def should_auto_dispatch_ambulance(self, severity: SeverityLevel) -> bool:
        """
        Determine if severity warrants ambulance prompt.
        Note: Actual dispatch still requires human confirmation.
        """
        return severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
    
    def get_response_recommendation(self, severity: SeverityLevel) -> dict:
        """
        Get recommended response actions based on severity.
        """
        recommendations = {
            SeverityLevel.CRITICAL: {
                "ambulance": "IMMEDIATE - Prompt operator for dispatch",
                "police": "IMMEDIATE - Auto-generate report",
                "notification": "Flash alert + audio alarm",
                "priority": "P0 - Handle immediately"
            },
            SeverityLevel.HIGH: {
                "ambulance": "RECOMMENDED - Prompt operator",
                "police": "Generate report within 5 minutes",
                "notification": "Visual alert",
                "priority": "P1 - Handle within 2 minutes"
            },
            SeverityLevel.MEDIUM: {
                "ambulance": "OPTIONAL - Based on verification",
                "police": "Generate report after verification",
                "notification": "Standard notification",
                "priority": "P2 - Handle within 10 minutes"
            },
            SeverityLevel.LOW: {
                "ambulance": "NOT REQUIRED",
                "police": "Log only, no immediate report",
                "notification": "Low priority notification",
                "priority": "P3 - Review when available"
            }
        }
        return recommendations.get(severity, recommendations[SeverityLevel.LOW])


# Convenience function for quick scoring
def calculate_severity(
    vehicle_count: int = 1,
    pedestrian_involved: bool = False,
    is_rollover: bool = False,
    is_multi_vehicle: bool = False,
    fire_smoke: bool = False,
    confidence: float = 0.85
) -> tuple:
    """
    Convenience function for quick severity calculation.
    
    Returns:
        Tuple of (SeverityLevel, score, recommendation)
    """
    scorer = SeverityScorer()
    
    factors = SeverityFactors(
        vehicle_count=vehicle_count,
        pedestrian_involved=pedestrian_involved,
        is_rollover=is_rollover,
        is_multi_vehicle=is_multi_vehicle,
        fire_smoke_detected=fire_smoke,
        detection_confidence=confidence
    )
    
    level, score, breakdown = scorer.calculate_severity(factors)
    recommendation = scorer.get_response_recommendation(level)
    
    return level, score, recommendation


if __name__ == "__main__":
    # Test severity scoring
    print("Testing Severity Scorer\n" + "="*40)
    
    # Test case 1: Minor collision
    level, score, rec = calculate_severity(vehicle_count=2, confidence=0.8)
    print(f"Minor collision: {level.value} (score: {score:.2f})")
    
    # Test case 2: Pedestrian involved
    level, score, rec = calculate_severity(vehicle_count=1, pedestrian_involved=True)
    print(f"Pedestrian hit: {level.value} (score: {score:.2f})")
    
    # Test case 3: Multi-vehicle with rollover
    level, score, rec = calculate_severity(
        vehicle_count=4, 
        is_multi_vehicle=True,
        is_rollover=True
    )
    print(f"Multi-vehicle rollover: {level.value} (score: {score:.2f})")
    
    # Test case 4: Fire detected
    level, score, rec = calculate_severity(vehicle_count=2, fire_smoke=True)
    print(f"Fire detected: {level.value} (score: {score:.2f})")
