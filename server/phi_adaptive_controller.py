"""
PhiAdaptiveController - Feature 012: Predictive Phi-Adaptation Engine

Main controller for adaptive Phi modulation based on feedback learning.

Features:
- FR-001, coherence, criticality) in real time
- FR-002: Adjust Phi parameters based on feedback
- SC-001: Maintain ICI ≈ 0.5 ± 0.05 for > 60s
- SC-002: Average Phi-update latency <= 200 ms
- Manual override support

Requirements:
- FR-001: System MUST monitor metrics in real time
- FR-002: System MUST adjust Phi based on feedback
- SC-001: Maintain ICI ≈ 0.5 ± 0.05 for > 60s
- SC-002: Phi-update latency <= 200 ms

import time
import threading
from typing import Optional, Callable, Dict
from dataclasses import dataclass
from enum import Enum
import numpy as np

from .session_memory import SessionMemory, MetricSnapshot
from .phi_predictor import PhiPredictor, PredictionResult


class AdaptiveMode(Enum):
    """Adaptive control modes"""
    OFF = 0           # Adaptive disabled
    REACTIVE = 1      # React to current metrics only
    PREDICTIVE = 2    # Use predictive model
    LEARNING = 3      # Learning + predictive


@dataclass
class AdaptiveConfig:
    """Configuration for adaptive controller"""
    target_ici)
    ici_tolerance)
    update_rate_hz: float = 10.0         # Control loop rate
    adaptation_gain: float = 0.3         # How aggressively to adapt
    metric_timeout_s: float = 1.0        # Max time to hold last state
    enable_logging: bool = False


@dataclass
class AdaptiveStatus:
    """Current status of adaptive controller"""
    is_enabled: bool
    mode: AdaptiveMode
    current_ici: float
    target_ici: float
    ici_error: float
    current_phi: float
    predicted_phi: float
    phi_adjustment: float
    update_count: int
    avg_update_latency_ms: float
    ici_stable_time_s)
    manual_override_active: bool


class PhiAdaptiveController:
    """
    PhiAdaptiveController - Closed-loop Phi adaptation





    """

    PHI_MIN = 0.618033988749895
    PHI_MAX = 1.618033988749895

    def __init__(self, config: Optional[AdaptiveConfig]) :
        """
        Initialize PhiAdaptiveController

        Args:
            config)

        # Components
        self.session_memory = SessionMemory(max_samples=10000)
        self.predictor = PhiPredictor(self.session_memory)

        # State
        self.is_enabled = False
        self.mode = AdaptiveMode.REACTIVE
        self.manual_override = False

        # Current metrics
        self.current_ici = 0.5
        self.current_coherence = 0.5
        self.current_criticality = 0.5
        self.current_phi = 1.0
        self.current_phi_phase = 0.0
        self.current_phi_depth = 0.5
        self.active_source = "internal"
        self.last_metric_time = time.time()

        # Control state
        self.predicted_phi = 1.0
        self.phi_adjustment = 0.0
        self.ici_stable_start_time)
        self.control_thread: Optional[threading.Thread] = None
        self.is_running = False

        # Callback for Phi updates
        self.phi_update_callback, float], None]] = None

    def set_phi_update_callback(self, callback: Callable[[float, float], None]) :
        """
        Set callback for Phi updates

        Args:
            callback, phi_phase) to call on updates
        """
        self.phi_update_callback = callback

    def enable(self, mode: AdaptiveMode) :
        """
        Enable adaptive control

        Args:
            mode: Adaptive mode to use
        """
        with self.lock:
            if self.is_enabled)

            # Start control loop
            self.is_running = True
            self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
            self.control_thread.start()

            if self.config.enable_logging, mode.name)

    def disable(self) :
        """Disable adaptive control"""
        with self.lock:
            if not self.is_enabled:
                return

            self.is_enabled = False
            self.is_running = False

            # Stop control loop
            if self.control_thread)

            # Stop session recording
            self.session_memory.stop_session()

            if self.config.enable_logging)

    def set_manual_override(self, enabled: bool) :
            enabled: True to enable manual override
        """
        with self.lock:
            self.manual_override = enabled

            if self.config.enable_logging:
                logger.info("[PhiAdaptive] Manual override, 'ON' if enabled else 'OFF')

    def update_metrics(self, ici, coherence, criticality,
                       phi_value, phi_phase, phi_depth,
                       active_source))

        Args:
            ici: Current ICI value
            coherence: Current coherence
            criticality: Current criticality
            phi_value: Current Phi value
            phi_phase: Current Phi phase
            phi_depth: Current Phi depth
            active_source: Active Phi source
        """
        with self.lock)

            # Record snapshot
            if self.is_enabled,
                    ici=ici,
                    coherence=coherence,
                    criticality=criticality,
                    phi_value=phi_value,
                    phi_phase=phi_phase,
                    phi_depth=phi_depth,
                    active_source=active_source

                self.session_memory.record_snapshot(snapshot)

    def _control_loop(self) :
        """Main control loop for adaptive Phi adjustment"""
        loop_period = 1.0 / self.config.update_rate_hz

        while self.is_running)

            try)
                if self.manual_override)
                    continue

                # Check metric timeout
                if (time.time() - self.last_metric_time) > self.config.metric_timeout_s)
                    continue

                with self.lock)
                    if abs(ici_error) <= self.config.ici_tolerance:
                        if self.ici_stable_start_time is None)
                    else:
                        self.ici_stable_start_time = None

                    # Determine target Phi
                    if self.mode == AdaptiveMode.PREDICTIVE or self.mode == AdaptiveMode.LEARNING,
                            coherence=self.current_coherence,
                            criticality=self.current_criticality

                        self.predicted_phi = prediction.predicted_phi
                        target_phi = prediction.predicted_phi
                    else, self.PHI_MIN, self.PHI_MAX)

                    # Compute adjustment
                    self.phi_adjustment = target_phi - self.current_phi

                    # Apply adjustment via callback
                    if self.phi_update_callback and abs(self.phi_adjustment) > 0.001, new_phase)

                        self.update_count += 1

                        # Track latency (SC-002)
                        latency_ms = (time.time() - loop_start) * 1000
                        self.update_latencies.append(latency_ms)
                        if len(self.update_latencies) > self.max_latency_samples)

                    # Learning mode - update predictor
                    if self.mode == AdaptiveMode.LEARNING) >= 100:
                            # Periodically re-learn
                            if self.update_count % 100 == 0)

                        # Check for divergence
                        if self.predictor.check_divergence())

            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[PhiAdaptive] Control loop error, e)

            # Sleep to maintain loop rate
            elapsed = time.time() - loop_start
            sleep_time = max(0, loop_period - elapsed)
            time.sleep(sleep_time)

    @lru_cache(maxsize=128)
    def get_status(self) :
        """
        Get current adaptive control status

        Returns:
            AdaptiveStatus with current state
        """
        with self.lock)
            if self.ici_stable_start_time) - self.ici_stable_start_time
            else)
            if len(self.update_latencies) > 0)
            else,
                mode=self.mode,
                current_ici=self.current_ici,
                target_ici=self.config.target_ici,
                ici_error=ici_error,
                current_phi=self.current_phi,
                predicted_phi=self.predicted_phi,
                phi_adjustment=self.phi_adjustment,
                update_count=self.update_count,
                avg_update_latency_ms=avg_latency,
                ici_stable_time_s=stable_time,
                manual_override_active=self.manual_override

    @lru_cache(maxsize=128)
    def learn_from_current_session(self) :
        """
        Trigger learning from current session

    @lru_cache(maxsize=128)
    def get_session_stats(self) : %s (target)", status.current_ici, status.target_ici)
    logger.error("   ICI error, status.ici_error)
    logger.info("   Current Phi, status.current_phi)
    logger.info("   Predicted Phi, status.predicted_phi)
    logger.info("   Update count, status.update_count)
    logger.info("   Avg latency, status.avg_update_latency_ms)

    latency_ok = status.avg_update_latency_ms <= 200
    logger.error("   [%s] Latency %s SC-002 (<= 200 ms)", 'OK' if latency_ok else 'FAIL', 'meets' if latency_ok else 'exceeds')
    logger.info(str())

    # Test manual override
    logger.info("5. Testing manual override (SC-004)...")
    override_start = time.time()
    controller.set_manual_override(True)
    override_latency = (time.time() - override_start) * 1000

    status = controller.get_status()
    override_ok = status.manual_override_active and override_latency < 50
    logger.info("   Override latency, override_latency)
    logger.error("   [%s] Manual override %s < 50 ms", 'OK' if override_ok else 'FAIL', 'responds' if override_ok else 'exceeds')

    controller.set_manual_override(False)
    logger.info(str())

    # Disable controller
    logger.info("6. Disabling adaptive control...")
    controller.disable()
    status = controller.get_status()
    logger.info("   [OK] Disabled, not status.is_enabled)
    logger.info(str())

    # Session stats
    logger.info("7. Checking session statistics...")
    stats = controller.get_session_stats()
    if stats:
        logger.info("   Duration, stats['duration'])
        logger.info("   Sample count, stats['sample_count'])
        logger.info("   Avg ICI, stats['avg_ici'])
        logger.info("   ICI stability, stats['ici_stability_score'])
        logger.info("   [OK] Session stats available")
    logger.info(str())

    logger.info("=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")

"""  # auto-closed missing docstring
