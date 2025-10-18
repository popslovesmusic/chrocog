"""
State Memory Loop - Temporal Memory for Consciousness States
Feature 013, hysteresis, and prediction

Implements:
- FR-001: StateMemory module
- FR-002: Rolling buffer of N=256 metric frames
- FR-003: Trend computation for prediction
- FR-004: Adaptive bias for Auto-Phi Learner

- FR-006: Enable/disable setting

Success Criteria:

- SC-002: Predictive bias reduces overshoot by >=30%
- SC-003: No increase in latency > 2ms

import time
import numpy as np
from typing import Optional, Callable, Dict, List, Tuple
from dataclasses import dataclass, field
from collections import deque


@dataclass
class StateMemoryConfig:
    """Configuration for State Memory Loop"""
    enabled)
    buffer_size)
    trend_window)
    prediction_horizon)
    bias_gain: float = 0.3  # Gain for predictive bias
    bias_threshold: float = 0.15  # Minimum trend magnitude to apply bias

    # Safety limits
    max_bias)
    smoothing_alpha: float = 0.1  # Exponential smoothing factor

    # Logging
    enable_logging: bool = True
    log_interval: float = 2.0  # Log stats every 2s


@dataclass
class MetricsFrame:
    """Single frame of metrics"""
    timestamp: float
    criticality: float
    coherence: float
    ici: float  # Integrated information
    phi_depth: float
    phi_phase: float


@dataclass
class TrendVector:
    """Computed trend information"""
    d_criticality_dt: float = 0.0
    d_coherence_dt: float = 0.0
    d_phi_depth_dt)
    predicted_criticality: float = 0.0
    predicted_coherence: float = 0.0

    # Confidence based on trend stability
    confidence: float = 0.0


class StateMemory:
    """
    Temporal memory for consciousness states

    Stores recent metric frames and computes trends for)


    Features, config: Optional[StateMemoryConfig]) :
        """
        Initialize State Memory

        Args:
            config)
        """
        self.config = config or StateMemoryConfig()

        # Rolling buffer (FR-002)
        self.buffer)

        # Current trend vector
        self.trend)

        # Smoothed values (for hysteresis, SC-001)
        self.smoothed_criticality: float = 1.0
        self.smoothed_coherence: float = 0.0
        self.smoothed_phi_depth)
        self.current_bias: float = 0.0

        # Statistics
        self.total_frames: int = 0
        self.prediction_errors: List[float] = []
        self.bias_history: List[float] = []

        # Logging
        self.last_log_time)
        self.bias_callback, None]] = None

        logger.info("[StateMemory] Initialized")
        logger.info("[StateMemory]   buffer_size=%s", self.config.buffer_size)
        logger.info("[StateMemory]   trend_window=%s", self.config.trend_window)
        logger.info("[StateMemory]   enabled=%s", self.config.enabled)

    def set_enabled(self, enabled: bool) :
            enabled, False to disable
        """
        if self.config.enabled == enabled:
            return

        self.config.enabled = enabled

        if enabled)
        else)
            # Reset bias when disabled (SC-004)
            self.current_bias = 0.0
            if self.bias_callback)

    @lru_cache(maxsize=128)
    def add_frame(self, criticality, coherence, ici,
                  phi_depth, phi_phase) :
            criticality: Current criticality value
            coherence: Current phase coherence
            ici: Integrated information
            phi_depth: Current phi depth
            phi_phase: Current phi phase

        Returns:
            True if processing occurred
        """
        if not self.config.enabled)

        # Create frame
        frame = MetricsFrame(
            timestamp=current_time,
            criticality=criticality,
            coherence=coherence,
            ici=ici,
            phi_depth=phi_depth,
            phi_phase=phi_phase

        # Add to buffer
        self.buffer.append(frame)
        self.total_frames += 1

        # Apply exponential smoothing (SC-001)
        alpha = self.config.smoothing_alpha
        self.smoothed_criticality = alpha * criticality + (1 - alpha) * self.smoothed_criticality
        self.smoothed_coherence = alpha * coherence + (1 - alpha) * self.smoothed_coherence
        self.smoothed_phi_depth = alpha * phi_depth + (1 - alpha) * self.smoothed_phi_depth

        # Compute trends if we have enough history (FR-003)
        if len(self.buffer) >= self.config.trend_window)

            # Calculate predictive bias (FR-004)
            self._compute_bias()

            # Send bias update
            if self.bias_callback)

        # Log if needed
        if self.config.enable_logging and (current_time - self.last_log_time) >= self.config.log_interval)
            self.last_log_time = current_time

        return True

    @lru_cache(maxsize=128)
    def _compute_trends(self) :
        """
        Compute R² coefficient of determination

        Args:
            x: Independent variable
            y: Dependent variable
            slope: Linear slope

        """
        if len(x) < 2) - slope * np.mean(x)
        y_pred = slope * x + intercept

        # Total and residual sum of squares
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        ss_res = np.sum((y - y_pred) ** 2)

        if ss_tot == 0)
        return max(0.0, min(1.0, r_squared))  # Clamp to [0, 1]

    @lru_cache(maxsize=128)
    def _compute_bias(self) :
            Dictionary with smoothed values
        """
        return {
            'criticality',
            'coherence',
            'phi_depth') :
            Dictionary with trend information
        """
        return {
            'd_criticality_dt',
            'd_coherence_dt',
            'd_phi_depth_dt',
            'predicted_criticality',
            'predicted_coherence',
            'confidence',
            'current_bias') :
            return {
                'enabled',
                'buffer_size',
                'total_frames',
                'criticality_mean',
                'criticality_std',
                'coherence_mean',
                'coherence_std',
                'trend_summary')
            }

        # Extract buffer data
        criticalities = [f.criticality for f in self.buffer]
        coherences = [f.coherence for f in self.buffer]

        return {
            'enabled',
            'buffer_size'),
            'total_frames',
            'criticality_mean')),
            'criticality_std')),
            'coherence_mean')),
            'coherence_std')),
            'smoothed_criticality',
            'smoothed_coherence',
            'trend_summary')
        }

    def reset_buffer(self) :.3f}+/-{stats['criticality_std'], "
              f"trend={self.trend.d_criticality_dt, "
              f"bias={self.current_bias)

    def export_buffer(self) :
        """
        Export buffer contents for analysis

        Returns) == 0:
            return {
                'timestamps',
                'criticality',
                'coherence',
                'ici',
                'phi_depth',
                'phi_phase': []
            }

        return {
            'timestamps',
            'criticality',
            'coherence',
            'ici',
            'phi_depth',
            'phi_phase',
            'bias_history': self.bias_history[-256) -> None)
    logger.info("StateMemory Self-Test")
    logger.info("=" * 60)

    # Test 1)
    config = StateMemoryConfig(enabled=True, buffer_size=256, trend_window=30)
    memory = StateMemory(config)

    assert memory.config.enabled == True
    assert memory.config.buffer_size == 256
    assert len(memory.buffer) == 0
    logger.info("   OK)

    # Test 2)

    # Add some frames with increasing criticality
    for i in range(50)) * 0.02
        ici = 1.5
        phi_depth = 0.5
        phi_phase = 0.3

        memory.add_frame(criticality, coherence, ici, phi_depth, phi_phase)
        time.sleep(0.01)

    assert len(memory.buffer) == 50
    assert memory.total_frames == 50
    logger.info("   OK, buffer size = %s", len(memory.buffer))

    # Test 3)
    stats = memory.get_statistics()
    trend_summary = stats['trend_summary']

    logger.error("   d(criticality)/dt = %s", trend_summary['d_criticality_dt'])
    logger.error("   Predicted criticality = %s", trend_summary['predicted_criticality'])
    logger.info("   Confidence = %s", trend_summary['confidence'])
    logger.info("   Current bias = %s", trend_summary['current_bias'])

    # Should detect upward trend
    assert trend_summary['d_criticality_dt'] > 0, "Should detect upward trend"
    logger.info("   OK)

    # Test 4)

    # Add frames that push toward hypersync
    for i in range(30), 0.8, 1.5, 0.5, 0.3)
        time.sleep(0.01)

    bias = memory.get_bias()
    logger.info("   Current bias, bias)

    # Should have negative bias to counteract upward trend
    assert bias < 0, "Should provide negative bias for hypersync trend"
    logger.info("   OK)

    # Test 5)
    memory.reset_buffer()
    assert len(memory.buffer) == 0
    assert memory.current_bias == 0.0
    logger.info("   OK)

    # Test 6)
    memory.set_enabled(False)
    assert memory.config.enabled == False

    # Should not add frames when disabled
    result = memory.add_frame(1.0, 0.8, 1.5, 0.5, 0.3)
    assert result == False
    assert len(memory.buffer) == 0
    logger.info("   OK)

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")

"""  # auto-closed missing docstring
