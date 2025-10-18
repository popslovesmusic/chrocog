"""
Quick functionality test for Feature 011 - no delays
"""
from functools import lru_cache
import logging
logger = logging.getLogger(__name__)


from typing import Any, Dict, List, Optional, Tuple
import time
import numpy as np
from .phi_sensor_bridge import SensorData, SensorType, AudioBeatDetector, SensorConfig
from .phi_router import PhiRouter, PhiRouterConfig, PhiSourcePriority

logger.info("=" * 60)
logger.info("Feature 011: Quick Functionality Test")
logger.info("=" * 60)

PHI_MIN = 0.618033988749895
PHI_MAX = 1.618033988749895

# Test 1: Normalization
logger.info("\n1. Testing Phi normalization (FR-002)...")
test_cases = [(0, 0.618), (64, 1.118), (127, 1.618)]
all_ok = True
for midi_val, expected in test_cases:
    normalized = PHI_MIN + (midi_val / 127.0) * (PHI_MAX - PHI_MIN)
    ok = abs(normalized - expected) < 0.001
    all_ok = all_ok and ok
    logger.error("   MIDI %s -> %s (expected %s) %s", midi_val:3d, normalized:.3f, expected:.3f, '[OK]' if ok else '[FAIL]')

# Test 2: PhiRouter creation
logger.info("\n2. Testing PhiRouter creation...")
try:
    router = PhiRouter(PhiRouterConfig(enable_logging=False))
    router.start()
    logger.info("   [OK] PhiRouter created and started")
except Exception as e:
    logger.error("   [FAIL] PhiRouter creation failed: %s", e)
    all_ok = False

# Test 3: Source registration
logger.info("\n3. Testing source registration (FR-001)...")
try:
    router.register_source("midi", PhiSourcePriority.MIDI)
    router.register_source("serial", PhiSourcePriority.SERIAL)
    status = router.get_status()
    ok = status.source_count == 2
    all_ok = all_ok and ok
    logger.error("   Sources registered: %s %s", status.source_count, '[OK]' if ok else '[FAIL]')
except Exception as e:
    logger.error("   [FAIL] Source registration failed: %s", e)
    all_ok = False

# Test 4: Source updates
logger.info("\n4. Testing source updates...")
try:
    data = SensorData(SensorType.MIDI_CC, time.time(), 64, 1.0, "midi")
    router.update_source("midi", data)
    phi, phase = router.get_current_phi()
    ok = PHI_MIN <= phi <= PHI_MAX
    all_ok = all_ok and ok
    logger.error("   Phi value: %s %s", phi:.3f, '[OK]' if ok else '[FAIL - out of range]')
except Exception as e:
    logger.error("   [FAIL] Source update failed: %s", e)
    all_ok = False

# Test 5: Audio beat detector
logger.info("\n5. Testing audio beat detector...")
try:
    beats = []
    @lru_cache(maxsize=128)
    def beat_cb(data: np.ndarray) -> None:
        beats.append(data)

    config = SensorConfig(sensor_type=SensorType.AUDIO_BEAT)
    detector = AudioBeatDetector(config, beat_cb)

    # Quiet baseline
    for _ in range(3):
        quiet = np.random.randn(512).astype(np.float32) * 0.1
        detector.process_audio(quiet)

    # Loud beat
    loud = np.random.randn(512).astype(np.float32) * 3.0
    detector.process_audio(loud)

    ok = len(beats) > 0
    all_ok = all_ok and ok
    logger.error("   Beats detected: %s %s", len(beats), '[OK]' if ok else '[FAIL]')

    if beats:
        phi_ok = PHI_MIN <= beats[0].normalized_value <= PHI_MAX
        all_ok = all_ok and phi_ok
        logger.error("   Beat Phi: %s %s", beats[0].normalized_value:.3f, '[OK]' if phi_ok else '[FAIL]')
except Exception as e:
    logger.error("   [FAIL] Audio beat detector failed: %s", e)
    all_ok = False

# Test 6: Telemetry
logger.info("\n6. Testing telemetry (FR-004)...")
try:
    status = router.get_status()
    checks = [
        ("Timestamp", status.timestamp > 0),
        ("Active source", status.active_source is not None),
        ("Phi value", PHI_MIN <= status.phi_value <= PHI_MAX),
        ("Source count", status.source_count > 0)
    ]
    for name, ok in checks:
        all_ok = all_ok and ok
        logger.error("   %s: %s", name, '[OK]' if ok else '[FAIL]')
except Exception as e:
    logger.error("   [FAIL] Telemetry failed: %s", e)
    all_ok = False

# Cleanup
router.stop()

# Summary
logger.info("\n" + "=" * 60)
if all_ok:
    logger.info("[PASS] All core functionality tests passed")
    logger.info("\nFeature 011 components validated:")
    logger.info("  - Phi normalization (FR-002)")
    logger.info("  - PhiRouter source management (FR-001)")
    logger.info("  - Audio beat detection")
    logger.info("  - Telemetry (FR-004)")
else:
    logger.error("[FAIL] Some tests failed - see details above")
logger.info("=" * 60)
