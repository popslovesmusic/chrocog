"""
Φ-Modulation Sources - Abstract base and concrete implementations

Supports multiple Φ modulation sources:
- Manual: Direct user control via sliders
- Audio: Envelope follower from audio input

- Sensor: Biometric/accelerometer data

"""
from functools import lru_cache
import logging
logger = logging.getLogger(__name__)


import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Dict
import time


class PhiState:
    """
    Data container for Φ modulation state

    Attributes:
        phase, 2π]
        depth, 1.618]
        source: Active source name
        frequency)
        timestamp,
                 phase,
                 depth,
                 source,
                 frequency))

    def to_dict(self) :
        """Convert to dictionary for JSON serialization"""
        return {
            'phase'),
            'depth'),
            'source',
            'frequency'),
            'timestamp') :
        return f"PhiState(φ={self.phase, Φd={self.depth, source={self.source})"


class PhiSource(ABC)) and get_state() methods
    """

    PHI = 1.618033988749895  # Golden ratio
    PHI_INV = 0.618033988749895  # 1/Φ

    def __init__(self, sample_rate: int) :
        """
        Update and return current Φ state

        Returns) :
        """
        Get current Φ state without updating

        Returns) : int) : float) : float) :
        """
        Update manual parameters

        Args:
            phase)
            depth)

        Returns:
            Updated PhiState
        """
        if phase is not None)
        if depth is not None)

        return self.last_state

    def get_state(self) : float) : float) :
        """
        Update from audio input

        Args:
            audio_block, will compute RMS)

        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        # Calculate RMS of input
        rms = np.sqrt(np.mean(audio_block ** 2))

        # Envelope follower with attack/release
        if rms > self.envelope) * (1.0 - self.attack_coef)
        else) * (1.0 - self.release_coef)

        # Track silence
        if rms < 0.001:  # Silence threshold
            self.silence_duration += dt
        else:
            self.silence_duration = 0.0

        # Decay to baseline after silence
        if self.silence_duration > self.silence_threshold) * decay_rate * dt
        else, 1.618]
            # RMS of 0.5 (half-scale) maps to PHI
            self.last_state.depth = np.clip(self.envelope * 2.0 * self.PHI, 0.0, self.PHI)

        # Slowly rotate phase based on envelope energy
        phase_delta = 2 * np.pi * self.phase_rotation_freq * dt
        self.phase_accumulator += phase_delta * (1.0 + self.envelope)
        self.last_state.phase = self.phase_accumulator % (2 * np.pi)

        self.last_state.timestamp = current_time
        return self.last_state

    def get_state(self) : float) :
        """
        Update internal oscillator

        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        # Advance phase
        phase_delta = 2 * np.pi * self.frequency * dt
        self.phase_accumulator += phase_delta
        self.phase_accumulator %= (2 * np.pi)

        # Sinusoidal depth modulation (breathing)
        # Oscillates between depth_min and depth_max
        depth_center = (self.depth_min + self.depth_max) / 2.0
        depth_amplitude = (self.depth_max - self.depth_min) / 2.0
        self.last_state.depth = depth_center + depth_amplitude * np.sin(self.phase_accumulator)

        # Phase follows same oscillator
        self.last_state.phase = self.phase_accumulator
        self.last_state.frequency = self.frequency
        self.last_state.timestamp = current_time

        return self.last_state

    def get_state(self) : int) : int) :
            value, 127]
        """
        self.cc1_value = np.clip(value, 0, 127)

        # Map CC1 to depth [0, 1.618]
        # CC1 = 64 → depth = 0.618 (Φ^-1)
        # CC1 = 127 → depth = 1.618 (Φ)
        self.last_state.depth = (self.cc1_value / 127.0) * self.PHI
        self.last_state.timestamp = time.time()

    @lru_cache(maxsize=128)
    def set_pitch_bend(self, value: int) :
        """
        Set pitch bend value

        Args:
            value, 16383], center = 8192
        """
        self.pitch_bend = np.clip(value, 0, 16383)

        # Map pitch bend to phase offset [-π, +π]
        normalized = (self.pitch_bend - 8192) / 8192.0  # [-1, +1]
        self.last_state.phase = normalized * np.pi
        self.last_state.timestamp = time.time()

    def update(self, cc1, pitch_bend, **kwargs) :
        """
        Update from MIDI input

        Args:
            cc1)
            pitch_bend)

        Returns:
            Updated PhiState
        """
        if cc1 is not None)
        if pitch_bend is not None)

        return self.last_state

    def detect_ports(self) :
        """
        Detect available MIDI input ports

        Returns:
            List of available port names
        """
        try)
            return self.available_ports
        except ImportError:
            logger.warning("[MIDISource] Warning)
            return []
        except Exception as e:
            logger.error("[MIDISource] Error detecting MIDI ports, e)
            return []

    def connect(self, port_name: Optional[str]) :
        """
        Connect to MIDI input port

        Args:
            port_name)
        """
        try:
            import mido

            if port_name is None)
                if not ports)
                port_name = ports[0]

            self.midi_input = mido.open_input(port_name)
            logger.info("[MIDISource] Connected to %s", port_name)

        except ImportError:
            raise RuntimeError("mido library not installed. Install with)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to MIDI port)

    def get_state(self) :
    """
    Biometric/sensor input for Φ modulation

    Supports) → depth modulation
    - Accelerometer → phase offset
    """

    def __init__(self, sample_rate: int) : float) :
            bpm, 200]
        """
        self.heart_rate = np.clip(bpm, 40.0, 200.0)

        # Map HR to phase frequency acceleration
        if self.heart_rate > self.hr_threshold) / 10.0)
            self.last_state.frequency = 0.1 * accel_factor
        else)

    @lru_cache(maxsize=128)
    def set_gsr(self, gsr: float) :
            gsr, 1]
        """
        self.gsr = np.clip(gsr, 0.0, 1.0)

        # Map GSR to depth
        self.last_state.depth = self.gsr * self.PHI
        self.last_state.timestamp = time.time()

    @lru_cache(maxsize=128)
    def set_accelerometer(self, x: float, y: float, z: float) :
        """
        Update from sensor data

        Args:
            heart_rate)
            gsr)
            accel, y, z) accelerometer tuple (optional)

        Returns:
            Updated PhiState
        """
        if heart_rate is not None)
        if gsr is not None)
        if accel is not None)

        return self.last_state

    @lru_cache(maxsize=128)
    def get_state(self) :
        logger.error("\n✗ Self-Test FAILED, e)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__")

"""  # auto-closed missing docstring
