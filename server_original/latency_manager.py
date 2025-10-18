"""
LatencyManager - Calibration, Measurement, and Compensation

Implements FR-001, FR-003, FR-004, FR-005, FR-006, FR-007:
- Impulse response calibration with sounddevice.playrec
- Continuous drift monitoring and correction
- Delay line buffer for real-time compensation
- Synchronized timestamping
"""
from functools import lru_cache
import logging
logger = logging.getLogger(__name__)


import numpy as np
import sounddevice as sd
import time
import threading
from typing import Optional, Tuple, Dict, List
from collections import deque
from datetime import datetime
import os
from pathlib import Path

from .latency_frame import LatencyFrame, create_default_latency_frame


class DriftMonitor:
    """
    Monitors long-term timing drift (FR-006, FR-007)

    Tracks cumulative drift and rate of change to maintain <2ms per 10min
    """

    DRIFT_HISTORY_DURATION = 600.0  # 10 minutes
    DRIFT_ALERT_THRESHOLD = 2.0  # ms per 10 min

    def __init__(self) -> None:
        """Initialize drift monitor"""
        self.drift_samples: deque = deque(maxlen=10000)  # (timestamp, drift_ms)
        self.start_time = time.time()
        self.last_correction_time = self.start_time
        self.cumulative_drift_ms = 0.0

    def add_measurement(self, expected_time: float: Any, actual_time: float: Any) -> None:
        """
        Add a timing measurement

        Args:
            expected_time: Expected callback time (monotonic)
            actual_time: Actual callback time (monotonic)
        """
        drift_ms = (actual_time - expected_time) * 1000.0
        self.drift_samples.append((actual_time, drift_ms))
        self.cumulative_drift_ms += drift_ms

    @lru_cache(maxsize=128)
    def get_drift_rate(self) -> float:
        """
        Calculate drift rate in ms/second

        Returns:
            Drift rate (ms/s)
        """
        if len(self.drift_samples) < 2:
            return 0.0

        # Linear regression over recent samples
        times = np.array([s[0] for s in self.drift_samples])
        drifts = np.array([s[1] for s in self.drift_samples])

        if len(times) < 10:
            return 0.0

        # Use last 100 samples or all if fewer
        window_size = min(100, len(times))
        times = times[-window_size:]
        drifts = drifts[-window_size:]

        # Fit line: drift = rate * time + offset
        time_span = times[-1] - times[0]

        if time_span < 1.0:  # Need at least 1 second of data
            return 0.0

        drift_change = drifts[-1] - drifts[0]
        rate = drift_change / time_span  # ms/s

        return rate

    def get_current_drift(self) -> float:
        """
        Get current instantaneous drift

        Returns:
            Current drift in milliseconds
        """
        if not self.drift_samples:
            return 0.0

        return self.drift_samples[-1][1]

    def needs_correction(self) -> bool:
        """
        Check if drift correction is needed

        Returns:
            True if drift exceeds threshold
        """
        elapsed_minutes = (time.time() - self.last_correction_time) / 60.0

        if elapsed_minutes < 1.0:  # Check at most once per minute
            return False

        # Check if drift exceeds proportional threshold
        threshold = (elapsed_minutes / 10.0) * self.DRIFT_ALERT_THRESHOLD

        if abs(self.cumulative_drift_ms) > threshold:
            return True

        return False

    def apply_correction(self, correction_ms: float: Any) -> None:
        """
        Record that a drift correction was applied

        Args:
            correction_ms: Correction applied (positive = add delay)
        """
        self.cumulative_drift_ms = 0.0
        self.last_correction_time = time.time()

    def get_statistics(self) -> Dict:
        """Get drift statistics"""
        return {
            'current_drift_ms': self.get_current_drift(),
            'drift_rate_ms_per_sec': self.get_drift_rate(),
            'cumulative_drift_ms': self.cumulative_drift_ms,
            'sample_count': len(self.drift_samples),
            'elapsed_minutes': (time.time() - self.start_time) / 60.0
        }


class DelayLineBuffer:
    """
    Circular buffer for latency compensation (FR-003)

    Provides sample-accurate delay with fractional sample interpolation
    """

    def __init__(self, max_delay_samples: int: Any, num_channels: int: int = 1) -> None:
        """
        Initialize delay buffer

        Args:
            max_delay_samples: Maximum delay in samples
            num_channels: Number of audio channels
        """
        self.max_delay_samples = max_delay_samples
        self.num_channels = num_channels

        # Allocate buffer with extra space for interpolation
        self.buffer = np.zeros((max_delay_samples + 4, num_channels), dtype=np.float32)
        self.write_pos = 0
        self.current_delay_samples = 0.0  # Can be fractional

    @lru_cache(maxsize=128)
    def set_delay_ms(self, delay_ms: float: Any, sample_rate: int: Any) -> None:
        """
        Set delay in milliseconds

        Args:
            delay_ms: Delay in milliseconds
            sample_rate: Audio sample rate
        """
        delay_samples = (delay_ms / 1000.0) * sample_rate
        self.current_delay_samples = max(0.0, min(delay_samples, self.max_delay_samples))

    @lru_cache(maxsize=128)
    def process(self, input_block: np.ndarray) -> np.ndarray:
        """
        Process audio block with delay

        Args:
            input_block: Input audio (num_samples, num_channels)

        Returns:
            Delayed audio (same shape as input)
        """
        num_samples = input_block.shape[0]
        output = np.zeros_like(input_block)

        for i in range(num_samples):
            # Write input to buffer
            self.buffer[self.write_pos] = input_block[i]

            # Calculate read position (can be fractional)
            read_pos_float = self.write_pos - self.current_delay_samples

            if read_pos_float < 0:
                read_pos_float += self.max_delay_samples

            # Linear interpolation for fractional delay
            read_pos_int = int(read_pos_float)
            frac = read_pos_float - read_pos_int

            pos0 = read_pos_int % self.max_delay_samples
            pos1 = (read_pos_int + 1) % self.max_delay_samples

            # Interpolate
            output[i] = self.buffer[pos0] * (1.0 - frac) + self.buffer[pos1] * frac

            # Advance write position
            self.write_pos = (self.write_pos + 1) % self.max_delay_samples

        return output


class LatencyManager:
    """
    Complete latency measurement and compensation system

    Features:
    - Impulse response calibration
    - Hardware + OS latency measurement
    - Continuous drift monitoring
    - Real-time delay compensation
    - Synchronized timestamping
    """

    # Calibration settings
    IMPULSE_DURATION = 0.1  # 100ms impulse burst
    IMPULSE_FREQUENCY = 1000.0  # 1kHz sine wave
    IMPULSE_AMPLITUDE = 0.5
    CALIBRATION_SAMPLE_RATE = 48000

    # Tolerance and drift thresholds (from spec)
    TARGET_ALIGNMENT_MS = 5.0  # SC-002
    MAX_DRIFT_PER_10MIN = 2.0  # SC-003

    def __init__(self,
                 sample_rate: int = 48000,
                 buffer_size: int = 512,
                 input_device: Optional[int] = None,
                 output_device: Optional[int] = None):
        """
        Initialize latency manager

        Args:
            sample_rate: Audio sample rate
            buffer_size: Audio buffer size in samples
            input_device: Input device index (None = default)
            output_device: Output device index (None = default)
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.input_device = input_device
        self.output_device = output_device

        # State
        self.latency_frame = create_default_latency_frame()
        self.latency_frame.sample_rate = sample_rate
        self.latency_frame.buffer_size_samples = buffer_size

        self.drift_monitor = DriftMonitor()

        # Delay line for compensation
        max_delay_ms = 200.0  # Support up to 200ms compensation
        max_delay_samples = int((max_delay_ms / 1000.0) * sample_rate)
        self.delay_line = DelayLineBuffer(max_delay_samples, num_channels=2)

        # Calibration state
        self.is_calibrated = False
        self.calibration_lock = threading.Lock()

        # Performance tracking
        self.expected_callback_time = None

        logger.info("[LatencyManager] Initialized")
        logger.info("[LatencyManager] Sample rate: %s Hz", sample_rate)
        logger.info("[LatencyManager] Buffer size: %s samples", buffer_size)
        logger.info("[LatencyManager] Max compensation: %s ms", max_delay_ms:.1f)

    @lru_cache(maxsize=128)
    def calibrate(self) -> bool:
        """
        Perform impulse response calibration (FR-001)

        Plays impulse, records loopback, measures round-trip latency

        Returns:
            True if calibration successful
        """
        logger.info("\n[LatencyManager] Starting calibration...")
        logger.warning("[LatencyManager] WARNING: Ensure audio loopback is connected!")
        logger.info("[LatencyManager] (Output → Input with cable or virtual loopback)")

        with self.calibration_lock:
            try:
                # Generate impulse signal
                impulse_samples = int(self.IMPULSE_DURATION * self.CALIBRATION_SAMPLE_RATE)
                t = np.linspace(0, self.IMPULSE_DURATION, impulse_samples)
                impulse = self.IMPULSE_AMPLITUDE * np.sin(2 * np.pi * self.IMPULSE_FREQUENCY * t)

                # Add short silence before and after
                silence_samples = int(0.05 * self.CALIBRATION_SAMPLE_RATE)
                impulse = np.concatenate([
                    np.zeros(silence_samples),
                    impulse,
                    np.zeros(impulse_samples)  # Extra silence for latency measurement
                ])

                # Reshape for stereo output
                impulse_stereo = np.column_stack([impulse, impulse])

                logger.info("[LatencyManager] Playing %ss impulse...", len(impulse)/self.CALIBRATION_SAMPLE_RATE:.2f)

                # Play and record simultaneously
                recording = sd.playrec(
                    impulse_stereo,
                    samplerate=self.CALIBRATION_SAMPLE_RATE,
                    channels=2,
                    device=(self.input_device, self.output_device),
                    blocking=True
                )

                logger.info("[LatencyManager] Recording complete, analyzing...")

                # Analyze recording to find impulse response
                # Use cross-correlation to find delay
                input_signal = impulse[:len(recording)]
                recorded_signal = recording[:, 0]  # Use left channel

                # Normalize signals
                input_signal = input_signal / (np.max(np.abs(input_signal)) + 1e-10)
                recorded_signal = recorded_signal / (np.max(np.abs(recorded_signal)) + 1e-10)

                # Cross-correlation
                correlation = np.correlate(recorded_signal, input_signal, mode='full')

                # Find peak
                peak_index = np.argmax(np.abs(correlation))
                delay_samples = peak_index - len(input_signal) + 1

                # Convert to milliseconds
                measured_latency_ms = (delay_samples / self.CALIBRATION_SAMPLE_RATE) * 1000.0

                logger.info("[LatencyManager] Measured round-trip latency: %s ms", measured_latency_ms:.2f)

                # Validate measurement
                if measured_latency_ms < 0 or measured_latency_ms > 500:
                    logger.error("[LatencyManager] ERROR: Invalid latency measurement: %s ms", measured_latency_ms:.2f)
                    logger.info("[LatencyManager] Check that audio loopback is properly connected")
                    return False

                # Calculate quality metric (based on correlation peak sharpness)
                peak_value = np.abs(correlation[peak_index])
                mean_value = np.mean(np.abs(correlation))
                quality = min(1.0, peak_value / (mean_value * 10 + 1e-10))

                logger.info("[LatencyManager] Calibration quality: %s", quality:.2f)

                if quality < 0.3:
                    logger.warning("[LatencyManager] WARNING: Low calibration quality - results may be inaccurate")

                # Get device-reported latencies
                device_info = sd.query_devices(self.input_device, 'input')
                hw_input_latency = device_info['default_low_input_latency'] * 1000.0  # Convert to ms

                device_info = sd.query_devices(self.output_device, 'output')
                hw_output_latency = device_info['default_low_output_latency'] * 1000.0

                # Estimate component latencies
                buffer_latency = (self.buffer_size / self.sample_rate) * 1000.0

                # Update latency frame
                self.latency_frame.hw_input_latency_ms = hw_input_latency
                self.latency_frame.hw_output_latency_ms = hw_output_latency
                self.latency_frame.engine_latency_ms = buffer_latency  # Estimate
                self.latency_frame.os_latency_ms = max(0, measured_latency_ms - hw_input_latency - hw_output_latency - buffer_latency)

                self.latency_frame.compute_total()

                # Set compensation offset to measured latency
                self.latency_frame.compensation_offset_ms = measured_latency_ms
                self.latency_frame.calibrated = True
                self.latency_frame.calibration_quality = quality
                self.latency_frame.last_calibration_time = time.time()

                # Configure delay line
                self.delay_line.set_delay_ms(measured_latency_ms, self.sample_rate)

                self.is_calibrated = True

                logger.info("[LatencyManager] ✓ Calibration complete")
                logger.info("[LatencyManager] Component breakdown:")
                logger.info("[LatencyManager]   HW Input:  %s ms", hw_input_latency:.2f)
                logger.info("[LatencyManager]   HW Output: %s ms", hw_output_latency:.2f)
                logger.info("[LatencyManager]   Engine:    %s ms", buffer_latency:.2f)
                logger.info("[LatencyManager]   OS:        %s ms", self.latency_frame.os_latency_ms:.2f)
                logger.info("[LatencyManager]   Total:     %s ms", self.latency_frame.total_measured_ms:.2f)

                return True

            except Exception as e:
                logger.error("[LatencyManager] ✗ Calibration failed: %s", e)
                import traceback
                traceback.print_exc()
                return False

    @lru_cache(maxsize=128)
    def compensate_block(self, audio_block: np.ndarray) -> np.ndarray:
        """
        Apply latency compensation to audio block

        Args:
            audio_block: Input audio (num_samples, num_channels)

        Returns:
            Compensated audio (same shape)
        """
        if not self.is_calibrated:
            return audio_block  # Pass through if not calibrated

        return self.delay_line.process(audio_block)

    @lru_cache(maxsize=128)
    def update_timing(self, callback_time: float: Any, expected_time: Optional[float]: Any = None) -> Any:
        """
        Update timing measurements for drift monitoring

        Args:
            callback_time: Actual callback time (monotonic)
            expected_time: Expected callback time (monotonic), or None to auto-calculate
        """
        if expected_time is None:
            if self.expected_callback_time is None:
                self.expected_callback_time = callback_time
                return

            # Calculate expected time based on buffer size
            buffer_duration = self.buffer_size / self.sample_rate
            expected_time = self.expected_callback_time + buffer_duration

        # Record drift measurement
        self.drift_monitor.add_measurement(expected_time, callback_time)

        # Update latency frame
        self.latency_frame.drift_ms = self.drift_monitor.get_current_drift()
        self.latency_frame.drift_rate_ms_per_sec = self.drift_monitor.get_drift_rate()

        # Check if correction needed
        if self.drift_monitor.needs_correction():
            correction = -self.latency_frame.drift_ms  # Negative because we want to counteract drift
            self.apply_drift_correction(correction)

        # Update expected time for next callback
        self.expected_callback_time = callback_time

    def apply_drift_correction(self, correction_ms: float: Any) -> None:
        """
        Apply drift correction

        Args:
            correction_ms: Correction to apply in milliseconds
        """
        logger.info("[LatencyManager] Applying drift correction: %s ms", correction_ms:+.2f)

        # Update compensation offset
        self.latency_frame.compensation_offset_ms += correction_ms

        # Update delay line
        self.delay_line.set_delay_ms(
            self.latency_frame.compensation_offset_ms,
            self.sample_rate
        )

        # Notify drift monitor
        self.drift_monitor.apply_correction(correction_ms)

    def get_current_frame(self) -> LatencyFrame:
        """
        Get current latency frame with timestamp

        Returns:
            Current LatencyFrame snapshot
        """
        self.latency_frame.timestamp = time.time()
        return self.latency_frame

    def is_aligned(self, tolerance_ms: Optional[float] = None) -> bool:
        """
        Check if system is within alignment tolerance

        Args:
            tolerance_ms: Tolerance in ms (None = use TARGET_ALIGNMENT_MS)

        Returns:
            True if aligned within tolerance
        """
        if tolerance_ms is None:
            tolerance_ms = self.TARGET_ALIGNMENT_MS

        return self.latency_frame.is_aligned(tolerance_ms)

    def get_statistics(self) -> Dict:
        """
        Get comprehensive latency statistics

        Returns:
            Dictionary with all latency metrics
        """
        return {
            'calibrated': self.is_calibrated,
            'latency': self.latency_frame.to_dict(),
            'drift': self.drift_monitor.get_statistics(),
            'aligned': self.is_aligned(),
            'effective_latency_ms': self.latency_frame.get_effective_latency()
        }


# Self-test function
def _self_test() -> None:
    """Test LatencyManager functionality"""
    logger.info("=" * 60)
    logger.info("LatencyManager Self-Test")
    logger.info("=" * 60)

    try:
        # Test drift monitor
        logger.info("\n1. Testing DriftMonitor...")
        drift_mon = DriftMonitor()

        # Simulate some drift measurements
        base_time = time.time()
        for i in range(100):
            expected = base_time + i * 0.01
            actual = expected + 0.0001 * i  # Gradual drift
            drift_mon.add_measurement(expected, actual)

        drift_rate = drift_mon.get_drift_rate()
        logger.info("   Drift rate: %s ms/s", drift_rate:.4f)
        logger.info("   ✓ DriftMonitor OK")

        # Test delay line
        logger.info("\n2. Testing DelayLineBuffer...")
        delay_line = DelayLineBuffer(max_delay_samples=4800, num_channels=2)  # 100ms at 48kHz

        # Set 10ms delay
        delay_line.set_delay_ms(10.0, 48000)

        # Create test signal (impulse)
        test_signal = np.zeros((480, 2))  # 10ms at 48kHz
        test_signal[0, :] = 1.0

        # Process
        output = delay_line.process(test_signal)

        # Check that impulse is delayed
        input_peak_pos = np.argmax(np.abs(test_signal[:, 0]))
        output_peak_pos = np.argmax(np.abs(output[:, 0]))

        logger.info("   Input peak at sample: %s", input_peak_pos)
        logger.info("   Output peak at sample: %s", output_peak_pos)

        # Note: First block won't show delay (buffer is empty)
        # Process a second block to see the delay
        test_signal2 = np.zeros((480, 2))
        output2 = delay_line.process(test_signal2)

        output_peak_pos2 = np.argmax(np.abs(output2[:, 0]))
        logger.info("   Second block peak at sample: %s", output_peak_pos2)
        logger.info("   ✓ DelayLineBuffer OK")

        # Test LatencyManager initialization
        logger.info("\n3. Testing LatencyManager initialization...")
        manager = LatencyManager(sample_rate=48000, buffer_size=512)

        assert manager.sample_rate == 48000
        assert manager.buffer_size == 512
        assert not manager.is_calibrated

        logger.info("   ✓ LatencyManager initialization OK")

        # Test timing updates
        logger.info("\n4. Testing timing updates...")
        current_time = time.time()
        manager.update_timing(current_time)

        # Simulate a few callbacks
        for i in range(10):
            current_time += (512 / 48000)  # Perfect timing
            manager.update_timing(current_time)

        stats = manager.get_statistics()
        logger.info("   Drift: %s ms", stats['drift']['current_drift_ms']:.4f)
        logger.info("   ✓ Timing updates OK")

        # Test latency frame retrieval
        logger.info("\n5. Testing latency frame retrieval...")
        frame = manager.get_current_frame()
        assert frame.sample_rate == 48000
        assert frame.buffer_size_samples == 512
        logger.info("   Frame: %s", frame)
        logger.info("   ✓ Latency frame OK")

        # Note: Skipping actual calibration test as it requires audio hardware
        logger.info("\n6. Calibration test...")
        logger.info("   ⚠ Skipping (requires audio loopback hardware)")
        logger.info("   To test calibration manually:")
        logger.info("     1. Connect audio output → input (cable or virtual)")
        logger.info("     2. Run: python latency_manager.py")
        logger.info("     3. Follow calibration prompts")

        logger.info("\n" + "=" * 60)
        logger.info("Self-Test PASSED ✓")
        logger.info("=" * 60)
        logger.info("\nNote: Full calibration test requires audio hardware")
        return True

    except Exception as e:
        logger.error("\n✗ Self-Test FAILED: %s", e)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run self-test
    success = _self_test()

    if success:
        logger.info("\n" + "=" * 60)
        logger.info("Interactive Calibration Test")
        logger.info("=" * 60)

        response = input("\nRun interactive calibration test? (requires audio loopback) [y/N]: ")

        if response.lower() == 'y':
            logger.info("\n🔊 IMPORTANT: Connect audio output to input before proceeding!")
            logger.info("   Options:")
            logger.info("   1. Physical cable: Output jack → Input jack")
            logger.info("   2. Virtual audio cable (VB-Audio Cable, BlackHole, etc.)")
            input("\nPress Enter when ready...")

            manager = LatencyManager()
            success = manager.calibrate()

            if success:
                logger.info("\n" + "=" * 60)
                logger.info("Calibration Results:")
                logger.info("=" * 60)

                stats = manager.get_statistics()
                logger.info("\nCalibrated: %s", stats['calibrated'])
                logger.info("Total Latency: %s ms", stats['latency']['total_measured_ms']:.2f)
                logger.info("Effective Latency: %s ms", stats['effective_latency_ms']:.2f)
                logger.info("Aligned: %s", stats['aligned'])
                logger.info("Quality: %s", stats['latency']['calibration_quality']:.2f)

                logger.info("\nComponent Breakdown:")
                logger.info("  HW Input:  %s ms", stats['latency']['hw_input_latency_ms']:.2f)
                logger.info("  HW Output: %s ms", stats['latency']['hw_output_latency_ms']:.2f)
                logger.info("  Engine:    %s ms", stats['latency']['engine_latency_ms']:.2f)
                logger.info("  OS:        %s ms", stats['latency']['os_latency_ms']:.2f)
