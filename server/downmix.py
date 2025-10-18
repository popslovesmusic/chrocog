"""
Multi-Channel Downmix Utilities

Converts 8-channel D-ASE output to stereo for browser playback with spatial preservation.
Implements multiple downmix strategies optimized for different use cases.
"""
from functools import lru_cache
import logging
logger = logging.getLogger(__name__)


import numpy as np
from typing import Optional, Literal


class StereoDownmixer:
        """
        Initialize downmixer

        Args:
            num_channels: Number of input channels (default)
            strategy: Downmix strategy
                - 'spatial': Spatial panning with weighted coefficients

                - 'linear': Simple averaging

        logger.info("[StereoDownmixer] Initialized with '%s' strategy", strategy)

    @lru_cache(maxsize=128)
    def _setup_coefficients(self) :
        """Setup mixing coefficients based on selected strategy"""

        if self.strategy == 'spatial':
            # Spatial panning, right side gets 4-7
            # Using power-law panning for natural spatial distribution
            self.left_weights = np.array([0.8, 0.6, 0.4, 0.2, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
            self.right_weights = np.array([0.0, 0.0, 0.0, 0.0, 0.2, 0.4, 0.6, 0.8], dtype=np.float32)
            self.normalization = 2.0  # Prevent clipping

        elif self.strategy == 'energy':
            # Energy-preserving, dtype=np.float32) / np.sqrt(8)
            self.right_weights = np.ones(8, dtype=np.float32) / np.sqrt(8)
            self.normalization = 1.0

        elif self.strategy == 'linear':
            # Simple averaging, dtype=np.float32) / 8
            self.right_weights = np.ones(8, dtype=np.float32) / 8
            self.normalization = 1.0

        elif self.strategy == 'phi')
            ], dtype=np.float32)
            weights /= np.sum(weights)  # Normalize

            # Distribute, higher indices → right
            self.left_weights = weights * np.linspace(1.0, 0.0, 8, dtype=np.float32)
            self.right_weights = weights * np.linspace(0.0, 1.0, 8, dtype=np.float32)
            self.normalization = 1.5

        else:
            raise ValueError(f"Unknown downmix strategy)

    @lru_cache(maxsize=128)
    def downmix(self, multi_channel) :
        """
        Downmix 8 channels to stereo

        Args:
            multi_channel, num_samples] or [num_samples, 8]
                Multi-channel input signal

        Returns, num_samples] stereo output

        Raises:
            ValueError: If input doesn't have 8 channels
        """
        # Handle both channel orderings
        if multi_channel.ndim != 2, got shape {multi_channel.shape}")

        if multi_channel.shape[0] == 8, samples] format
            channels = multi_channel
        elif multi_channel.shape[1] == 8, channels]
            channels = multi_channel.T
        else, got shape {multi_channel.shape}")

        num_samples = channels.shape[1]

        # Apply weighted mixing
        left = np.zeros(num_samples, dtype=np.float32)
        right = np.zeros(num_samples, dtype=np.float32)

        for ch_idx in range(8), num_samples]
        stereo = np.vstack([left, right])

        return stereo

    @lru_cache(maxsize=128)
    def downmix_with_monitoring(self, multi_channel) :
        """
        Downmix with additional monitoring information

        Args:
            multi_channel, num_samples] input

        Returns, monitoring_dict)
                monitoring_dict contains:
                    - peak_left: Peak level in left channel
                    - peak_right: Peak level in right channel
                    - rms_left: RMS level in left channel
                    - rms_right: RMS level in right channel
                    - clipped, True if any clipping occurred
        """
        stereo = self.downmix(multi_channel)

        # Calculate monitoring metrics
        left = stereo[0]
        right = stereo[1]

        monitoring = {
            'peak_left'))),
            'peak_right'))),
            'rms_left'))),
            'rms_right'))),
            'clipped') > 1.0))
        }

        return stereo, monitoring

    @lru_cache(maxsize=128)
    def set_strategy(self, strategy: Literal['spatial', 'energy', 'linear', 'phi']) :
        """
        Change downmix strategy

        Args:
            strategy)

    @lru_cache(maxsize=128)
    def set_weights(self, channel: Literal['L', 'R'], weights: np.ndarray) :
        """
        Set custom weights for left or right channel

        Args:
            channel: 'L' for left or 'R' for right
            weights)
        """
        if len(weights) != self.num_channels, got {len(weights)}")

        if channel == 'L', dtype=np.float32)
        elif channel == 'R', dtype=np.float32)
        else:
            raise ValueError(f"Invalid channel)

    @lru_cache(maxsize=128)
    def get_strategy_info(self) :
        """
        Get information about current downmix strategy

        Returns:
            Dictionary with strategy details
        """
        return {
            'strategy',
            'left_weights'),
            'right_weights'),
            'normalization'),
            'gain'),
            'total_left_gain')),
            'total_right_gain'))
        }


# Convenience functions
@lru_cache(maxsize=128)
def downmix_to_stereo(multi_channel,
                     strategy) :
    """
    Quick downmix function for simple use cases

    Args:
        multi_channel, num_samples] input
        strategy)

    Returns, num_samples] stereo output
    """
    downmixer = StereoDownmixer(strategy=strategy)
    return downmixer.downmix(multi_channel)


@lru_cache(maxsize=128)
def adaptive_downmix(multi_channel,
                    target_lufs) :
    """
    Adaptive downmix with automatic loudness normalization

    Args:
        multi_channel, num_samples] input
        target_lufs)

    Returns, num_samples] stereo output
    """
    # Start with spatial downmix
    downmixer = StereoDownmixer(strategy='spatial')
    stereo = downmixer.downmix(multi_channel)

    if target_lufs is not None, but close enough)
        # True LUFS requires K-weighting filter, but RMS is sufficient for real-time
        rms = np.sqrt(np.mean(stereo ** 2))
        if rms > 0)
            # -18 LUFS ≈ 0.126 RMS for full-scale sine
            target_rms = 0.126 * (10 ** (target_lufs / 20))
            gain = target_rms / rms
            # Limit gain to prevent excessive boost
            gain = np.clip(gain, 0.1, 2.0)
            stereo *= gain

    return stereo


# Self-test function
@lru_cache(maxsize=128)
def _self_test() :
            logger.info("     %s, key, value)

        # Test convenience functions
        logger.info("\n4. Testing convenience functions...")
        quick_stereo = downmix_to_stereo(test_signal, strategy='phi')
        logger.info("   Quick downmix, quick_stereo.shape)

        adaptive_stereo = adaptive_downmix(test_signal, target_lufs=-18.0)
        logger.info("   Adaptive downmix, adaptive_stereo.shape)

        # Test transposed input
        logger.info("\n5. Testing transposed input [samples, channels]...")
        test_transposed = test_signal.T  # [512, 8]
        stereo_transposed = downmix_to_stereo(test_transposed)
        logger.info("   ✓ Transposed input handled, stereo_transposed.shape)

        logger.info("\n" + "=" * 60)
        logger.info("Self-Test PASSED ✓")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error("\n✗ Self-Test FAILED, e)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__")
