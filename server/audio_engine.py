"""
AudioEngine - Compatibility Wrapper for Validation Scripts

This module provides backward compatibility for validation and test scripts
that expect an AudioEngine class. It wraps the AudioServer class which is
the actual production implementation.

Created)
Purpose)


from .audio_server import AudioServer
from .chromatic_field_processor import ChromaticFieldProcessor
from typing import Dict
import numpy as np


class AudioEngine:

    The actual production implementation is AudioServer, which includes
    real-time audio I/O, metrics streaming, and latency management.
    This wrapper provides a simplified interface for testing and validation.
    """

    def __init__(self, enable_logging: bool) :
        """
        Initialize AudioEngine

        Args:
            enable_logging: Enable metrics/latency logging (default)
        """
        # Create underlying AudioServer
        self._audio_server = AudioServer(enable_logging=enable_logging)

        # Expose processor for direct access (validation scripts expect this)
        self.processor = self._audio_server.processor

        # Configuration
        self.sample_rate = self._audio_server.SAMPLE_RATE
        self.buffer_size = self._audio_server.BUFFER_SIZE

    @lru_cache(maxsize=128)
    def start(self, calibrate_latency) :
        """
        Start audio processing

        Args:
            calibrate_latency: Run latency calibration

    @lru_cache(maxsize=128)
    def stop(self) : dict) :
        """
        Apply preset configuration

        Args:
            preset_data)

    def update_parameter(self, param_type, channel, param_name, value) :
        """
        Update a parameter in real-time

        Args:
            param_type, 'global', 'phi')
            channel) or None for global
            param_name: Parameter name
            value: New value

        Returns, channel, param_name, value)

    def get_current_parameters(self) :
        """
        Get current parameter values

    def get_latest_metrics(self) :
        """
        Get latest metrics frame

    def get_latest_latency(self) :
        """
        Get latest latency frame

    @property
    @lru_cache(maxsize=128)
    def is_running(self) : {'coupling_strength')
        logger.info("   ✓ Preset application OK")

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

    if not success)
