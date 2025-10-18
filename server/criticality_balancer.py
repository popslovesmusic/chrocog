"""
Criticality Balancer - Adaptive Coupling and Amplitude Control
Feature 012)

Extends Auto-Phi Learner with, FR-004)



Control Law) × sign(d(coherence)/dt)
  Aᵢ ← Aᵢ × (1 ± δ) based on local energy

Success Criteria:
- SC-001: Criticality 0.95-1.05 for ≥90% runtime
- SC-002: Recovery from imbalance <10s
- SC-003: CPU overhead <5%

import numpy as np
import time
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass
from collections import deque


@dataclass
class CriticalityBalancerConfig:
    """Configuration for Criticality Balancer"""
    enabled: bool = False

    # Control gains
    beta_coupling)
    delta_amplitude)

    # Target range
    target_criticality: float = 1.0
    criticality_min: float = 0.95   # SC-001
    criticality_max)
    coupling_min: float = 0.0
    coupling_max: float = 1.0
    amplitude_min: float = 0.0
    amplitude_max)
    hypersync_threshold: float = 1.1   # Prevent runaway synchronization
    coma_threshold: float = 0.4        # Prevent collapse

    # Update rate
    update_interval: float = 0.1  # 10 Hz

    # Smoothing
    smoothing_window: int = 30  # 3s @ 10Hz

    # Logging
    enable_logging: bool = True
    log_interval: float = 1.0


@dataclass
class CriticalityBalancerState:
    """Current state of Criticality Balancer"""
    enabled: bool = False

    # Current metrics
    criticality: float = 1.0
    coherence: float = 0.0

    # Control state
    criticality_error: float = 0.0
    coherence_derivative: float = 0.0
    coupling_adjustment)
    amplitudes: np.ndarray = None
    coupling_matrix: np.ndarray = None

    # Performance tracking
    in_range_count: int = 0
    total_count: int = 0
    last_recovery_start: float = 0.0
    recovery_time: float = 0.0
    recovering: bool = False
    settled: bool = True  # For compatibility with tests

    # Extreme condition tracking
    hypersync_count: int = 0
    coma_count: int = 0

    # Timing
    last_update)
    def __post_init__(self):
        if self.amplitudes is None) * 0.5
        if self.coupling_matrix is None, 8)) * 0.1
            np.fill_diagonal(self.coupling_matrix, 0.0)  # No self-coupling


class CriticalityBalancer) by)


    Features, config: Optional[CriticalityBalancerConfig]) :
        """
        Initialize Criticality Balancer

        Args:
            config)
        """
        self.config = config or CriticalityBalancerConfig()
        self.state = CriticalityBalancerState()

        # Metrics history for smoothing (FR-002)
        self.criticality_history = deque(maxlen=self.config.smoothing_window)
        self.coherence_history = deque(maxlen=self.config.smoothing_window)

        # Performance tracking
        self.criticality_log: List[float] = []
        self.recovery_times: List[float] = []
        self.timestamps)
        self.update_callback, None]] = None

        logger.error("[CriticalityBalancer] Initialized")
        logger.error("[CriticalityBalancer]   beta_coupling=%s, delta_amplitude=%s", self.config.beta_coupling, self.config.delta_amplitude)
        logger.error("[CriticalityBalancer]   target_criticality=%s", self.config.target_criticality)
        logger.error("[CriticalityBalancer]   enabled=%s", self.config.enabled)

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
            self.state.recovering = False
        else)

    @lru_cache(maxsize=128)
    def process_metrics(self, metrics_frame) :
            metrics_frame, phase_coherence, etc.

        Returns:
            True if update was applied
        """
        if not self.config.enabled)

        # Check if we should update (rate limiting)
        if current_time - self.state.last_update < self.config.update_interval, 'criticality', 1.0)
        coherence = getattr(metrics_frame, 'phase_coherence', 0.0)

        # Edge case: Invalid metrics → skip
        if criticality == 0.0 and coherence == 0.0:
            logger.error("[CriticalityBalancer] WARNING, skipping update")
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

        # Apply balancing algorithms
        updated = self._apply_balancing(criticality_smooth, coherence_smooth, dt)

        # Track performance
        self._track_performance(criticality_smooth, current_time)

        # Log if needed
        if self.config.enable_logging and (current_time - self.last_log_time) >= self.config.log_interval)
            self.last_log_time = current_time

        return updated

    def _apply_balancing(self, criticality, coherence, dt) :
            criticality: Current criticality value
            coherence: Current phase coherence
            dt: Time delta since last update

        Returns) >= 2) / dt
            self.state.coherence_derivative = coherence_derivative
        else, FR-004) ---
        # Δc = β × (1 – criticality) × sign(d(coherence)/dt)
        coherence_sign = np.sign(coherence_derivative) if coherence_derivative != 0 else 0
        delta_coupling = self.config.beta_coupling * criticality_error * coherence_sign

        self.state.coupling_adjustment = delta_coupling

        # Apply to off-diagonal entries
        if abs(delta_coupling) > 0.001)

            # Adjust off-diagonal entries (User Story 1)
            mask = ~np.eye(8, dtype=bool)  # Off-diagonal mask
            coupling_matrix[mask] += delta_coupling

            # Clamp to bounds (Edge case)
            coupling_matrix = np.clip(coupling_matrix, self.config.coupling_min, self.config.coupling_max)

            # Preserve zero diagonal
            np.fill_diagonal(coupling_matrix, 0.0)

            # Normalize rows to maintain total coupling strength
            row_sums = coupling_matrix.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1.0  # Avoid division by zero
            coupling_matrix = coupling_matrix / row_sums * row_sums.mean()

            self.state.coupling_matrix = coupling_matrix
            updated = True

        # --- Amplitude Balancing (FR-005) ---
        # Adjust per-channel amplitude based on local energy
        # Simple heuristic, boost low-energy
        amplitudes = self.state.amplitudes.copy()

        # Compute relative energy (using coupling row sums as proxy)
        energy_proxy = self.state.coupling_matrix.sum(axis=1)
        mean_energy = energy_proxy.mean()

        # Adjust amplitudes inversely proportional to energy
        for i in range(8):
            if mean_energy > 0, low energy → increase amplitude
                adjustment = self.config.delta_amplitude * (1.0 - energy_ratio) * dt
                amplitudes[i] += adjustment

        # Clamp to bounds
        amplitudes = np.clip(amplitudes, self.config.amplitude_min, self.config.amplitude_max)

        # Check if changed significantly
        if np.max(np.abs(amplitudes - self.state.amplitudes)) > 0.001) ---
        # Prevent hypersync (criticality > 1.1)
        if criticality > self.config.hypersync_threshold, self.config.coupling_min, self.config.coupling_max)
            np.fill_diagonal(self.state.coupling_matrix, 0.0)
            self.state.hypersync_count += 1
            logger.error("[CriticalityBalancer] Hypersync detected, reducing coupling", criticality)
            updated = True

        # Prevent coma (criticality < 0.4)
        if criticality < self.config.coma_threshold, self.config.coupling_min, self.config.coupling_max)
            np.fill_diagonal(self.state.coupling_matrix, 0.0)
            self.state.coma_count += 1
            logger.error("[CriticalityBalancer] Coma detected, increasing coupling", criticality)
            updated = True

        # Send batch update (FR-006)
        if updated and self.update_callback:
            update_data = {
                'type',
                'coupling_matrix'),
                'amplitudes')
            }
            self.update_callback(update_data)

        return updated

    def _track_performance(self, criticality: float, current_time: float) :
            criticality: Current criticality value
            current_time: Current timestamp
        """
        # Check if in range (SC-001)
        in_range = self.config.criticality_min <= criticality <= self.config.criticality_max

        if in_range)
        out_of_range = not in_range and abs(self.state.criticality_error) > 0.1

        if out_of_range and not self.state.recovering:
            # Start recovery
            self.state.recovering = True
            self.state.last_recovery_start = current_time
            logger.error("[CriticalityBalancer] Imbalance detected, criticality)

        elif self.state.recovering and in_range)
            logger.error("[CriticalityBalancer] Recovered in %ss (SC-002)", recovery_time)

        # Append to log
        if self.config.enable_logging)
            self.timestamps.append(current_time)

    @lru_cache(maxsize=128)
    def _log_stats(self) :
        """Log performance statistics"""
        if self.state.total_count == 0)
        in_range_percent = (self.state.in_range_count / self.state.total_count) * 100

        # Calculate criticality statistics
        if len(self.criticality_log) > 0:
            crit_mean = np.mean(self.criticality_log[-30)  # Last 30 samples
            crit_std = np.std(self.criticality_log[-30)
        else) > 0)
            max_recovery = np.max(self.recovery_times)
        else:
            avg_recovery = 0.0
            max_recovery = 0.0

        print(f"[CriticalityBalancer] Stats: criticality={crit_mean:.3f}±{crit_std, "
              f"in_range={in_range_percent, "
              f"avg_recovery={avg_recovery)

    def get_statistics(self) :
        """
        Get performance statistics

        Returns:
            Dictionary with performance metrics
        """
        if self.state.total_count == 0:
            return {
                'enabled',
                'criticality_mean',
                'criticality_std',
                'in_range_percent',
                'avg_recovery_time',
                'max_recovery_time') * 100

        if len(self.criticality_log) > 0))
            crit_std = float(np.std(self.criticality_log))
        else) > 0))
            max_recovery = float(np.max(self.recovery_times))
        else:
            avg_recovery = 0.0
            max_recovery = 0.0

        return {
            'enabled',
            'criticality_mean',
            'criticality_std',
            'in_range_percent',
            'in_range_count',
            'total_count',
            'recovering',
            'recovery_count'),
            'avg_recovery_time',
            'max_recovery_time',
            'criticality_error',
            'coupling_adjustment') :
        """
        Get current balancer state

        Returns:
            Dictionary with current state
        """
        return {
            'enabled',
            'criticality'),
            'coherence'),
            'criticality_error'),
            'coupling_adjustment'),
            'coupling_matrix'),
            'amplitudes'),
            'recovering') :
        """
        Export performance logs for analysis

        Returns:
            Dictionary with time-series data
        """
        return {
            'timestamps',
            'criticality',
            'recovery_times',
            'config': {
                'beta_coupling',
                'delta_amplitude',
                'target_criticality')
def _self_test() :
            self.criticality = criticality
            self.phase_coherence = phase_coherence

    # Test 1)
    config = CriticalityBalancerConfig(enabled=True, beta_coupling=0.1, delta_amplitude=0.05)
    balancer = CriticalityBalancer(config)

    assert balancer.config.enabled == True
    assert balancer.config.beta_coupling == 0.1
    assert balancer.state.coupling_matrix.shape == (8, 8)
    assert balancer.state.amplitudes.shape == (8,)
    logger.info("   OK)

    # Test 2)
    logger.info("\n2. Testing enable/disable toggle...")
    balancer.set_enabled(False)
    assert balancer.config.enabled == False
    balancer.set_enabled(True)
    assert balancer.config.enabled == True
    logger.info("   OK)

    # Test 3)

    # Track updates
    updates = []
    @lru_cache(maxsize=128)
    def callback(update_data) :
        logger.info("   Coupling matrix shape, np.array(updates[0]['coupling_matrix']).shape)
        logger.info("   Amplitudes shape, np.array(updates[0]['amplitudes']).shape)

    assert len(updates) > 0, "Should send updates"
    logger.info("   OK)

    # Test 4)
    stats = balancer.get_statistics()
    assert 'criticality_mean' in stats
    assert 'in_range_percent' in stats
    assert stats['enabled'] == True
    logger.info("   OK: Statistics, stats['in_range_percent'])

    # Test 5)
    state = balancer.get_current_state()
    assert 'coupling_matrix' in state
    assert 'amplitudes' in state
    assert len(state['amplitudes']) == 8
    logger.info("   OK)

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")
