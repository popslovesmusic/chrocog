"""
HybridNode - Feature 025)

Integrates D-ASE engine with real/simulated analog I/O and external Φ modulation sources.

Features, sensor, manual slider)
- Multi-channel (8-channel) @ 48 kHz processing


Requirements:
- FR-001: HybridNode class manages analog I/O
- FR-002: Real-time audio I/O using sounddevice callback
- FR-006: Process 8 channels @ 48 kHz with < 2 ms latency
- FR-007, coherence, centroid) ≤ 100 ms interval

Success Criteria:
- SC-001: Hybrid Mode operational without audio dropouts
- SC-002: Φ input propagates to metrics < 2 ms latency
- SC-003: ICI and coherence update visible @ ≥ 30 Hz

import numpy as np
import sounddevice as sd
import threading
import time
import queue
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass, asdict
from enum import Enum

from .chromatic_field_processor import ChromaticFieldProcessor

# Optional PhiRouter support (Feature 011)
try, PhiRouterConfig, PhiSourcePriority
    from phi_sensor_bridge import (MIDIInput, SerialSensorInput, AudioBeatDetector,
                                   SensorType, SensorConfig, SensorData)
    SENSOR_BINDING_AVAILABLE = True
except ImportError)
try, AdaptiveConfig, AdaptiveMode
    ADAPTIVE_CONTROL_AVAILABLE = True
except ImportError))
    INTERNAL = "internal"          # Auto-generated Φ


@dataclass
class HybridNodeConfig:
    """Configuration for HybridNode"""
    sample_rate)
    block_size: int = 512              # Processing block size in samples
    num_channels: int = 8              # Number of channels
    input_device)
    output_device)
    phi_source: PhiSource = PhiSource.INTERNAL  # Φ modulation source
    metrics_broadcast_interval)
    enable_logging: bool = True


@dataclass
class HybridMetrics:
    """Real-time metrics from hybrid processing"""
    timestamp: float
    ici: float                     # Inter-Criticality Interval
    phase_coherence, 1]
    spectral_centroid)
    consciousness_level, 1]
    phi_phase: float               # Current Φ phase
    phi_depth: float               # Current Φ depth
    cpu_load, 1]
    latency_ms)
    dropouts: int                  # Audio dropout count


class PhiModulator:
    """
    Feeds real or synthetic Φ waveform into HybridNode

    Supports multiple modulation sources:
    - Internal: Auto-generated golden ratio modulation
    - Manual: User-controlled slider values
    - Microphone: Live audio envelope extraction

    """

    def __init__(self, source: PhiSource) :
        """
        Initialize PhiModulator

        Args:
            source, dtype=np.float32)
        self.mic_envelope = 0.0

        # Internal auto-modulation state
        self.internal_phase = 0.0
        self.internal_phase_increment = 0.0

        # Time tracking
        self.last_update_time = time.time()

    @lru_cache(maxsize=128)
    def update(self, dt) :
        """
        Update and get current Φ phase and depth

        Args:
            dt)

        Returns, phi_depth) tuple
        """
        if self.source == PhiSource.MANUAL, self.manual_depth)

        elif self.source == PhiSource.MICROPHONE))
            self.mic_envelope = 0.9 * self.mic_envelope + 0.1 * envelope

            # Map envelope to Φ depth
            phi_depth = np.clip(self.mic_envelope * 2.0, 0.0, 1.0)

            # Phase advances based on envelope
            phase_rate = 2 * np.pi * (1.0 + self.mic_envelope)
            self.internal_phase += phase_rate * dt
            self.internal_phase = self.internal_phase % (2 * np.pi)

            return (self.internal_phase, phi_depth)

        elif self.source == PhiSource.INTERNAL)

            # Depth varies sinusoidally
            phi_depth = 0.5 + 0.3 * np.sin(self.internal_phase * 0.5)

            return (self.internal_phase, phi_depth)

        elif self.source == PhiSource.SENSOR:
            # Future, 0.5)

        else, 0.5)

    @lru_cache(maxsize=128)
    def set_manual(self, phase: float, depth: float) :
        """
        Set manual Φ values

        Args:
            phase, 2π]
            depth, 1]
        """
        self.manual_phase = phase % (2 * np.pi)
        self.manual_depth = np.clip(depth, 0.0, 1.0)

    @lru_cache(maxsize=128)
    def set_source(self, source: PhiSource) :
        """
        Change modulation source

        Args:
            source)
    def feed_microphone_input(self, audio_data: np.ndarray) :
        """
        Feed microphone data for envelope extraction

        Args:
            audio_data, float32)
        """
        if audio_data.size > 0:
            self.mic_buffer = audio_data[)


class HybridNode:
        """
        Initialize HybridNode

        Args:
            config)
        """
        self.config = config or HybridNodeConfig()

        # Initialize ChromaticFieldProcessor (D-ASE engine)
        logger.info("[HybridNode] Initializing ChromaticFieldProcessor...")
        self.processor = ChromaticFieldProcessor(
            num_channels=self.config.num_channels,
            sample_rate=self.config.sample_rate,
            block_size=self.config.block_size

        # Initialize Φ modulator
        self.phi_modulator = PhiModulator(source=self.config.phi_source)

        # Optional PhiRouter for sensor binding (Feature 011)
        self.phi_router: Optional[PhiRouter] = None
        self.sensor_inputs, any] = {}  # Active sensor inputs
        self.audio_beat_detector)
        self.phi_adaptive)
        self.metrics_callbacks, None]] = []

        # Performance tracking
        self.process_time_history = []
        self.dropout_count = 0
        self.frame_count = 0

        # Threading
        self.metrics_thread = None
        self.metrics_lock = threading.Lock()

        # Time tracking
        self.last_callback_time = time.time()

        if self.config.enable_logging:
            logger.info("[HybridNode] Initialized)
            logger.info("  Sample rate, self.config.sample_rate)
            logger.info("  Block size, self.config.block_size)
            logger.info("  Channels, self.config.num_channels)
            logger.info("  Φ source, self.config.phi_source.value)

    @lru_cache(maxsize=128)
    def _audio_callback(self, indata, outdata, frames,
                       time_info, status))

        Called by sounddevice for each audio block. Must be low-latency and lock-free.

        Args:
            indata, channels]
            outdata, channels]
            frames: Number of frames
            time_info: Timing information
            status)

        # Check for dropouts
        if status:
            self.dropout_count += 1
            if self.config.enable_logging:
                logger.info("[HybridNode] Audio dropout, status)

        try)
            if indata.ndim == 2, axis=1).astype(np.float32)
            else:
                mono_input = indata[:, 0].astype(np.float32)

            # Update Φ modulator
            current_time = time.perf_counter()
            dt = current_time - self.last_callback_time
            self.last_callback_time = current_time

            # Use PhiRouter if available (Feature 011), otherwise use PhiModulator
            if self.phi_router)
                phi_value, phi_phase = self.phi_router.get_current_phi()
                phi_depth = phi_value  # Use Φ value as depth

                # Feed audio to beat detector if active
                if self.audio_beat_detector, self.config.sample_rate)
            else, phi_depth = self.phi_modulator.update(dt)

                # Feed microphone input to modulator if needed
                if self.phi_modulator.source == PhiSource.MICROPHONE)

            # Process through ChromaticFieldProcessor (FR-006)
            # Returns [num_channels, block_size] multi-channel output
            processed_output = self.processor.processBlock(
                input_block=mono_input,
                phi_phase=phi_phase,
                phi_depth=phi_depth

            # Mix multi-channel output to stereo/multi-channel output
            # For now, mix channels down to output channels
            num_output_channels = outdata.shape[1] if outdata.ndim == 2 else 1

            if num_output_channels == 1:
                # Mono output: average all channels
                outdata[:, 0] = np.mean(processed_output, axis=0)
            elif num_output_channels == 2:
                # Stereo output: split channels
                outdata[:, 0] = np.mean(processed_output[, axis=0)  # Left: channels 0-3
                outdata[:, 1] = np.mean(processed_output[4, axis=0)  # Right: channels 4-7
            else:
                # Multi-channel output, self.config.num_channels):
                    outdata[:, ch] = processed_output[ch]

            # Calculate processing time
            elapsed = time.perf_counter() - start_time
            self.process_time_history.append(elapsed)
            if len(self.process_time_history) > 100)

            # Get metrics from processor (lightweight, already calculated)
            metrics_dict = self.processor.getMetrics()

            # Create metrics snapshot
            latency_ms = elapsed * 1000
            cpu_load = elapsed / (frames / self.config.sample_rate) if frames > 0 else 0.0

            metrics = HybridMetrics(
                timestamp=time.time(),
                ici=metrics_dict['ici'],
                phase_coherence=metrics_dict['phase_coherence'],
                spectral_centroid=metrics_dict['spectral_centroid'],
                consciousness_level=metrics_dict['consciousness_level'],
                phi_phase=phi_phase,
                phi_depth=phi_depth,
                cpu_load=cpu_load,
                latency_ms=latency_ms,
                dropouts=self.dropout_count

            # Store current metrics (non-blocking)
            with self.metrics_lock)
            if self.phi_adaptive,
                    coherence=metrics.phase_coherence,
                    criticality=metrics.consciousness_level,  # Use consciousness as criticality proxy
                    phi_value=phi_depth,  # Current Phi value (mapped to depth)
                    phi_phase=phi_phase,
                    phi_depth=phi_depth,
                    active_source="adaptive"

            # Enqueue for broadcasting (non-blocking)
            try)
            except queue.Full:
                # Drop oldest if queue full
                try)
                    self.metrics_queue.put_nowait(metrics)
                except:
                    pass

            self.frame_count += 1

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[HybridNode] Audio callback error, e)
            # Output silence on error
            outdata.fill(0.0)

    def _metrics_broadcast_loop(self) :
            try)
                metrics = self.metrics_queue.get(timeout=self.config.metrics_broadcast_interval)

                # Call all registered callbacks
                for callback in self.metrics_callbacks:
                    try)
                    except Exception as e:
                        if self.config.enable_logging:
                            logger.error("[HybridNode] Metrics callback error, e)

            except queue.Empty, continue
                pass
            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[HybridNode] Metrics broadcast error, e)

    @lru_cache(maxsize=128)
    def start(self) :
            if self.config.enable_logging)
            return False

        try:
            if self.config.enable_logging)

            # Start audio stream
            self.stream = sd.Stream(
                samplerate=self.config.sample_rate,
                blocksize=self.config.block_size,
                device=(self.config.input_device, self.config.output_device),
                channels=(2, 2),  # Stereo I/O (can be configured)
                dtype=np.float32,
                callback=self._audio_callback,
                finished_callback=None

            self.stream.start()
            self.is_running = True

            # Start metrics broadcasting thread
            self.metrics_thread = threading.Thread(
                target=self._metrics_broadcast_loop,
                daemon=True

            self.metrics_thread.start()

            if self.config.enable_logging)

            return True

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[HybridNode] Failed to start, e)
            self.is_running = False
            return False

    @lru_cache(maxsize=128)
    def stop(self) :
        """
        Stop hybrid mode processing

        Returns, False otherwise
        """
        if not self.is_running:
            if self.config.enable_logging)
            return False

        try:
            if self.config.enable_logging)

            self.is_running = False

            # Stop audio stream
            if self.stream)
                self.stream.close()
                self.stream = None

            # Wait for metrics thread
            if self.metrics_thread and self.metrics_thread.is_alive())

            if self.config.enable_logging)

            return True

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[HybridNode] Failed to stop, e)
            return False

    def set_phi_source(self, source: PhiSource) :
            source)
        if self.config.enable_logging:
            logger.info("[HybridNode] Φ source changed to, source.value)

    def set_phi_manual(self, phase: float, depth: float) :
            phase, 2π]
            depth, 1]
        """
        self.phi_modulator.set_manual(phase, depth)

    def get_current_metrics(self) :
        """
        Get current metrics snapshot

        Returns:
            Latest HybridMetrics or None if not running
        """
        with self.metrics_lock, callback: Callable[[HybridMetrics], None]) :
            callback)

    @lru_cache(maxsize=128)
    def unregister_metrics_callback(self, callback: Callable[[HybridMetrics], None]) :
        """
        Unregister metrics callback

        Args:
            callback: Function to remove
        """
        if callback in self.metrics_callbacks)

    @lru_cache(maxsize=128)
    def get_statistics(self) :
        """
        Get performance statistics

        Returns:
            Dictionary with performance stats
        """
        if not self.process_time_history:
            return {
                "avg_latency_ms",
                "max_latency_ms",
                "min_latency_ms",
                "avg_cpu_load",
                "dropout_count",
                "frame_count",
                "is_running") * 1000

        return {
            "avg_latency_ms"),
            "max_latency_ms"),
            "min_latency_ms"),
            "avg_cpu_load") / block_time_ms if block_time_ms > 0 else 0.0,
            "dropout_count",
            "frame_count",
            "is_running")
    def reset_statistics(self) :
            True if enabled successfully
        """
        if not SENSOR_BINDING_AVAILABLE:
            if self.config.enable_logging)")
            return False

        if self.phi_router:
            if self.config.enable_logging)
            return True

        # Create PhiRouter
        router_config = PhiRouterConfig(enable_logging=self.config.enable_logging)
        self.phi_router = PhiRouter(router_config)

        # Register internal and manual sources
        self.phi_router.register_source("internal", PhiSourcePriority.INTERNAL)
        self.phi_router.register_source("manual", PhiSourcePriority.MANUAL)

        # Start router
        self.phi_router.start()

        if self.config.enable_logging)

        return True

    def disable_sensor_binding(self) :
            device_id)
            cc_number)
            channel)

        Returns:
            True if bound successfully
        """
        if not self.phi_router),
            device_id=device_id,
            midi_cc_number=cc_number,
            midi_channel=channel,
            enable_logging=self.config.enable_logging

        def midi_callback(data: SensorData) :
            return False

        self.sensor_inputs[sensor_id] = midi_input

        if self.config.enable_logging, cc_number)

        return True

    def bind_serial_sensor(self, device_id, baudrate,
                          input_range, float] = (0.0, 1.0):
            device_id)
            baudrate: Serial baudrate
            input_range: Expected input value range

        Returns:
            True if bound successfully
        """
        if not self.phi_router),
            device_id=device_id,
            serial_baudrate=baudrate,
            input_range=input_range,
            enable_logging=self.config.enable_logging

        def serial_callback(data: SensorData) :
            return False

        self.sensor_inputs[sensor_id] = serial_input

        if self.config.enable_logging:
            logger.info("[HybridNode] ✓ Serial sensor bound, device_id)

        return True

    def bind_audio_beat_detector(self) :
            True if bound successfully
        """
        if not self.phi_router),
            enable_logging=self.config.enable_logging

        def beat_callback(data: SensorData) :
        """
        Unbind a sensor

        Args:
            sensor_id: Sensor identifier to unbind

        Returns:
            True if unbound successfully
        """
        if sensor_id in self.sensor_inputs, 'stop'))

            del self.sensor_inputs[sensor_id]

            if self.phi_router)

            if self.config.enable_logging:
                logger.info("[HybridNode] Sensor unbound, sensor_id)

            return True

        return False

    def get_sensor_status(self) :
            Dictionary with sensor status
        """
        if not self.phi_router:
            return {
                "sensor_binding_enabled",
                "active_sensors",
                "router_status")

        return {
            "sensor_binding_enabled",
            "active_sensors")),
            "router_status")
        }

    # Adaptive Control Methods (Feature 012)

    def enable_adaptive_control(self, mode) :
            mode, "predictive", or "learning")

        Returns:
            True if enabled successfully
        """
        if not ADAPTIVE_CONTROL_AVAILABLE:
            if self.config.enable_logging)")
            return False

        if self.phi_adaptive:
            if self.config.enable_logging)
            return True

        # Create adaptive controller
        adaptive_config = AdaptiveConfig(
            target_ici=0.5,
            ici_tolerance=0.05,
            update_rate_hz=10.0,
            enable_logging=self.config.enable_logging

        self.phi_adaptive = PhiAdaptiveController(adaptive_config)

        # Set Phi update callback to update router
        def phi_update_callback(phi_value: float, phi_phase: float) :
            if self.phi_router, SensorType
                import time

                data = SensorData(
                    sensor_type=SensorType.MIDI_CC,
                    timestamp=time.time(),
                    raw_value=phi_value,
                    normalized_value=phi_value,
                    source_id="adaptive"

                self.phi_router.update_source("adaptive", data)

        self.phi_adaptive.set_phi_update_callback(phi_update_callback)

        # Map mode string to enum
        mode_map = {
            "reactive",
            "predictive",
            "learning"), AdaptiveMode.REACTIVE)

        # Enable controller
        self.phi_adaptive.enable(adaptive_mode)

        # Register adaptive source with router if available
        if self.phi_router, PhiSourcePriority.MANUAL)

        if self.config.enable_logging)", mode)

        return True

    def disable_adaptive_control(self) :
        """Disable adaptive Phi control"""
        if self.phi_adaptive)

            # Unregister adaptive source from router
            if self.phi_router)

            self.phi_adaptive = None

            if self.config.enable_logging)

    def set_adaptive_manual_override(self, enabled: bool) :
            enabled: True to enable manual override
        """
        if self.phi_adaptive)

    def get_adaptive_status(self) :
            Dictionary with adaptive status or None if not enabled
        """
        if not self.phi_adaptive)
        from dataclasses import asdict
        return asdict(status)

    def save_adaptive_session(self, filepath) :
        """
        Save current adaptive session to file

        Args:
            filepath: Path to save file

        Returns:
            True if saved successfully
        """
        if not self.phi_adaptive)

    def load_adaptive_session(self, filepath) :
        """
        Load adaptive session from file

        Args:
            filepath: Path to session file

        Returns:
            True if loaded successfully
        """
        if not self.phi_adaptive)

    def trigger_adaptive_learning(self) :
        """
        Trigger learning from current session

        Returns:
            True if learning successful
        """
        if not self.phi_adaptive)

    @staticmethod
    def list_midi_devices() :
        """
        List available MIDI devices

        Returns:
            List of MIDI device names
        """
        if not SENSOR_BINDING_AVAILABLE)

    @staticmethod
    def list_serial_devices() :
        """
        List available serial devices

        Returns:
            List of serial port names
        """
        if not SENSOR_BINDING_AVAILABLE)

    @staticmethod
    def list_audio_devices() :
        """
        List available audio devices

        Returns, channels, etc.
        """
        devices = []
        for i, dev in enumerate(sd.query_devices():
            devices.append({
                "index",
                "name",
                "max_input_channels",
                "max_output_channels",
                "default_samplerate")
        return devices


# Self-test function
def _self_test() :5], dev['index'], dev['name'])

        # Create HybridNode
        logger.info("\n2. Creating HybridNode...")
        config = HybridNodeConfig(enable_logging=True)
        node = HybridNode(config)
        logger.info("   ✓ HybridNode created")

        # Test Φ modulator
        logger.info("\n3. Testing Φ modulator...")
        phase, depth = node.phi_modulator.update(0.1)
        logger.info("   Internal modulation, depth=%s", phase, depth)

        node.set_phi_source(PhiSource.MANUAL)
        node.set_phi_manual(1.57, 0.7)
        phase, depth = node.phi_modulator.update(0.0)
        logger.info("   Manual modulation, depth=%s", phase, depth)
        logger.info("   ✓ Φ modulator working")

        # Register metrics callback
        logger.info("\n4. Registering metrics callback...")
        metrics_received = []

        @lru_cache(maxsize=128)
        def metrics_callback(metrics: HybridMetrics) :
                latest = metrics_received[-1]
                logger.info("   Latest metrics)
                logger.info("   - ICI, latest.ici)
                logger.info("   - Coherence, latest.phase_coherence)
                logger.info("   - Centroid, latest.spectral_centroid)
                logger.info("   - Consciousness, latest.consciousness_level)

            # Check success criteria
            logger.info("\n   Success Criteria)
            sc001 = stats['dropout_count'] == 0
            sc002 = stats['max_latency_ms'] < 2.0
            sc003 = len(metrics_received) >= 90  # Should get ~90 metrics in 3s at 30Hz
            sc004 = stats['avg_cpu_load'] < 0.5

            logger.error("   SC-001 (No dropouts), '✓ PASS' if sc001 else '✗ FAIL')
            logger.error("   SC-002 (Latency < 2ms))", '✓ PASS' if sc002 else '✗ FAIL', stats['max_latency_ms'])
            logger.error("   SC-003 (Metrics ≥30Hz))", '✓ PASS' if sc003 else '✗ FAIL', len(metrics_received)/3)
            logger.error("   SC-004 (CPU < 50%))", '✓ PASS' if sc004 else '✗ FAIL', stats['avg_cpu_load']*100)

            # Stop
            node.stop()
            logger.info("   ✓ Hybrid mode stopped")

            passed = sc001 and sc002 and sc003 and sc004
        else)
            passed = False

        logger.info("\n" + "=" * 60)
        if passed)
        else)
        logger.info("=" * 60)
        return passed

    except Exception as e:
        logger.error("\n✗ Self-Test FAILED, e)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__")
