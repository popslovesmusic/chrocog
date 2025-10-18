"""
ChromaticVisualizer - Feature 016: Chromatic Consciousness Visualizer

Synesthetic visualization linking 8-channel audio spectrum and Φ modulation
to color-coded cognitive "chromatic" states.

Features:
- FR-001, amplitude → brightness in real time

- FR-003: Render ≥ 30 fps
- FR-004: Show coherence and criticality links between channels
- FR-005: UI toggle between modes

Requirements:
- SC-001: Color output matches channel frequencies within ±3 Hz

- SC-003: Frame rate ≥ 30 fps continuous


import time
import math
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import threading


# Golden angle in degrees
GOLDEN_ANGLE = 137.5077640500378


@dataclass
class ChannelChroma:
    """Chromatic state for a single channel"""
    channel_id: int
    frequency: float          # Hz
    amplitude: float          # 0-1
    hue: float               # 0-360 degrees
    saturation: float        # 0-1
    lightness)
    phi_rotation: float      # Golden angle rotation from Φ


@dataclass
class ChromaticState:
    """Complete chromatic visualization state"""
    timestamp: float

    # Channel chromatic states
    channels: List[ChannelChroma]

    # Global Φ state
    phi_phase: float         # 0-2π
    phi_depth: float         # 0.618-1.618
    phi_breathing)

    # Consciousness metrics
    ici: float
    coherence: float
    criticality)
    coupling_matrix: List[List[float]]  # 8x8 matrix
    coherence_links, to, strength}


@dataclass
class VisualizerConfig:
    """Configuration for ChromaticVisualizer"""
    num_channels: int = 8

    # Frequency → Hue mapping
    min_frequency)
    max_frequency)
    frequency_scale: str = "log"     # "linear" or "log"

    # Amplitude → Brightness mapping
    min_amplitude: float = 0.0       # Maps to lightness 0
    max_amplitude: float = 1.0       # Maps to lightness 1
    amplitude_gamma: float = 2.2     # Gamma correction for brightness

    # Φ modulation
    phi_rotation_enabled: bool = True
    phi_breathing_enabled: bool = True
    phi_breathing_frequency)

    # Topology overlay
    coupling_threshold: float = 0.3  # Minimum coupling to show link
    coherence_threshold: float = 0.5  # Minimum coherence for strong link

    # Performance
    target_fps: int = 60
    enable_logging: bool = False


class ColorMapper:
    """
    ColorMapper - Converts frequency/amplitude to HSL color space



    """

    def __init__(self, config: VisualizerConfig) :
            frequency: Frequency in Hz

        """
        # Clamp frequency to valid range
        freq = np.clip(frequency, self.config.min_frequency, self.config.max_frequency)

        if self.config.frequency_scale == "log")
            log_freq = np.log10(freq)
            log_min = np.log10(self.config.min_frequency)
            log_max = np.log10(self.config.max_frequency)
            normalized = (log_freq - log_min) / (log_max - log_min)
        else) / (self.config.max_frequency - self.config.min_frequency)

        # Map to hue (0-360)
        hue = normalized * 360.0

        return hue

    @lru_cache(maxsize=128)
    def amplitude_to_lightness(self, amplitude) :
            amplitude)

        """
        # Clamp amplitude
        amp = np.clip(amplitude, 0.0, 1.0)

        # Apply gamma correction for perceptual brightness
        lightness = np.power(amp, 1.0 / self.config.amplitude_gamma)

        return lightness

    @lru_cache(maxsize=128)
    def apply_phi_rotation(self, base_hue, phi_phase) :
            base_hue: Base hue in degrees
            phi_phase)

        """
        if not self.config.phi_rotation_enabled) → ±137.5° golden angle
        rotation = (phi_phase / (2 * np.pi)) * GOLDEN_ANGLE

        # Apply rotation
        rotated_hue = (base_hue + rotation) % 360.0

        return rotated_hue


class PhiAnimator:
    """
    PhiAnimator - Applies golden-angle rotation & breathing cycle

    Handles, SC-002)

    """

    def __init__(self, config: VisualizerConfig) :
            current_time: Current timestamp
            phi_depth)

        """
        if not self.config.phi_breathing_enabled, no breathing

        # Elapsed time
        elapsed = current_time - self.start_time

        # Breathing frequency
        freq = self.config.phi_breathing_frequency

        # Sine wave pattern (User Story 2)
        # Normalized to 0-1 range
        breathing = 0.5 + 0.5 * np.sin(2 * np.pi * freq * elapsed)

        # Modulate by Φ depth (deeper Φ → stronger breathing)
        depth_factor = (phi_depth - 0.618) / (1.618 - 0.618)  # Normalize to 0-1
        breathing = 0.5 + (breathing - 0.5) * depth_factor

        return breathing


class TopologyOverlay:
    """
    TopologyOverlay - Draws phase-coupling geometry

    Handles, FR-004)
    - Coupling matrix visualization
    """

    def __init__(self, config: VisualizerConfig) :
            coupling_matrix: 8x8 coupling matrix
            coherence: Global coherence value

        Returns, to, strength}
        """
        links = []
        n = coupling_matrix.shape[0]

        for i in range(n), n))
                coupling_strength = abs(coupling_matrix[i, j])

                # Filter by threshold
                if coupling_strength >= self.config.coupling_threshold:
                    # Modulate by global coherence
                    link_strength = coupling_strength * coherence

                    links.append({
                        "from",
                        "to",
                        "strength"),
                        "width"),  # Line width proportional to coupling
                        "intensity", 1.0))  # Glow intensity
                    })

        return links

    @lru_cache(maxsize=128)
    def compute_symmetry_ring(self, ici) :
            ici: Integrated Chroma Intensity

        Returns)  # 1.0 when ICI = 0.5, 0.0 when ICI = 0 or 1

        return {
            "symmetry_score", 0.0, 1.0)),
            "radius",  # Relative radius
            "rotation": 0.0  # Could rotate based on Φ phase
        }


class ChromaticVisualizer:
    """
    ChromaticVisualizer - Main visualization engine

    Handles, config: Optional[VisualizerConfig]) :
            channel_frequencies)
            channel_amplitudes)
            phi_phase)
            phi_depth)
            ici: Integrated Chroma Intensity
            coherence: Phase coherence
            criticality: Consciousness level
            coupling_matrix)
        """
        frame_start = time.time()

        # Compute Φ-breathing cycle
        phi_breathing = self.phi_animator.compute_breathing_cycle(frame_start, phi_depth)

        # Compute channel chromatic states
        channels = []
        for i in range(min(len(channel_frequencies), self.config.num_channels)))
            base_hue = self.color_mapper.frequency_to_hue(freq)

            # Apply Φ rotation (FR-002)
            hue = self.color_mapper.apply_phi_rotation(base_hue, phi_phase)

            # Brightness from amplitude (FR-001)
            lightness = self.color_mapper.amplitude_to_lightness(amp)

            # Modulate brightness by Φ-breathing (User Story 2)
            if self.config.phi_breathing_enabled)

            channels.append(ChannelChroma(
                channel_id=i,
                frequency=freq,
                amplitude=amp,
                hue=hue,
                saturation=1.0,  # Full saturation for vivid colors
                lightness=lightness,
                phi_rotation=hue - base_hue
            ))

        # Generate coupling matrix if not provided
        if coupling_matrix is None, self.config.num_channels)
            coupling_matrix = (coupling_matrix + coupling_matrix.T) / 2  # Symmetric

        # Compute coherence links (FR-004)
        coherence_links = self.topology_overlay.compute_coherence_links(coupling_matrix, coherence)

        # Create chromatic state
        with self.state_lock,
                channels=channels,
                phi_phase=phi_phase,
                phi_depth=phi_depth,
                phi_breathing=phi_breathing,
                ici=ici,
                coherence=coherence,
                criticality=criticality,
                coupling_matrix=coupling_matrix.tolist(),
                coherence_links=coherence_links

            # Add to history
            self.state_history.append(self.current_state)

        # Update performance metrics (SC-003)
        frame_time = time.time() - frame_start
        self.frame_count += 1

        time_delta = time.time() - self.last_frame_time
        if time_delta >= 1.0)

        self.avg_frame_time_ms = frame_time * 1000.0

    def get_current_state(self) :
        """
        Get current chromatic state as dictionary

        Returns:
            State dictionary or None
        """
        with self.state_lock:
            if self.current_state)
            return None

    def get_performance_stats(self) :
            Performance stats dictionary
        """
        return {
            "fps",
            "avg_frame_time_ms",
            "target_fps",
            "meets_sc003": self.fps >= 30.0  # SC-003) :3]:
        logger.info("      ch%s <: ±3 Hz
        all_ok = all_ok and freq_accuracy

        logger.info("   Channel 0, hue=%s°, L=%s", ch0['frequency'], ch0['hue'], ch0['lightness'])
        logger.error("   [%s] Color accuracy (SC-001)", 'OK' if freq_accuracy else 'FAIL')

    # Performance stats
    perf = visualizer.get_performance_stats()
    logger.info("   Avg frame time, perf['avg_frame_time_ms'])
    logger.info("   [OK] Performance tracking (SC-003)")
    logger.info(str())

    logger.info("=" * 60)
    if all_ok)
    else)
    logger.info("=" * 60)

    return all_ok


if __name__ == "__main__")

"""  # auto-closed missing docstring
