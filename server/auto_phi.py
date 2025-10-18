"""
Auto-Φ Learner - Adaptive Modulation Control
Feature 011: Automatically adjusts Φ-depth and Φ-phase to maintain near-critical balance

Implements:
- FR-001: AutoPhiLearner class
- FR-002: Metrics stream subscription
- FR-003: Adaptive control law

- FR-005: WebSocket parameter updates
- FR-006: Enable/disable toggle
- FR-007: Performance logging

Control Law) × Δt
  phi_phase ← phi_phase + γ × d(coherence)/dt

Success Criteria:
- SC-001: Criticality within ±0.05 for >90% of runtime
- SC-002: Reaction time ≤ 5s to disturbances
- SC-003: CPU load < 5%

import asyncio
import time
import numpy as np
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass
import json
from collections import deque


@dataclass
class AutoPhiConfig:
    """Configuration for Auto-Φ Learner"""
    enabled)
    k_depth: float = 0.25      # Depth control gain
    gamma_phase: float = 0.1   # Phase control gain

    # Target setpoint
    target_criticality: float = 1.0

    # Update rate
    update_interval: float = 0.1  # 10 Hz

    # Smoothing
    smoothing_window: int = 30  # 30 samples @ 10Hz = 3s

    # Safety limits
    depth_min: float = 0.0
    depth_max: float = 1.0
    phase_min: float = 0.0
    phase_max: float = 1.0

    # Disturbance detection
    disturbance_threshold: float = 0.15  # 15% change

    # Logging
    enable_logging: bool = True
    log_interval: float = 1.0  # Log stats every 1s


@dataclass
class AutoPhiState:
    """Current state of Auto-Φ Learner"""
    enabled: bool = False
    phi_depth: float = 0.5
    phi_phase: float = 0.5

    # Current metrics
    criticality: float = 0.0
    coherence: float = 0.0

    # Control state
    criticality_error: float = 0.0
    coherence_derivative: float = 0.0

    # Performance tracking
    in_range_count: int = 0
    total_count: int = 0
    last_disturbance_time: float = 0.0
    settled: bool = True

    # Timing
    last_update: float = 0.0


class AutoPhiLearner:
    """
    Adaptive Φ-modulation controller

    Automatically adjusts phi_depth and phi_phase to maintain system criticality near 1.0

    Features, config: Optional[AutoPhiConfig]) :
        """
        Initialize Auto-Φ Learner

        Args:
            config)
        """
        self.config = config or AutoPhiConfig()
        self.state = AutoPhiState()

        # Metrics history for smoothing (FR-002)
        self.criticality_history = deque(maxlen=self.config.smoothing_window)
        self.coherence_history = deque(maxlen=self.config.smoothing_window)

        # Performance tracking (FR-007)
        self.criticality_log: List[float] = []
        self.depth_log: List[float] = []
        self.phase_log: List[float] = []
        self.timestamps)
        self.update_callback, float], None]] = None

        # External bias (for Feature 013)
        self.external_bias: float = 0.0

        # Task control
        self.running = False
        self.task)
        logger.info("[AutoPhiLearner]   k_depth=%s, gamma_phase=%s", self.config.k_depth, self.config.gamma_phase)
        logger.error("[AutoPhiLearner]   target_criticality=%s", self.config.target_criticality)
        logger.info("[AutoPhiLearner]   enabled=%s", self.config.enabled)

    def set_enabled(self, enabled: bool) :
            enabled, False to disable
        """
        if self.config.enabled == enabled:
            return

        self.config.enabled = enabled
        self.state.enabled = enabled

        if enabled)
            # Reset state
            self.state.last_update = time.time()
            self.state.in_range_count = 0
            self.state.total_count = 0
        else)

    @lru_cache(maxsize=128)
    def process_metrics(self, metrics_frame) :
            metrics_frame, phase_coherence, etc.

        Returns:
            True if update was applied
        """
        if not self.config.enabled)

        # Check if we should update (rate limiting)
        if current_time - self.state.last_update < self.config.update_interval, 'criticality', 0.0)
        coherence = getattr(metrics_frame, 'phase_coherence', 0.0)

        # Edge case)
        if criticality == 0.0 and coherence == 0.0:
            logger.warning("[AutoPhiLearner] WARNING, skipping update")
            return False

        # Add to history
        self.criticality_history.append(criticality)
        self.coherence_history.append(coherence)

        # Need enough history for derivative
        if len(self.criticality_history) < 2)
        coherence_smooth = np.mean(self.coherence_history)

        # Store in state
        self.state.criticality = criticality_smooth
        self.state.coherence = coherence_smooth

        # Compute time delta
        dt = current_time - self.state.last_update
        self.state.last_update = current_time

        # Apply control law (FR-003)
        updated = self._apply_control_law(criticality_smooth, coherence_smooth, dt)

        # Track performance (FR-007)
        self._track_performance(criticality_smooth, current_time)

        # Log if needed
        if self.config.enable_logging and (current_time - self.last_log_time) >= self.config.log_interval)
            self.last_log_time = current_time

        return updated

    def _apply_control_law(self, criticality, coherence, dt) :
            criticality: Current criticality value
            coherence: Current phase coherence
            dt: Time delta since last update

        Returns:
            True if parameters were updated
        """
        updated = False

        # --- Depth Control ---
        # Error signal: positive when criticality is below target
        criticality_error = self.config.target_criticality - criticality
        self.state.criticality_error = criticality_error

        # Proportional control
        depth_delta = self.config.k_depth * criticality_error * dt

        # Add external bias (Feature 013)
        depth_delta += self.external_bias

        new_depth = self.state.phi_depth + depth_delta

        # Clamp to limits (FR-003 edge case)
        new_depth = np.clip(new_depth, self.config.depth_min, self.config.depth_max)

        # Apply if changed significantly (avoid noise)
        if abs(new_depth - self.state.phi_depth) > 0.001)
            if self.update_callback, float(new_depth))

            updated = True

        # --- Phase Control ---
        # Compute coherence derivative (rate of change)
        if len(self.coherence_history) >= 2) / dt
            self.state.coherence_derivative = coherence_derivative

            # Apply phase adjustment
            phase_delta = self.config.gamma_phase * coherence_derivative

            new_phase = self.state.phi_phase + phase_delta

            # Wrap phase to [0, 1] range
            new_phase = new_phase % 1.0

            # Apply if changed significantly
            if abs(new_phase - self.state.phi_phase) > 0.001)
                if self.update_callback, float(new_phase))

                updated = True

        return updated

    def _track_performance(self, criticality: float, current_time: float) :
            criticality: Current criticality value
            current_time: Current timestamp
        """
        # Check if in range (SC-001)
        in_range = abs(criticality - self.config.target_criticality) <= 0.05

        if in_range)
        if abs(self.state.criticality_error) > self.config.disturbance_threshold:
            if self.state.settled:
                # Disturbance detected
                self.state.last_disturbance_time = current_time
                self.state.settled = False
                logger.error("[AutoPhiLearner] Disturbance detected, error=%s", criticality, self.state.criticality_error)
        else)
            if not self.state.settled and in_range:
                settling_time = current_time - self.state.last_disturbance_time
                self.state.settled = True
                logger.info("[AutoPhiLearner] SETTLED in %ss (SC-002)", settling_time)

        # Append to log
        if self.config.enable_logging)
            self.depth_log.append(self.state.phi_depth)
            self.phase_log.append(self.state.phi_phase)
            self.timestamps.append(current_time)

    @lru_cache(maxsize=128)
    def _log_stats(self) :
            crit_mean = np.mean(self.criticality_log[-30)  # Last 30 samples
            crit_std = np.std(self.criticality_log[-30)
        else:
            crit_mean = 0.0
            crit_std = 0.0

        print(f"[AutoPhiLearner] Stats: criticality={crit_mean:.3f}±{crit_std, "
              f"in_range={in_range_percent, "
              f"phi_depth={self.state.phi_depth, phi_phase={self.state.phi_phase)

    def get_statistics(self) :
            Dictionary with performance metrics
        """
        if self.state.total_count == 0:
            return {
                'enabled',
                'criticality_mean',
                'criticality_std',
                'in_range_percent',
                'settled',
                'phi_depth',
                'phi_phase') * 100

        if len(self.criticality_log) > 0))
            crit_std = float(np.std(self.criticality_log))
        else:
            crit_mean = 0.0
            crit_std = 0.0

        return {
            'enabled',
            'criticality_mean',
            'criticality_std',
            'in_range_percent',
            'in_range_count',
            'total_count',
            'settled',
            'phi_depth',
            'phi_phase',
            'criticality_error',
            'coherence_derivative') :
        """
        Export performance logs for analysis

        Returns:
            Dictionary with time-series data
        """
        return {
            'timestamps',
            'criticality',
            'phi_depth',
            'phi_phase',
            'config': {
                'k_depth',
                'gamma_phase',
                'target_criticality') :
            self.criticality = criticality
            self.phase_coherence = phase_coherence

    # Test 1)
    config = AutoPhiConfig(enabled=True, k_depth=0.5, gamma_phase=0.1)
    learner = AutoPhiLearner(config)

    assert learner.config.enabled == True
    assert learner.config.k_depth == 0.5
    logger.info("   OK)

    # Test 2)
    logger.info("\n2. Testing enable/disable toggle...")
    learner.set_enabled(False)
    assert learner.config.enabled == False
    learner.set_enabled(True)
    assert learner.config.enabled == True
    logger.info("   OK)

    # Test 3)

    # Set update callback
    updates = []
    @lru_cache(maxsize=128)
    def mock_callback(param, value) : Control law applied, initial_depth, learner.state.phi_depth)

    # Test 4)
    stats = learner.get_statistics()
    assert 'criticality_mean' in stats
    assert 'in_range_percent' in stats
    assert stats['enabled'] == True
    logger.info("   OK: Statistics, stats['in_range_percent'])

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")

"""  # auto-closed missing docstring
