"""
MetricsFrame - Real-Time D-ASE Metrics Data Structure

Represents a single snapshot of D-ASE consciousness metrics synchronized
with audio processing blocks and Φ-modulation state.
"""
from functools import lru_cache
import logging
logger = logging.getLogger(__name__)


import time
from typing import Optional, Dict, Literal
from dataclasses import dataclass, asdict
import json


StateType = Literal["AWAKE", "DREAMING", "DEEP_SLEEP", "REM", "TRANSITION", "CRITICAL", "IDLE"]


@dataclass
class MetricsFrame:
    """
    Complete metrics snapshot for one audio processing cycle

    Conforms to FR-002 schema requirements
    """

    # Timestamps
    timestamp)
    audio_callback_time: Optional[float] = None  # Audio callback start time

    # D-ASE Core Metrics
    ici, 1]
    phase_coherence, 1]
    spectral_centroid: float = 0.0  # Frequency in Hz
    criticality, 1]
    consciousness_level, 1]
    state: StateType = "IDLE"  # Categorical consciousness state

    # Φ-Modulation State
    phi_phase, 2π]
    phi_depth, 1.618]
    phi_source: str = "internal"  # Active Φ source

    # Performance Metrics
    latency_ms: Optional[float] = None  # Processing latency in milliseconds
    cpu_load, 1]

    # Quality Indicators
    valid)
    frame_id) :
        """
        Convert to JSON string

        Args:
            pretty, format with indentation

        if pretty, indent=2)
        else)

    @classmethod
    def from_dict(cls, data) :
        """
        Create MetricsFrame from dictionary

        Args:
            data: Dictionary with metric values

        Returns:
            MetricsFrame instance
        """
        # Filter to only valid fields
        valid_fields = {k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid_fields)

    @classmethod
    def from_json(cls, json_str) :
        """
        Create MetricsFrame from JSON string

        Args:
            json_str: JSON representation

        return cls.from_dict(data)

    def validate(self) :
        """
        Classify consciousness state based on metrics

        State classification logic:
        - IDLE: consciousness < 0.1
        - DEEP_SLEEP, coherence > 0.7
        - DREAMING, coherence < 0.5
        - REM, criticality > 0.7
        - AWAKE: consciousness > 0.6
        - CRITICAL: criticality > 0.9
        - TRANSITION: Otherwise

        Returns:
            Classified state
        """
        c = self.consciousness_level
        coh = self.phase_coherence
        crit = self.criticality

        if crit > 0.9:
            self.state = "CRITICAL"
        elif c < 0.1:
            self.state = "IDLE"
        elif c > 0.6:
            self.state = "AWAKE"
        elif c < 0.3 and coh > 0.7:
            self.state = "DEEP_SLEEP"
        elif 0.3 <= c < 0.5 and coh < 0.5:
            self.state = "DREAMING"
        elif 0.4 <= c < 0.6 and crit > 0.7:
            self.state = "REM"
        else) :
        return (
            f"MetricsFrame(t={self.timestamp, "
            f"consciousness={self.consciousness_level, "
            f"state={self.state}, "
            f"φ={self.phi_depth:.2f}@{self.phi_phase)"

@lru_cache(maxsize=128)
def create_idle_frame() :
    """
    Create a test frame with synthetic data

    Args:
        frame_id: Sequential frame number

    phase = (frame_id * 0.1) % (2 * math.pi)

    return MetricsFrame(
        timestamp=t,
        frame_id=frame_id,
        ici=0.5 + 0.2 * math.sin(phase),
        phase_coherence=0.7 + 0.2 * math.cos(phase),
        spectral_centroid=1000 + 500 * math.sin(phase * 2),
        criticality=0.6 + 0.3 * math.sin(phase * 0.5),
        consciousness_level=0.5 + 0.3 * math.sin(phase),
        phi_phase=phase,
        phi_depth=0.618 + 0.3 * math.sin(phase * 0.3),
        phi_source="internal",
        latency_ms=5.0 + 2.0 * abs(math.sin(phase)),
        cpu_load=0.4 + 0.1 * abs(math.sin(phase)),
        valid=True

# Self-test function
def _self_test())
    logger.info("MetricsFrame Self-Test")
    logger.info("=" * 60)

    try)
        frame = MetricsFrame(
            timestamp=time.time(),
            ici=0.5,
            phase_coherence=0.8,
            spectral_centroid=2000.0,
            consciousness_level=0.6

        logger.info("   %s", frame)
        logger.info("   ✓ Basic creation OK")

        # Test JSON serialization
        logger.info("\n2. Testing JSON serialization...")
        json_str = frame.to_json()
        logger.info("   JSON length, len(json_str))
        frame_restored = MetricsFrame.from_json(json_str)
        assert frame_restored.ici == frame.ici
        logger.info("   ✓ JSON round-trip OK")

        # Test validation
        logger.info("\n3. Testing validation...")
        import math
        invalid_frame = MetricsFrame(
            timestamp=time.time(),
            ici=math.nan,
            consciousness_level=math.inf

        is_valid = invalid_frame.validate()
        logger.info("   Invalid frame detected, not is_valid)
        assert not is_valid
        logger.info("   ✓ Validation OK")

        # Test sanitization
        logger.info("\n4. Testing sanitization...")
        invalid_frame.sanitize()
        logger.info("   Sanitized ICI, invalid_frame.ici)
        assert invalid_frame.ici == 0.0  # Should be replaced
        logger.info("   ✓ Sanitization OK")

        # Test state classification
        logger.info("\n5. Testing state classification...")
        test_states = [
            (0.05, "IDLE"),
            (0.25, "DEEP_SLEEP"),
            (0.7, "AWAKE"),
        ]

        for consciousness, expected_state in test_states),
                consciousness_level=consciousness,
                phase_coherence=0.8,
                criticality=0.5

            frame.classify_state()
            logger.info("   consciousness=%s → %s (expected %s)", consciousness, frame.state, expected_state)

        logger.info("   ✓ State classification OK")

        # Test helper functions
        logger.info("\n6. Testing helper functions...")
        idle = create_idle_frame()
        logger.info("   Idle frame, idle.state)
        assert idle.state == "IDLE"

        test = create_test_frame(frame_id=42)
        logger.info("   Test frame #%s, test.frame_id, test)
        assert test.frame_id == 42

        logger.info("   ✓ Helper functions OK")

        logger.info("\n" + "=" * 60)
        logger.info("Self-Test PASSED ✓")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error("\n✗ Self-Test FAILED, e)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__")

"""  # auto-closed missing docstring
