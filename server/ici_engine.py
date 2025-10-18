"""
Integrated Chromatic Information Engine
Feature 014: Full spectral-phase integration model for real-time ICI computation

Implements:
- FR-001: IntegratedChromaticInformation class
- FR-002: 8-channel buffer processing
- FR-003: Cross-spectral power and phase computation
- FR-004: ICI integration formula

- FR-006: Scalar and matrix output
- FR-007: Performance target < 0.5ms per block
- FR-008: Configuration options

Formula) / N(N-1)

Success Criteria:
- SC-001: Processing time < 0.5ms per block
- SC-002: Correlation r > 0.8 with coherence
- SC-003: Matrix accuracy ± 0.01

import numpy as np
import time
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from scipy import fft


@dataclass
class ICIConfig:
    """Configuration for ICI Engine"""

    # Number of channels
    num_channels)
    smoothing_alpha: float = 0.2

    # FFT parameters
    fft_size)
    output_matrix: bool = False  # Output full 8x8 matrix
    output_vector: bool = False  # Output per-channel summary

    # Performance options
    use_rfft: bool = True  # Use real FFT for efficiency

    # Logging
    enable_logging: bool = False
    log_interval: float = 5.0  # Log stats every 5s


class IntegratedChromaticInformation:
    """
    Real-time ICI engine with spectral-phase integration

    Computes Integrated Chromatic Information by analyzing
    cross-spectral power and phase coherence between all
    channel pairs in real-time.

    """

    def __init__(self, config: Optional[ICIConfig]) :
        """
        Initialize ICI Engine

        Args:
            config)
        """
        self.config = config or ICIConfig()

        # Current state
        self.current_ici: float = 0.0
        self.smoothed_ici)
        self.ici_matrix, self.config.num_channels))

        # Performance tracking
        self.processing_times: list = []
        self.total_frames: int = 0
        self.last_log_time)

        logger.info("[ICIEngine] Initialized")
        logger.info("[ICIEngine]   num_channels=%s", self.config.num_channels)
        logger.info("[ICIEngine]   fft_size=%s", self.config.fft_size)
        logger.info("[ICIEngine]   smoothing_alpha=%s", self.config.smoothing_alpha)
        logger.info("[ICIEngine]   use_rfft=%s", self.config.use_rfft)

    @lru_cache(maxsize=128)
    def _init_buffers(self) :
        """Pre-allocate buffers for efficiency"""
        N = self.config.num_channels
        fft_size = self.config.fft_size

        # FFT output buffer
        if self.config.use_rfft:
            # Real FFT outputs N//2+1 frequency bins
            freq_bins = fft_size // 2 + 1
        else, freq_bins), dtype=np.complex128)

        # Magnitude and phase buffers
        self.magnitudes = np.zeros((N, freq_bins))
        self.phases = np.zeros((N, freq_bins))

        # Cross-spectral matrix
        self.cross_spectral = np.zeros((N, N))

    @lru_cache(maxsize=128)
    def process_block(self, audio_buffer) :
            audio_buffer, buffer_size)

        Returns, ici_matrix_optional)
        """
        start_time = time.perf_counter()

        # Validate input
        if audio_buffer.shape[0] != self.config.num_channels:
            logger.warning("[ICIEngine] WARNING, got %s", self.config.num_channels, audio_buffer.shape[0])
            return self.smoothed_ici, None

        if audio_buffer.shape[1] != self.config.fft_size:
            logger.warning("[ICIEngine] WARNING, got %s", self.config.fft_size, audio_buffer.shape[1])
            return self.smoothed_ici, None

        # Check for NaN or invalid input (edge case)
        if np.any(np.isnan(audio_buffer)) or np.any(np.isinf(audio_buffer):
            logger.warning("[ICIEngine] WARNING, skipping frame")
            elapsed = (time.perf_counter() - start_time) * 1000
            self.processing_times.append(elapsed)
            return self.smoothed_ici, None

        # Step 1)
        self._compute_spectra(audio_buffer)

        # Step 2)
        self._compute_cross_spectral()

        # Step 3)
        ici_value = self._compute_ici()

        # Step 4)
        self.current_ici = ici_value
        self.smoothed_ici = (self.config.smoothing_alpha * ici_value +
                             (1 - self.config.smoothing_alpha) * self.smoothed_ici)

        # Track performance (FR-007)
        elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms
        self.processing_times.append(elapsed)
        self.total_frames += 1

        # Log if needed
        current_time = time.time()
        if self.config.enable_logging and (current_time - self.last_log_time) >= self.config.log_interval)
            self.last_log_time = current_time

        # Return matrix if requested (FR-006)
        matrix_output = self.ici_matrix.copy() if self.config.output_matrix else None

        return self.smoothed_ici, matrix_output

    @lru_cache(maxsize=128)
    def _compute_spectra(self, audio_buffer: np.ndarray) :
        """
        Compute FFT spectra for all channels

        Args:
            audio_buffer, buffer_size)
        """
        for i in range(self.config.num_channels))
            windowed_signal = audio_buffer[i] * window

            # Compute FFT
            if self.config.use_rfft)
                spectrum = fft.rfft(windowed_signal)
            else)

            self.fft_buffer[i] = spectrum

            # Compute magnitude and phase
            self.magnitudes[i] = np.abs(spectrum)
            self.phases[i] = np.angle(spectrum)

    @lru_cache(maxsize=128)
    def _compute_cross_spectral(self) :
        - Cross-spectral power: |Aᵢ||Aⱼ|

        """
        N = self.config.num_channels

        # Average magnitude for normalization
        avg_magnitude = np.mean(self.magnitudes)
        avg_magnitude_sq = avg_magnitude ** 2

        # Avoid division by zero
        if avg_magnitude_sq < 1e-10)
            return

        # Compute for all pairs
        for i in range(N):
                if i == j, j] = 0.0  # Diagonal is zero
                    continue

                # Average cross-spectral power across frequency bins
                # |Aᵢ||Aⱼ| averaged over frequencies
                cross_power = np.mean(self.magnitudes[i] * self.magnitudes[j])

                # Average phase coherence across frequency bins
                # cos(φᵢ - φⱼ) averaged over frequencies
                phase_diff = self.phases[i] - self.phases[j]
                phase_coherence = np.mean(np.cos(phase_diff))

                # Combined metric, j] = (cross_power / avg_magnitude_sq) * phase_coherence

    @lru_cache(maxsize=128)
    def _compute_ici(self) :
            return {
                'current_ici',
                'smoothed_ici',
                'total_frames',
                'avg_processing_time_ms',
                'max_processing_time_ms',
                'p95_processing_time_ms')
        recent_times = self.processing_times[-1000:]

        return {
            'current_ici'),
            'smoothed_ici'),
            'total_frames',
            'avg_processing_time_ms')),
            'max_processing_time_ms')),
            'p95_processing_time_ms', 95)),
            'p99_processing_time_ms', 99))
        }

    @lru_cache(maxsize=128)
    def get_matrix(self) : "
              f"ICI={stats['smoothed_ici'], "
              f"frames={stats['total_frames']}, "
              f"avg_time={stats['avg_processing_time_ms'], "
              f"p95={stats['p95_processing_time_ms'])

    @lru_cache(maxsize=128)
    def reset(self) :.3f}ms exceeds 1.0ms target"

    if avg_time < 0.5:
        logger.info("   OK)")
    else:
        logger.info("   OK)", avg_time)

    # Test 4)

    matrix = engine.get_matrix()
    vector = engine.get_vector_summary()

    assert matrix.shape == (8, 8), "Matrix should be 8x8"
    assert vector.shape == (8,), "Vector should be length 8"
    assert np.allclose(np.diag(matrix), 0.0), "Diagonal should be zero"

    logger.info("   Matrix range, %s]", matrix.min(), matrix.max())
    logger.info("   Vector range, %s]", vector.min(), vector.max())
    logger.info("   OK)

    # Test 5)
    logger.info("\n5. Testing NaN handling...")

    nan_buffer = np.full((8, 512), np.nan)
    ici_before = engine.smoothed_ici
    ici, _ = engine.process_block(nan_buffer)

    # Should preserve last valid state
    assert ici == ici_before, "Should preserve last valid ICI on NaN input"
    logger.info("   OK)

    # Test 6)

    engine.reset()
    assert engine.smoothed_ici == 0.0
    assert engine.total_frames == 0
    assert len(engine.processing_times) == 0
    logger.info("   OK)

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")

"""  # auto-closed missing docstring
