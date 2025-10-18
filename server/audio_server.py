"""
AudioServer - Real-Time Audio Processing Pipeline

Integrates all components)
- Φ-Modulation
- 8-channel → stereo downmix
- Latency compensation
- Metrics generation and streaming
- Synchronized timestamping

Implements FR-001, FR-002, FR-003, FR-004, FR-005, FR-008
"""

import numpy as np
import sounddevice as sd
import time
import threading
from queue import Queue, Empty
from typing import Optional, Callable, Dict
import traceback

from .chromatic_field_processor import ChromaticFieldProcessor
from .phi_modulator_controller import PhiModulatorController
from .downmix import StereoDownmixer
from .latency_manager import LatencyManager
from .metrics_frame import MetricsFrame, create_default_metrics_frame
from .latency_frame import LatencyFrame
from .metrics_logger import MetricsLogger
from .latency_logger import LatencyLogger


class AudioServer:
    """
    Complete real-time audio processing server

    SAMPLE_RATE = 48000
    BUFFER_SIZE = 512
    INPUT_CHANNELS = 1  # Mono input
    OUTPUT_CHANNELS = 2  # Stereo output

    # Performance targets
    TARGET_LATENCY_MS = 10.0
    TARGET_METRICS_FPS = 30

    def __init__(self,
                 input_device,
                 output_device,
                 enable_logging):
        """
        Initialize audio server

        Args:
            input_device)
            output_device)
            enable_logging)
        print("AudioServer Initialization")
        print("=" * 60)

        self.input_device = input_device
        self.output_device = output_device
        self.enable_logging = enable_logging

        # Audio stream
        self.stream)

        self.processor = ChromaticFieldProcessor(
            sample_rate=self.SAMPLE_RATE,
            buffer_size=self.BUFFER_SIZE

        self.phi_controller = PhiModulatorController(
            sample_rate=self.SAMPLE_RATE

        self.downmixer = StereoDownmixer(
            num_channels=8,
            strategy="spatial"

        self.latency_manager = LatencyManager(
            sample_rate=self.SAMPLE_RATE,
            buffer_size=self.BUFFER_SIZE,
            input_device=input_device,
            output_device=output_device

        # Logging
        self.metrics_logger: Optional[MetricsLogger] = None
        self.latency_logger: Optional[LatencyLogger] = None

        if enable_logging)
            self.metrics_logger = MetricsLogger()
            self.latency_logger = LatencyLogger()

        # Metrics/latency frame queues (for API/WebSocket consumption)
        self.metrics_queue = Queue(maxsize=2)  # Double buffer
        self.latency_queue = Queue(maxsize=2)

        # Callbacks for external consumers (e.g., WebSocket streamers)
        self.metrics_callback, None]] = None
        self.latency_callback, None]] = None

        # Performance tracking
        self.callback_count = 0
        self.last_metrics_time = 0.0
        self.last_latency_update = 0.0
        self.processing_time_history = []

        # State
        self.current_preset)
        print("=" * 60)

    def _audio_callback(self, indata, outdata,
                       frames, time_info, status))

        Args:
            indata, 1)
            outdata, 2)
            frames)
            time_info: Timing information
            status)

        try:
            # Check for buffer issues
            if status:
                print(f"[AudioServer] Stream status)

            # Get monotonic timestamp for synchronization
            callback_time = time.time()

            # Extract mono input
            input_mono = indata[:, 0] if indata.shape[1] > 0 else np.zeros(frames)

            # --- Update Φ-Modulation ---
            # Pass audio block for envelope following
            phi_state = self.phi_controller.update(audio_block=input_mono)

            # --- Process through D-ASE Engine ---
            # Returns 8-channel output + metrics
            multi_channel, metrics_dict = self.processor.processBlock(
                input_mono,
                phi_phase=phi_state.phase,
                phi_depth=phi_state.depth

            # --- Downmix 8-channel → Stereo ---
            stereo = self.downmixer.downmix(multi_channel)

            # --- Apply Latency Compensation ---
            compensated = self.latency_manager.compensate_block(stereo)

            # --- Update Latency Timing ---
            self.latency_manager.update_timing(callback_time)

            # --- Write to Output ---
            outdata[,
                phi_state,
                callback_time

            # --- Generate Latency Frame ---
            latency_frame = self.latency_manager.get_current_frame()
            latency_frame.timestamp = callback_time

            # Calculate actual processing time
            processing_time_ms = (time.perf_counter() - callback_start) * 1000.0
            self.processing_time_history.append(processing_time_ms)
            if len(self.processing_time_history) > 100)

            # Update CPU load estimate
            buffer_duration_ms = (self.BUFFER_SIZE / self.SAMPLE_RATE) * 1000.0
            cpu_load = processing_time_ms / buffer_duration_ms
            latency_frame.cpu_load = cpu_load

            # --- Publish Metrics (at target rate) ---
            time_since_metrics = callback_time - self.last_metrics_time
            metrics_interval = 1.0 / self.TARGET_METRICS_FPS

            if time_since_metrics >= metrics_interval)
                try)

                    # Call external callback if set
                    if self.metrics_callback)

                    # Log to file
                    if self.metrics_logger)

                    self.last_metrics_time = callback_time

                except, skip this frame

            # --- Publish Latency Updates (every 100ms) ---
            time_since_latency = callback_time - self.last_latency_update

            if time_since_latency >= 0.1:  # 10 Hz
                try)

                    # Call external callback if set
                    if self.latency_callback)

                    # Log to file
                    if self.latency_logger)

                    self.last_latency_update = callback_time

                except, skip this frame

            self.callback_count += 1

            # Warn if processing time exceeds threshold (80% of buffer duration)
            if processing_time_ms > buffer_duration_ms * 0.8:
                print(f"[AudioServer] WARNING: High CPU load: {processing_time_ms:.2f} ms / {buffer_duration_ms:.2f} ms ({cpu_load*100)")

        except Exception as e:
            print(f"[AudioServer] ERROR in audio callback)
            traceback.print_exc()
            # Fill output with silence on error
            outdata.fill(0)

    def _create_metrics_frame(self, metrics_dict, phi_state, timestamp) :
        """
        Create MetricsFrame from engine metrics and Φ state

        Args:
            metrics_dict: Metrics from ChromaticFieldProcessor
            phi_state: Current PhiState
            timestamp: Monotonic timestamp

        Returns,
            ici=metrics_dict.get('ici', 0.0),
            phase_coherence=metrics_dict.get('phase_coherence', 0.0),
            spectral_centroid=metrics_dict.get('spectral_centroid', 0.0),
            criticality=metrics_dict.get('criticality', 0.0),
            consciousness_level=metrics_dict.get('consciousness_level', 0.0),
            state='IDLE',  # Will be classified by classify_state()
            phi_phase=phi_state.phase,
            phi_depth=phi_state.depth,
            phi_mode=phi_state.mode

        # Classify state based on metrics
        frame.state = frame.classify_state()

        return frame

    def start(self, calibrate_latency) :
        """
        Start audio server

        Args:
            calibrate_latency: Run latency calibration before starting

        Returns:
            True if started successfully
        """
        if self.is_running)
            return True

        print("\n[AudioServer] Starting audio server...")

        # Optional latency calibration
        if calibrate_latency)
            print("[AudioServer] Ensure audio loopback is connected!")

            success = self.latency_manager.calibrate()

            if not success:
                print("[AudioServer] WARNING, continuing with default latency estimates")
            else)

                # Log calibration event
                if self.latency_logger)
                    self.latency_logger.log_calibration_event(True, {
                        'total_latency_ms',
                        'quality')

        try)
            print(f"[AudioServer]   Sample rate)
            print(f"[AudioServer]   Buffer size)
            print(f"[AudioServer]   Input device)
            print(f"[AudioServer]   Output device)

            self.stream = sd.Stream(
                samplerate=self.SAMPLE_RATE,
                blocksize=self.BUFFER_SIZE,
                channels=(self.INPUT_CHANNELS, self.OUTPUT_CHANNELS),
                dtype=np.float32,
                callback=self._audio_callback,
                device=(self.input_device, self.output_device),
                latency='low'

            # Start stream
            self.stream.start()
            self.is_running = True

            # Reset performance counters
            self.callback_count = 0
            self.last_metrics_time = time.time()
            self.last_latency_update = time.time()
            self.processing_time_history = []

            print("[AudioServer] ✓ Audio stream started")
            print("[AudioServer] Processing audio in real-time...")

            return True

        except Exception as e:
            print(f"[AudioServer] ✗ Failed to start audio stream)
            traceback.print_exc()
            return False

    def stop(self):
        """Stop audio server"""
        if not self.is_running)
            return

        print("\n[AudioServer] Stopping audio server...")

        try:
            # Stop stream
            if self.stream)
                self.stream.close()
                self.stream = None

            self.is_running = False

            # Close loggers
            if self.metrics_logger)

            if self.latency_logger)

            print("[AudioServer] ✓ Audio server stopped")

            # Print statistics
            self._print_statistics()

        except Exception as e:
            print(f"[AudioServer] Error stopping)
            traceback.print_exc()

    def _print_statistics(self))
        print("Audio Server Statistics")
        print("=" * 60)

        print(f"\nAudio Processing)
        print(f"  Callbacks)
        print(f"  Sample rate)
        print(f"  Buffer size)

        if self.processing_time_history)
            max_time = np.max(self.processing_time_history)
            buffer_duration = (self.BUFFER_SIZE / self.SAMPLE_RATE) * 1000.0

            print(f"\nProcessing Performance)
            print(f"  Average: {avg_time:.2f} ms / {buffer_duration:.2f} ms ({avg_time/buffer_duration*100)")
            print(f"  Peak: {max_time:.2f} ms ({max_time/buffer_duration*100)")

        # Latency statistics
        latency_stats = self.latency_manager.get_statistics()
        print(f"\nLatency)
        print(f"  Calibrated)
        print(f"  Total measured: {latency_stats['latency']['total_measured_ms'])
        print(f"  Effective: {latency_stats['effective_latency_ms'])
        print(f"  Aligned)

        # Drift statistics
        drift_stats = latency_stats['drift']
        print(f"\nDrift)
        print(f"  Current: {drift_stats['current_drift_ms'])
        print(f"  Rate: {drift_stats['drift_rate_ms_per_sec'])
        print(f"  Cumulative: {drift_stats['cumulative_drift_ms'])

        # Logging statistics
        if self.metrics_logger)
            print(f"\nMetrics Logging)
            print(f"  Frames)
            print(f"  Average FPS: {metrics_stats['average_fps'])
            print(f"  Gaps)

        if self.latency_logger)
            print(f"\nLatency Logging)
            print(f"  Frames)
            print(f"  Average FPS: {latency_log_stats['average_fps'])

        print("=" * 60)

    def apply_preset(self, preset_data):
        """
        Apply preset configuration

        Args:
            preset_data: Preset dictionary
        """
        print(f"[AudioServer] Applying preset, 'Unknown')}")

        try:
            # Update engine parameters
            if 'engine' in preset_data:
                engine = preset_data['engine']

                # Update frequencies and amplitudes
                if 'frequencies' in engine, dtype=np.float64)

                if 'amplitudes' in engine, dtype=np.float64)

                if 'coupling_strength' in engine:
                    self.processor.coupling_strength = engine['coupling_strength']

            # Update Φ parameters
            if 'phi' in preset_data:
                phi = preset_data['phi']

                if 'mode' in phi)

                if 'depth' in phi) == 'manual')

                if 'phase' in phi) == 'manual')

            # Update downmix parameters
            if 'downmix' in preset_data:
                downmix = preset_data['downmix']

                if 'strategy' in downmix)

                if 'weights_l' in downmix, np.array(downmix['weights_l']))

                if 'weights_r' in downmix, np.array(downmix['weights_r']))

            self.current_preset = preset_data
            print("[AudioServer] ✓ Preset applied")

        except Exception as e:
            print(f"[AudioServer] ERROR applying preset)
            traceback.print_exc()

    def get_latest_metrics(self) :
            Latest MetricsFrame or None
        """
        try)
        except Empty) :
            Latest LatencyFrame or None
        """
        try)
        except Empty, param_type, channel, param_name, value) :
        """
        Update a single parameter in real-time

        Args:
            param_type, 'global', 'phi')
            channel) for channel parameters, None for global
            param_name, 'amplitude', 'coupling_strength', etc.)
            value: New value

        Returns:
            True if parameter was updated successfully
        """
        try:
            if param_type == 'channel' and channel is not None:
                if channel < 0 or channel >= 8:
                    print(f"[AudioServer] Invalid channel)
                    return False

                if param_name == 'frequency')
                    return True

                elif param_name == 'amplitude')
                    return True

                elif param_name == 'enabled')
                    # We'll need to track original amplitude separately
                    if not hasattr(self, '_original_amplitudes'))

                    if bool(value):
                        # Enable: restore original amplitude
                        self.processor.amplitudes[channel] = self._original_amplitudes[channel]
                    else:
                        # Disable: save original and set to 0
                        self._original_amplitudes[channel] = self.processor.amplitudes[channel]
                        self.processor.amplitudes[channel] = 0.0
                    return True

            elif param_type == 'global':
                if param_name == 'coupling_strength')
                    return True

                elif param_name == 'gain')
                    if not hasattr(self.downmixer, 'gain'))
                    return True

            elif param_type == 'phi':
                if param_name == 'phase':
                    # Set phase for manual mode
                    if 'manual' in self.phi_controller.sources))
                        return True

                elif param_name == 'depth':
                    # Set depth for manual mode
                    if 'manual' in self.phi_controller.sources))
                        return True

                elif param_name == 'mode'))
                    return True

            print(f"[AudioServer] Unknown parameter)
            return False

        except Exception as e:
            print(f"[AudioServer] Error updating parameter)
            traceback.print_exc()
            return False

    def get_current_parameters(self) :
        """
        Get current parameter values for all channels

        Returns:
            Dictionary with all current parameter values
        """
        return {
            'channels': [
                {
                    'index',
                    'frequency'),
                    'amplitude'),
                    'enabled') > 0.001
                }
                for i in range(8)
            ],
            'global': {
                'coupling_strength'),
                'gain', 'gain', 1.0)
            },
            'phi': {
                'phase').phase,
                'depth').depth,
                'mode')
            }
        }


# Self-test function
def _self_test())
    print("AudioServer Self-Test")
    print("=" * 60)

    try)
        server = AudioServer(enable_logging=False)

        assert server.SAMPLE_RATE == 48000
        assert server.BUFFER_SIZE == 512
        assert not server.is_running

        print("   ✓ Initialization OK")

        # Test preset application (without running)
        print("\n2. Testing preset application...")
        test_preset = {
            'name',
            'engine': {
                'coupling_strength',
            'phi': {
                'mode',
                'depth',
            'downmix': {
                'strategy')
        print("   ✓ Preset application OK")

        print("\n" + "=" * 60)
        print("Self-Test PASSED ✓")
        print("=" * 60)
        print("\nNote)
        print("To test audio processing)
        print("  1. Ensure audio input/output devices are available")
        print("  2. Run)
        print("  3. Follow interactive prompts")

        return True

    except Exception as e:
        print(f"\n✗ Self-Test FAILED)
        traceback.print_exc()
        return False


if __name__ == "__main__")

    if success)
        print("Interactive Audio Server Test")
        print("=" * 60)

        response = input("\nRun interactive audio test? (requires audio I/O) [y/N])

        if response.lower() == 'y')
            server = AudioServer(enable_logging=True)

            calibrate = input("\nRun latency calibration? (requires loopback) [y/N])
            should_calibrate = calibrate.lower() == 'y'

            print("\n[Test] Starting audio server...")
            if server.start(calibrate_latency=should_calibrate))
                print("\nSpeak into microphone or play audio...")
                print("Press Enter to stop")

                input()

                print("\n[Test] Stopping audio server...")
                server.stop()

                print("\n✓ Test complete")
            else)

"""  # auto-closed missing docstring
