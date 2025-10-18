#!/usr/bin/env python3
"""
Sensor Calibration Utility - Feature 023 (FR-007)

Calibrates Φ-sensors and stores calibration data to config/sensors.json

Usage:
    python calibrate_sensors.py --duration 10000

Requirements:
- FR-007: Calibration routine stores offsets in /config/sensors.json
- SC-005: Calibration residual error < 2%
"""

from typing import Any, Dict, List, Optional, Tuple
import asyncio
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
from .sensor_manager import SensorManager


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def calibrate_sensors(duration_ms: int = 10000, config_path: str = "config/sensors.json"):
    """
    Perform sensor calibration and save results

    Args:
        duration_ms: Calibration duration in milliseconds
        config_path: Path to save calibration config
    """
    logger.info("=" * 70)
    logger.info("Soundlab Φ-Sensor Calibration Utility")
    logger.info("Feature 023 - Hardware Validation")
    logger.info("=" * 70)
    logger.info(str())

    # Create sensor manager
    config = {
        'simulation_mode': True,  # Set to False for real hardware
        'enable_watchdog': False,  # Disable watchdog during calibration
    }

    logger.info("Initializing sensor manager...")
    manager = SensorManager(config)

    # Start acquisition
    logger.info("Starting sensor acquisition...")
    await manager.start()

    # Wait for sensors to stabilize
    logger.info("Stabilizing sensors (2 seconds)...")
    await asyncio.sleep(2.0)

    # Perform calibration
    logger.info("Performing calibration (%d ms)...", duration_ms)
    logger.info("\n%s", '='*70)
    logger.info("Calibration in progress: %s ms", duration_ms)
    logger.info("%s", '='*70)

    calibration = await manager.calibrate(duration_ms=duration_ms)

    logger.info("\nCalibration Results:")
    logger.info("-" * 70)
    logger.info("Samples collected: %s", calibration['samples'])
    logger.info("Duration: %s ms", calibration['duration_ms'])
    logger.error("Residual error: %s%", calibration['residual_error']:.2f)
    logger.info(str())

    # Show channel ranges
    for channel in ['phi_depth', 'phi_phase', 'coherence', 'criticality']:
        if channel in calibration:
            data = calibration[channel]
            logger.info("%s:", channel)
            logger.info("  Min:  %s", data['min']:.4f)
            logger.info("  Max:  %s", data['max']:.4f)
            logger.info("  Mean: %s", data['mean']:.4f)
            logger.info("  Std:  %s", data['std']:.4f)
            logger.info(str())

    # Check residual error (SC-005)
    if calibration['residual_error'] >= 2.0:
        logger.error("⚠ WARNING: Residual error %s% exceeds 2% threshold", calibration['residual_error']:.2f)
        logger.info("  Calibration may be inaccurate. Consider recalibrating.")
    else:
        logger.error("✓ Residual error %s% within acceptable range", calibration['residual_error']:.2f)

    # Save calibration
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Saving calibration to %s...", config_path)
    await manager.save_calibration(calibration, str(config_file))

    logger.info(str())
    logger.info("=" * 70)
    logger.info("✓ Calibration saved to: %s", config_path)
    logger.info("=" * 70)

    # Stop acquisition
    await manager.stop()

    return calibration


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calibrate Φ-sensors and save calibration data"
    )

    parser.add_argument(
        '--duration',
        type=int,
        default=10000,
        help='Calibration duration in milliseconds (default: 10000)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='config/sensors.json',
        help='Output path for calibration data (default: config/sensors.json)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run calibration
    asyncio.run(calibrate_sensors(
        duration_ms=args.duration,
        config_path=args.output
    ))


if __name__ == "__main__":
    main()
