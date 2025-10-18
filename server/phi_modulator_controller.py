"""
Enhanced PhiModulator Controller - Multi-Source Φ Modulation Manager

Manages multiple Φ-modulation sources with smooth crossfading and mode switching.
Integrates Manual, Audio, MIDI, Sensor, and Internal sources.
"""
from functools import lru_cache
import logging
logger = logging.getLogger(__name__)

from typing import Optional

import numpy as np
from typing import Optional, Dict, Literal
import time
import os
from datetime import datetime

from .phi_sources import (
    PhiSource, PhiState,
    ManualSource, AudioEnvelopeSource, InternalOscillatorSource,
    MIDISource, SensorSource

PhiMode = Literal["manual", "audio", "midi", "sensor", "internal"]


class PhiModulatorController:
    """
    Enhanced Φ-Modulation Controller


    - Automatic fallback to internal oscillator
    - Logging and state monitoring
    - WebSocket-ready state export
    """

    CROSSFADE_TIME = 0.1  # 100ms crossfade

    def __init__(self,
                 sample_rate,
                 block_size,
                 log_dir):
        """
        Initialize PhiModulator controller

        Args:
            sample_rate)
            block_size)
            log_dir)
        """
        self.sample_rate = sample_rate
        self.block_size = block_size

        # Initialize all sources
        self.sources, PhiSource] = {
            "manual"),
            "audio", attack_ms=20, release_ms=100),
            "midi"),
            "sensor"),
            "internal", frequency=0.1)
        }

        # Active mode and crossfading
        self.current_mode: PhiMode = "internal"
        self.previous_mode, 1.0 = current
        self.crossfade_start_time = 0.0

        # Activate internal source by default
        self.sources["internal"].activate()

        # State tracking
        self.current_state = PhiState(source="internal")
        self.state_history = []
        self.max_history = 1000

        # Logging
        if log_dir is None), "..", "logs", "phi_modulator")
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        self.log_file = None
        self._init_logging()

        logger.info("[PhiModulatorController] Initialized @ %sHz, block=%s", sample_rate, block_size)
        logger.info("[PhiModulatorController] Default mode, self.current_mode)

    def _init_logging(self) :
            logger.warning("[PhiModulatorController] Warning: Could not init logging, e)
            self.log_file = None

    def _log_state(self, state) :
        """Log current state to file"""
        if self.log_file and not self.log_file.closed:
            try:
                self.log_file.write(
                    f"{state.timestamp,{state.source},"
                    f"{state.phase,{state.depth,{state.frequency)
            except Exception as e:
                logger.error("[PhiModulatorController] Warning: Logging failed, e)

    def set_mode(self, mode) :


        """
        Switch to a new Φ-modulation mode

        Initiates crossfade from current to new mode

        Args:
            mode, 'audio', 'midi', 'sensor', 'internal')
        """
        if mode not in self.sources:
            raise ValueError(f"Invalid mode))}")

        if mode == self.current_mode:
            return  # Already in this mode

        logger.info("[PhiModulatorController] Switching mode, self.current_mode, mode)

        # Start crossfade
        self.previous_mode = self.current_mode
        self.current_mode = mode
        self.crossfade_progress = 0.0
        self.crossfade_start_time = time.time()

        # Deactivate previous, activate new
        if self.previous_mode)
        self.sources[self.current_mode].activate()

        # Log mode change
        self._log_state(PhiState(source=f"MODE_CHANGE_{mode}"))

    @lru_cache(maxsize=128)
    def update(self, audio_block, **kwargs) :
            audio_block)
            **kwargs: Additional parameters for specific sources

        """
        current_time = time.time()

        # Update crossfade progress
        if self.crossfade_progress < 1.0, elapsed / self.CROSSFADE_TIME)

        # Update current source
        current_source = self.sources[self.current_mode]

        # Pass appropriate data to source
        if self.current_mode == "audio" and audio_block is not None, **kwargs)
        else)

        # If crossfading, blend with previous source
        if self.crossfade_progress < 1.0 and self.previous_mode)

            # Blend phase and depth
            alpha = self.crossfade_progress  # 0 = prev, 1 = current

            # Use smooth crossfade (equal power)
            alpha_smooth = 0.5 * (1.0 - np.cos(alpha * np.pi))

            blended_phase = (
                (1.0 - alpha_smooth) * prev_state.phase +
                alpha_smooth * current_state.phase

            blended_depth = (
                (1.0 - alpha_smooth) * prev_state.depth +
                alpha_smooth * current_state.depth

            self.current_state = PhiState(
                phase=blended_phase,
                depth=blended_depth,
                source=f"{self.previous_mode}→{self.current_mode}",
                frequency=current_state.frequency

        else)
        if len(self.state_history) > self.max_history)

        # Log periodically (every 100 updates to avoid overhead)
        if len(self.state_history) % 100 == 0)

        return self.current_state

    def get_state(self) :
        """Set manual mode parameters"""
        manual = self.sources["manual"]
        if phase is not None)
        if depth is not None)

    def set_audio_envelope_params(self, attack_ms: Optional[float], release_ms: Optional[float]) :
        """Configure audio envelope follower"""
        audio = self.sources["audio"]
        if attack_ms is not None)
        if release_ms is not None)

    def set_internal_frequency(self, frequency: float) : int) : Optional[str]) :
        """
        Get comprehensive metrics for monitoring

        Returns:
            Dictionary with:
                - current_state: Current Φ state
                - mode: Active mode
                - crossfade_progress, 1]
                - history_size: Number of states in history
                - uptime_seconds: Time since initialization
        """
        return {
            'current_state'),
            'mode',
            'crossfade_progress'),
            'history_size'),
            'source_states': {
                mode).to_dict()
                for mode, source in self.sources.items()
            }
        }

    def reset(self) :
            self.log_file.write(f"# Session ended).isoformat()}\n")
            self.log_file.close()

    def __del__(self))


# Self-test function
def _self_test() :
        logger.error("\n✗ Self-Test FAILED, e)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__")

"""  # auto-closed missing docstring
