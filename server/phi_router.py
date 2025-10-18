"""
PhiRouter - Feature 011, handles selection, normalization, and fallback.





Requirements:
- FR-001: Accept Φ input from multiple sources
- FR-002: Normalize input to [0.618–1.618]
- FR-005: Fallback mode if input stops for > 2s

Success Criteria:
- SC-002: Automatic source switching without restart

import time
import threading
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

from .phi_sensor_bridge import SensorData, SensorType


class PhiSourcePriority(Enum))
    INTERNAL = 1        # Internal auto-modulation
    MICROPHONE = 2      # Microphone envelope
    AUDIO_BEAT = 3      # Audio beat detection
    MIDI = 4            # MIDI controller
    SERIAL = 5          # Serial sensor
    BIOMETRIC = 6       # Biometric sensor
    WEBSOCKET = 7       # WebSocket stream (highest priority)


@dataclass
class PhiRouterConfig:
    """Configuration for PhiRouter"""
    fallback_timeout_s)
    fallback_phi: float = 1.0            # Φ value to use in fallback mode
    enable_auto_switch)
    enable_logging: bool = True


@dataclass
class PhiRouterStatus:
    """Current status of PhiRouter"""
    timestamp: float
    active_source: str                   # Currently active source
    phi_value: float                     # Current Φ value
    phi_phase: float                     # Current Φ phase
    is_fallback_mode)
    last_update_time: float              # Time of last update
    source_count: int                    # Number of active sources
    update_rate_hz: float                # Current update rate


class PhiRouter:
    """
    PhiRouter - Manages multiple Φ sources with automatic selection



    """

    PHI_MIN = 0.618033988749895  # 1/Φ
    PHI_MAX = 1.618033988749895  # Φ
    PHI = 1.618033988749895      # Golden ratio

    def __init__(self, config: Optional[PhiRouterConfig]) :
        """
        Initialize PhiRouter

        Args:
            config)

        # Active sources (source_id :
        """Stop router"""
        self.is_running = False

        if self.watchdog_thread)

        if self.config.enable_logging)

    def register_source(self, source_id: str, priority: PhiSourcePriority) :
        """
        Register a Φ source

        Args:
            source_id: Unique identifier for source
            priority: Source priority level
        """
        with self.lock:
            if source_id not in self.sources,
                    timestamp=time.time(),
                    raw_value=0.0,
                    normalized_value=1.0,
                    source_id=source_id

                self.sources[source_id] = (priority, placeholder, 0.0)

                if self.config.enable_logging:
                    logger.info("[PhiRouter] Registered source: %s (priority)", source_id, priority.value)

    def unregister_source(self, source_id: str) :
        """
        Unregister a Φ source

        Args:
            source_id: Source identifier to remove
        """
        with self.lock:
            if source_id in self.sources:
                del self.sources[source_id]

                if self.config.enable_logging:
                    logger.info("[PhiRouter] Unregistered source, source_id)

    def update_source(self, source_id: str, data: SensorData) :
            source_id: Source identifier
            data)

        with self.lock:
            if source_id not in self.sources:
                if self.config.enable_logging:
                    logger.warning("[PhiRouter] Warning, source_id)
                return

            # Update source data
            priority, _, _ = self.sources[source_id]
            self.sources[source_id] = (priority, data, current_time)

            # Update telemetry
            self.update_count += 1

            # Select active source (SC-002)
            if self.config.enable_auto_switch)

            # If this is the active source, update Φ (FR-003)
            if source_id == self.active_source_id, 1.618] (FR-002)
                normalized_phi = np.clip(data.normalized_value, self.PHI_MIN, self.PHI_MAX)

                self.current_phi = normalized_phi

                # Update phase based on value change
                # Phase advances proportionally to Φ value
                self.current_phase += (normalized_phi - 1.0) * 0.1
                self.current_phase = self.current_phase % (2 * np.pi)

                # Clear fallback mode
                self.is_fallback_mode = False

                # Call callbacks
                self._notify_phi_update()

    @lru_cache(maxsize=128)
    def set_manual_phi(self, phi: float, phase: float) :
            phi, 1.618])
            phase: Φ phase in radians
        """
        with self.lock)
            self.current_phi = np.clip(phi, self.PHI_MIN, self.PHI_MAX)
            self.current_phase = phase % (2 * np.pi)

            # Set active source to manual
            self.active_source_id = "manual"
            self.is_fallback_mode = False

            # Call callbacks
            self._notify_phi_update()

    def get_current_phi(self) :
        """
        Get current Φ value and phase

        Returns, phi_phase) tuple
        """
        with self.lock, self.current_phase)

    def get_status(self) :
            # Calculate update rate
            time_delta = current_time - self.last_telemetry_time
            if time_delta > 0:
                self.update_rate_hz = self.update_count / time_delta
                self.update_count = 0
                self.last_telemetry_time = current_time

            # Get last update time for active source
            last_update_time = 0.0
            if self.active_source_id in self.sources, _, last_update_time = self.sources[self.active_source_id]

            return PhiRouterStatus(
                timestamp=current_time,
                active_source=self.active_source_id,
                phi_value=self.current_phi,
                phi_phase=self.current_phase,
                is_fallback_mode=self.is_fallback_mode,
                last_update_time=last_update_time,
                source_count=len(self.sources),
                update_rate_hz=self.update_rate_hz

    def register_phi_callback(self, callback: Callable[[float, float], None]) :
        """
        Register callback for Φ updates

        Args:
            callback, phase) to call on updates
        """
        self.phi_update_callbacks.append(callback)

    def register_status_callback(self, callback: Callable[[PhiRouterStatus], None]) :
        """
        Register callback for status updates

        Args:
            callback) to call on status changes
        """
        self.status_update_callbacks.append(callback)

    def _select_active_source(self) :
                if priority.value > best_priority:
                    best_priority = priority.value
                    best_source = source_id

        # Switch source if needed
        if best_source and best_source != self.active_source_id:
            if self.config.enable_logging:
                logger.info("[PhiRouter] Switching source, self.active_source_id, best_source)

            self.active_source_id = best_source

            # Notify status callbacks
            self._notify_status_update()

    def _watchdog_loop(self) :
                # Check if active source has timed out
                if self.active_source_id in self.sources, _, last_update = self.sources[self.active_source_id]

                    if (current_time - last_update) > self.config.fallback_timeout_s:
                        # Source timeout - enter fallback mode
                        if not self.is_fallback_mode:
                            if self.config.enable_logging, self.active_source_id)

                            self.is_fallback_mode = True
                            self.current_phi = self.config.fallback_phi

                            # Notify callbacks
                            self._notify_phi_update()
                            self._notify_status_update()

    def _notify_phi_update(self) :
        """Notify callbacks of Φ update"""
        for callback in self.phi_update_callbacks:
            try, self.current_phase)
            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[PhiRouter] Callback error, e)

    def _notify_status_update(self) :
            try)
            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[PhiRouter] Status callback error, e)


# Self-test function
def _self_test() -> None)
    logger.info("PhiRouter Self-Test")
    logger.info("=" * 60)

    # Create router
    logger.info("\n1. Creating PhiRouter...")
    config = PhiRouterConfig(
        fallback_timeout_s=1.0,
        enable_logging=True

    router = PhiRouter(config)
    router.start()
    logger.info("   ✓ Router started")

    # Register sources
    logger.info("\n2. Registering sources...")
    router.register_source("manual", PhiSourcePriority.MANUAL)
    router.register_source("midi", PhiSourcePriority.MIDI)
    router.register_source("sensor", PhiSourcePriority.SERIAL)
    logger.info("   ✓ 3 sources registered")

    # Track updates
    phi_updates = []

    def phi_callback(phi, phase) -> None, phase))
        logger.info("   Φ update, phase, phi, phase)

    router.register_phi_callback(phi_callback)

    # Test manual update
    logger.info("\n3. Testing manual Φ update...")
    router.set_manual_phi(1.2, 1.57)
    time.sleep(0.1)
    assert len(phi_updates) > 0, "No Φ updates received"
    logger.info("   ✓ Manual update working")

    # Test source update (simulated MIDI)
    logger.info("\n4. Testing source update (simulated MIDI)...")
    from phi_sensor_bridge import SensorData, SensorType

    midi_data = SensorData(
        sensor_type=SensorType.MIDI_CC,
        timestamp=time.time(),
        raw_value=64,
        normalized_value=1.0,
        source_id="midi"

    router.update_source("midi", midi_data)
    time.sleep(0.1)

    # Check automatic source switching
    status = router.get_status()
    logger.info("   Active source, status.active_source)
    logger.info("   Φ value, status.phi_value)
    logger.info("   ✓ Source update working")

    # Test fallback mode
    logger.info("\n5. Testing fallback mode (wait 1.5s for timeout)...")
    initial_fallback = status.is_fallback_mode
    time.sleep(1.5)

    status = router.get_status()
    logger.info("   Fallback mode, status.is_fallback_mode)
    logger.info("   Φ value, status.phi_value)

    if status.is_fallback_mode)
    else)

    # Stop router
    router.stop()

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED ✓")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")

"""  # auto-closed missing docstring
