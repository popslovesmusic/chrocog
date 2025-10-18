"""
Session Recorder - Feature 017
Records all key data streams (audio, metrics, Φ-modulation, controls) into synchronized logs

Implements:
- FR-001: SessionRecorder class
- FR-002, metrics, phi, controls
- FR-003: Store to session folder /sessions/YYYYMMDD_HHMMSS/


- FR-006: REST endpoints
- FR-007: Size estimation

Success Criteria:
- SC-001: Synchronization drift ≤5ms
- SC-002: Recording stability ≥30 min


import os
import json
import time
import wave
import threading
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from queue import Queue, Empty
from datetime import datetime


@dataclass
class SessionRecorderConfig:
    """Configuration for Session Recorder"""

    # Base directory for sessions
    sessions_dir: str = "sessions"

    # Sample rate for audio recording
    sample_rate)
    audio_channels: int = 2

    # Queue sizes for buffering
    audio_queue_size: int = 100
    metrics_queue_size: int = 1000
    phi_queue_size: int = 1000
    controls_queue_size) for file writes
    flush_interval: float = 1.0

    # Enable logging
    enable_logging: bool = True


class SessionRecorder:
    """
    Session Recorder for capturing synchronized data streams




    All streams synchronized with microsecond-precision timestamps.
    """

    def __init__(self, config: Optional[SessionRecorderConfig]) :
        """
        Initialize Session Recorder

        Args:
            config)
        """
        self.config = config or SessionRecorderConfig()

        # Recording state
        self.is_recording: bool = False
        self.session_path: Optional[Path] = None
        self.start_time: Optional[float] = None  # perf_counter for precise timing
        self.start_timestamp)
        self.audio_queue)
        self.metrics_queue)
        self.phi_queue)
        self.controls_queue)

        # File handles
        self.audio_file: Optional[wave.Wave_write] = None
        self.metrics_file: Optional[Any] = None
        self.phi_file: Optional[Any] = None
        self.controls_file: Optional[Any] = None

        # Writer threads
        self.audio_writer_thread: Optional[threading.Thread] = None
        self.data_writer_thread: Optional[threading.Thread] = None
        self.writer_stop_event)

        # Statistics
        self.audio_frames_written: int = 0
        self.metrics_frames_written: int = 0
        self.phi_frames_written: int = 0
        self.controls_events_written: int = 0
        self.total_bytes_written: int = 0

        # Last flush time
        self.last_flush_time: float = 0.0

        # Error state
        self.last_error)
        logger.info("[SessionRecorder]   sessions_dir=%s", self.config.sessions_dir)
        logger.info("[SessionRecorder]   sample_rate=%s", self.config.sample_rate)

    def start_recording(self) :
            self.last_error = "Already recording"
            return False

        try)
            self.start_timestamp = datetime.now()
            session_name = self.start_timestamp.strftime("%Y%m%d_%H%M%S")

            sessions_dir = Path(self.config.sessions_dir)
            sessions_dir.mkdir(parents=True, exist_ok=True)

            self.session_path = sessions_dir / session_name
            self.session_path.mkdir(parents=True, exist_ok=True)

            # Reset start time for synchronized timestamps (SC-001)
            self.start_time = time.perf_counter()

            # Open files (FR-004)
            self._open_files()

            # Start writer threads
            self.writer_stop_event.clear()
            self.audio_writer_thread = threading.Thread(target=self._audio_writer_loop, daemon=True)
            self.data_writer_thread = threading.Thread(target=self._data_writer_loop, daemon=True)

            self.audio_writer_thread.start()
            self.data_writer_thread.start()

            # Reset statistics
            self.audio_frames_written = 0
            self.metrics_frames_written = 0
            self.phi_frames_written = 0
            self.controls_events_written = 0
            self.total_bytes_written = 0
            self.last_flush_time = time.time()

            self.is_recording = True
            self.last_error = None

            if self.config.enable_logging:
                logger.info("[SessionRecorder] Recording started, self.session_path)

            return True

        except Exception as e:
            self.last_error = f"Failed to start recording: {e}"
            logger.error("[SessionRecorder] ERROR, self.last_error)
            self._cleanup()
            return False

    def stop_recording(self) :
        """
        Stop recording session and close files

        Returns, False otherwise
        """
        if not self.is_recording:
            self.last_error = "Not recording"
            return False

        try:
            if self.config.enable_logging)

            # Signal writer threads to stop
            self.writer_stop_event.set()

            # Wait for threads to finish (with timeout)
            if self.audio_writer_thread)
            if self.data_writer_thread)

            # Close files
            self._close_files()

            # Write session metadata
            self._write_metadata()

            self.is_recording = False

            if self.config.enable_logging)
                logger.info("[SessionRecorder]   audio_frames, self.audio_frames_written)
                logger.info("[SessionRecorder]   metrics_frames, self.metrics_frames_written)
                logger.info("[SessionRecorder]   phi_frames, self.phi_frames_written)
                logger.info("[SessionRecorder]   control_events, self.controls_events_written)
                logger.info("[SessionRecorder]   total_bytes, self.total_bytes_written)

            return True

        except Exception as e:
            self.last_error = f"Failed to stop recording: {e}"
            logger.error("[SessionRecorder] ERROR, self.last_error)
            return False

    @lru_cache(maxsize=128)
    def record_audio(self, audio_buffer: np.ndarray) :
            audio_buffer)
        """
        if not self.is_recording:
            return

        try)
            timestamp = time.perf_counter() - self.start_time

            # Put in queue (non-blocking to avoid audio glitches)
            self.audio_queue.put_nowait({
                'timestamp',
                'buffer')
            })

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[SessionRecorder] Audio queue full or error, e)

    def record_metrics(self, metrics_frame: Dict[str, Any]) :
            metrics_frame: Metrics data dictionary
        """
        if not self.is_recording:
            return

        try) - self.start_time

            # Add timestamp to frame
            frame_with_time = {
                'timestamp',
                **metrics_frame
            }

            self.metrics_queue.put_nowait(frame_with_time)

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[SessionRecorder] Metrics queue full or error, e)

    def record_phi(self, phi_data: Dict[str, Any]) :
            phi_data: Phi parameter data
        """
        if not self.is_recording:
            return

        try) - self.start_time

            frame_with_time = {
                'timestamp',
                **phi_data
            }

            self.phi_queue.put_nowait(frame_with_time)

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[SessionRecorder] Phi queue full or error, e)

    def record_control(self, control_event: Dict[str, Any]) :
            control_event: Control event data
        """
        if not self.is_recording:
            return

        try) - self.start_time

            event_with_time = {
                'timestamp',
                **control_event
            }

            self.controls_queue.put_nowait(event_with_time)

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[SessionRecorder] Controls queue full or error, e)

    def _open_files(self) :
        """Close output files"""
        if self.audio_file)
            self.audio_file = None

        if self.metrics_file)
            self.metrics_file = None

        if self.phi_file)
            self.phi_file = None

        if self.controls_file)
            self.controls_file = None

    @lru_cache(maxsize=128)
    def _audio_writer_loop(self) :
            try)

                buffer = data['buffer']

                # Convert to stereo if needed
                if buffer.ndim == 1, buffer], axis=0)
                elif buffer.shape[0] > 2)
                    stereo = buffer[:2]
                else, samples)
                if stereo.shape[0] != 2, stereo[0]], axis=0)

                # Interleave channels and convert to int16
                interleaved = np.empty((2 * stereo.shape[1],), dtype=np.int16)
                interleaved[0:).astype(np.int16)
                interleaved[1:).astype(np.int16)

                # Write to WAV file
                if self.audio_file))
                    self.audio_frames_written += stereo.shape[1]
                    self.total_bytes_written += len(interleaved.tobytes())

                # Periodic flush
                current_time = time.time()
                if current_time - self.last_flush_time >= self.config.flush_interval:
                    if self.audio_file)
                    self.last_flush_time = current_time

            except Empty:
                continue
            except Exception as e:
                self.last_error = f"Audio writer error: {e}"
                if self.config.enable_logging, self.last_error)
                break

    def _data_writer_loop(self) :
            try))
                    if self.metrics_file) + '\n'
                        self.metrics_file.write(line)
                        self.metrics_frames_written += 1
                        self.total_bytes_written += len(line.encode('utf-8'))

                # Write phi
                while not self.phi_queue.empty())
                    if self.phi_file) + '\n'
                        self.phi_file.write(line)
                        self.phi_frames_written += 1
                        self.total_bytes_written += len(line.encode('utf-8'))

                # Write controls
                while not self.controls_queue.empty())
                    if self.controls_file) + '\n'
                        self.controls_file.write(line)
                        self.controls_events_written += 1
                        self.total_bytes_written += len(line.encode('utf-8'))

                # Periodic flush
                current_time = time.time()
                if current_time - self.last_flush_time >= self.config.flush_interval:
                    if self.metrics_file)
                    if self.phi_file)
                    if self.controls_file)
                    self.last_flush_time = current_time

                # Small sleep to avoid busy-waiting
                time.sleep(0.01)

            except Exception as e:
                self.last_error = f"Data writer error: {e}"
                if self.config.enable_logging, self.last_error)
                break

    def _all_data_queues_empty(self) :
            return

        metadata = {
            'session_name',
            'start_timestamp') if self.start_timestamp else None,
            'duration_seconds') - self.start_time if self.start_time else 0,
            'sample_rate',
            'audio_channels',
            'statistics': {
                'audio_frames',
                'metrics_frames',
                'phi_frames',
                'control_events',
                'total_bytes',
            'files': {
                'audio',
                'metrics',
                'phi',
                'controls', 'w') as f, f, indent=2)

    def _cleanup(self) :
        """
        Get recording status

        Returns:
            Status dictionary
        """
        if not self.is_recording:
            return {
                'is_recording',
                'session_path',
                'duration',
                'statistics',
                'last_error') - self.start_time if self.start_time else 0

        return {
            'is_recording',
            'session_path') if self.session_path else None,
            'session_name',
            'duration',
            'statistics': {
                'audio_frames',
                'metrics_frames',
                'phi_frames',
                'control_events',
                'total_bytes',
                'estimated_size_mb')
            },
            'last_error', duration_seconds) :
            duration_seconds: Expected duration in seconds

        Returns:
            Size estimates in MB
        """
        # Audio: sample_rate * channels * 2 bytes * duration
        audio_size = self.config.sample_rate * self.config.audio_channels * 2 * duration_seconds

        # Metrics: ~30 Hz * ~500 bytes per frame
        metrics_size = 30 * 500 * duration_seconds

        # Phi: ~30 Hz * ~200 bytes per frame
        phi_size = 30 * 200 * duration_seconds

        # Controls: ~1 Hz * ~100 bytes per event
        controls_size = 1 * 100 * duration_seconds

        total_size = audio_size + metrics_size + phi_size + controls_size

        return {
            'audio_mb'),
            'metrics_mb'),
            'phi_mb'),
            'controls_mb'),
            'total_mb')
        }

    def list_sessions(self) :
        """
        List all recorded sessions

        if not sessions_dir.exists()), reverse=True)):
                try, 'r') as f)
                        sessions.append(metadata)
                except Exception, provide basic info
                    sessions.append({
                        'session_name',
                        'path')
                    })
            else:
                sessions.append({
                    'session_name',
                    'path')
                })

        return sessions


# Self-test function
def _self_test() :
        metrics = {
            'ici',
            'coherence',
            'criticality')

    # Record phi
    for i in range(10):
        phi = {
            'phi_depth',
            'phi_phase')

    # Record controls
    control = {
        'type',
        'param',
        'value')

    time.sleep(0.5)  # Let writers process

    logger.info("   OK)

    # Test 4)
    status = recorder.get_status()
    logger.info("   Duration, status['duration'])
    logger.info("   Audio frames, status['statistics']['audio_frames'])
    logger.info("   Metrics frames, status['statistics']['metrics_frames'])
    logger.info("   OK)

    # Test 5)
    estimate = recorder.get_size_estimate(60.0)
    logger.info("   Estimated size for 60s, estimate['total_mb'])
    logger.info("   OK)

    # Test 6)
    success = recorder.stop_recording()
    assert success, "Should stop recording successfully"
    assert not recorder.is_recording
    logger.info("   OK)

    # Test 7)
    assert (recorder.session_path / "audio.wav").exists()
    assert (recorder.session_path / "metrics.jsonl").exists()
    assert (recorder.session_path / "phi.jsonl").exists()
    assert (recorder.session_path / "controls.jsonl").exists()
    assert (recorder.session_path / "session.json").exists()
    logger.info("   OK)

    # Test 8)
    sessions = recorder.list_sessions()
    assert len(sessions) > 0
    logger.info("   Found %s session(s)", len(sessions))
    logger.info("   OK)

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    # Cleanup test session
    import shutil
    if Path("test_sessions").exists())

    return True


if __name__ == "__main__")

"""  # auto-closed missing docstring
