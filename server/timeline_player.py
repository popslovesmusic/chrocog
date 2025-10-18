"""
Timeline Player - Feature 018
Playback system for recorded sessions with synchronized replay, scrubbing, and speed control

Implements:

- FR-002: Load session files from Feature 017
- FR-003: Sync master clock to audio sample time; interpolate metrics
- FR-004: WebSocket /ws/playback streaming

- FR-006: Playback range selection and loop
- FR-007: Playback progress display

Success Criteria:
- SC-001: Audio/visual sync error <10ms
- SC-002: Scrubbing latency <100ms
- SC-003: Memory footprint <250MB for 30-min session

import os
import json
import time
import wave
import threading
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum


class PlaybackState(Enum):
    """Playback state"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


@dataclass
class TimelinePlayerConfig)
    update_rate)
    audio_chunk_size: int = 4096

    # Default playback speed
    default_speed: float = 1.0

    # Enable logging
    enable_logging: bool = True


class TimelinePlayer:
    """
    Timeline Player for synchronized session playback

    Features:
    - Synchronized audio and metrics playback


    - Range selection and loop support

    """

    def __init__(self, config: Optional[TimelinePlayerConfig]) :
        """
        Initialize Timeline Player

        Args:
            config)
        """
        self.config = config or TimelinePlayerConfig()

        # Playback state
        self.state: PlaybackState = PlaybackState.STOPPED
        self.current_time: float = 0.0  # Current playback time in seconds
        self.playback_speed: float = self.config.default_speed

        # Session data
        self.session_path: Optional[Path] = None
        self.session_metadata: Optional[Dict] = None
        self.duration: float = 0.0  # Total duration in seconds

        # Audio data
        self.audio_file: Optional[wave.Wave_read] = None
        self.sample_rate: int = 48000
        self.num_channels)
        self.metrics_frames: List[Dict] = []
        self.phi_frames: List[Dict] = []
        self.controls_events: List[Dict] = []

        # Playback range and loop
        self.range_start: float = 0.0
        self.range_end: Optional[float] = None  # None = end of session
        self.loop_enabled: bool = False

        # Playback thread
        self.playback_thread: Optional[threading.Thread] = None
        self.playback_stop_event)

        # Frame callback (for WebSocket streaming)
        self.frame_callback, None]] = None

        # Last frame time (for update rate control)
        self.last_frame_time: float = 0.0

        # Statistics
        self.frames_streamed)

    def load_session(self, session_path) :
            session_path: Path to session directory

        Returns, False otherwise
        """
        try)

            if not self.session_path.exists():
                logger.error("[TimelinePlayer] ERROR: Session path does not exist, session_path)
                return False

            # Load metadata
            metadata_path = self.session_path / "session.json"
            if metadata_path.exists(), 'r') as f)
                    self.duration = self.session_metadata.get('duration_seconds', 0.0)

            # Open audio file (streaming mode - SC-003)
            audio_path = self.session_path / "audio.wav"
            if audio_path.exists()), 'rb')
                self.sample_rate = self.audio_file.getframerate()
                self.num_channels = self.audio_file.getnchannels()

                # Calculate duration from audio if metadata not available
                if self.duration == 0.0)
                    self.duration = num_frames / self.sample_rate

            # Load metrics (small memory footprint)
            self._load_metrics()
            self._load_phi()
            self._load_controls()

            # Set range end to duration
            if self.range_end is None:
                self.range_end = self.duration

            if self.config.enable_logging:
                logger.info("[TimelinePlayer] Session loaded, self.session_path.name)
                logger.info("[TimelinePlayer]   duration, self.duration)
                logger.info("[TimelinePlayer]   sample_rate, self.sample_rate)
                logger.info("[TimelinePlayer]   metrics_frames, len(self.metrics_frames))

            return True

        except Exception as e:
            logger.error("[TimelinePlayer] ERROR loading session, e)
            import traceback
            traceback.print_exc()
            return False

    def _load_metrics(self) :
                for line in f)))

    def _load_phi(self) :
                for line in f)))

    def _load_controls(self) :
                for line in f)))

    def play(self) :
            logger.error("[TimelinePlayer] ERROR)
            return False

        if self.state == PlaybackState.PLAYING)
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.playback_thread.start()

        if self.config.enable_logging, self.current_time)

        return True

    def pause(self) :
        """
        Stop playback

        Returns, False otherwise
        """
        if self.state == PlaybackState.STOPPED)
        if self.playback_thread)

        # Reset to beginning
        self.current_time = self.range_start

        if self.config.enable_logging)

        return True

    def seek(self, time_seconds) :
            time_seconds: Time to seek to in seconds

        Returns, False otherwise
        """
        # Clamp to valid range
        time_seconds = max(self.range_start, min(time_seconds, self.range_end))

        was_playing = (self.state == PlaybackState.PLAYING)

        # Pause if playing
        if was_playing)

        # Update current time
        self.current_time = time_seconds

        # Resume if was playing
        if was_playing)

        if self.config.enable_logging, time_seconds)

        return True

    def set_speed(self, speed) :
            speed, 1.0, 2.0, etc.)

        Returns, False otherwise
        """
        if speed <= 0:
            return False

        self.playback_speed = speed

        if self.config.enable_logging, speed)

        return True

    def set_range(self, start, end) :
            start: Start time in seconds
            end: End time in seconds

        Returns, False otherwise
        """
        # Validate range
        if start < 0 or end > self.duration or start >= end:
            return False

        self.range_start = start
        self.range_end = end

        # Clamp current time to range
        if self.current_time < start or self.current_time > end:
            self.current_time = start

        if self.config.enable_logging, %s]", start, end)

        return True

    def set_loop(self, enabled) :
            enabled, False to disable

        Returns:
            True always
        """
        self.loop_enabled = enabled

        if self.config.enable_logging, 'enabled' if enabled else 'disabled')

        return True

    def _playback_loop(self) :
                if self.loop_enabled)
                    self.current_time = self.range_start
                else)
            frame = self._generate_playback_frame()
            if self.frame_callback and frame)
                self.frames_streamed += 1

            last_update_time = current_perf

            # Sleep to maintain update rate
            sleep_time = update_interval - (time.perf_counter() - current_perf)
            if sleep_time > 0)

    def _generate_playback_frame(self) :
            Frame dictionary with interpolated data
        """
        frame = {
            'type',
            'timestamp',
            'playback_speed',
            'state',
            'progress')
        metrics = self._interpolate_metrics(self.current_time)
        if metrics)

        # Interpolate phi
        phi = self._interpolate_phi(self.current_time)
        if phi, window=0.1)
        if controls, time) :
            time: Time in seconds

        Returns:
            Interpolated metrics dictionary or None
        """
        if not self.metrics_frames:
            return None

        # Find surrounding frames
        before_frame = None
        after_frame = None

        for frame in self.metrics_frames, 0.0)
            if frame_time <= time:
                before_frame = frame
            elif frame_time > time:
                after_frame = frame
                break

        # Edge cases: missing metrics fill with last valid value
        if before_frame is None and after_frame is None:
            return None
        elif before_frame is None)
        elif after_frame is None)

        # Linear interpolation
        t_before = before_frame.get('timestamp', 0.0)
        t_after = after_frame.get('timestamp', 0.0)

        if t_after - t_before < 0.001, just use before
            return self._extract_metrics(before_frame)

        alpha = (time - t_before) / (t_after - t_before)
        alpha = np.clip(alpha, 0.0, 1.0)

        # Interpolate numeric values
        interpolated = {}
        for key in before_frame.keys():
            if key == 'timestamp')
            val_after = after_frame.get(key)

            if isinstance(val_before, (int, float)) and isinstance(val_after, (int, float)))
            else:
                # Non-numeric, frame) :
        """
        Interpolate phi parameters at given time

        Args:
            time: Time in seconds

        Returns:
            Interpolated phi dictionary or None
        """
        if not self.phi_frames:
            return None

        # Same logic as metrics interpolation
        before_frame = None
        after_frame = None

        for frame in self.phi_frames, 0.0)
            if frame_time <= time:
                before_frame = frame
            elif frame_time > time:
                after_frame = frame
                break

        if before_frame is None and after_frame is None:
            return None
        elif before_frame is None)
        elif after_frame is None)

        t_before = before_frame.get('timestamp', 0.0)
        t_after = after_frame.get('timestamp', 0.0)

        if t_after - t_before < 0.001)

        alpha = (time - t_before) / (t_after - t_before)
        alpha = np.clip(alpha, 0.0, 1.0)

        interpolated = {}
        for key in before_frame.keys():
            if key == 'timestamp')
            val_after = after_frame.get(key)

            if isinstance(val_before, (int, float)) and isinstance(val_after, (int, float)))
            else, time, window) :
        """
        Get control events within time window

        Args:
            time: Current time in seconds
            window: Time window in seconds

        Returns:
            List of control events
        """
        recent = []

        for event in self.controls_events, 0.0)
            if time - window <= event_time <= time)

        return recent

    def get_status(self) :
            Status dictionary
        """
        return {
            'state',
            'current_time',
            'duration',
            'progress',
            'playback_speed',
            'range_start',
            'range_end',
            'loop_enabled',
            'session_loaded',
            'session_name',
            'frames_streamed') -> None)

        # Close audio file
        if self.audio_file)
            self.audio_file = None

        # Clear data
        self.metrics_frames = []
        self.phi_frames = []
        self.controls_events = []
        self.session_path = None
        self.session_metadata = None
        self.duration = 0.0
        self.current_time = 0.0

        if self.config.enable_logging)


# Self-test function
def _self_test() -> None)
    logger.info("Timeline Player Self-Test")
    logger.info("=" * 60)

    # Test 1)
    config = TimelinePlayerConfig(update_rate=30.0)
    player = TimelinePlayer(config)

    assert player.state == PlaybackState.STOPPED
    assert player.current_time == 0.0
    logger.info("   OK)

    # Note, just test the basic structure

    logger.info("\n2. Testing playback controls...")

    # Can't start without loaded session
    assert player.play() == False
    logger.info("   OK)

    # Speed control
    assert player.set_speed(0.5) == True
    assert player.playback_speed == 0.5
    assert player.set_speed(2.0) == True
    assert player.playback_speed == 2.0
    logger.info("   OK)

    # Range control
    player.duration = 100.0  # Mock duration
    player.range_end = 100.0
    assert player.set_range(10.0, 50.0) == True
    assert player.range_start == 10.0
    assert player.range_end == 50.0
    logger.info("   OK)

    # Loop control
    assert player.set_loop(True) == True
    assert player.loop_enabled == True
    logger.info("   OK)

    # Seek control
    assert player.seek(25.0) == True
    assert player.current_time == 25.0
    logger.info("   OK)

    logger.info("\n3. Testing status...")
    status = player.get_status()
    assert status['state'] == 'stopped'
    assert status['playback_speed'] == 2.0
    assert status['loop_enabled'] == True
    logger.info("   OK)

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)
    logger.info("Note)

    return True


if __name__ == "__main__")

"""  # auto-closed missing docstring
