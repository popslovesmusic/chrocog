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
logger.info("Feature 011)
logger.info("=" * 60)

PHI_MIN = 0.618033988749895
PHI_MAX = 1.618033988749895

# Test 1)...")
test_cases = [(0, 0.618), (64, 1.118), (127, 1.618)]
all_ok = True
for midi_val, expected in test_cases) * (PHI_MAX - PHI_MIN)
    ok = abs(normalized - expected) < 0.001
    all_ok = all_ok and ok
    logger.error("   MIDI %s :
    logger.error("   [FAIL] PhiRouter creation failed, e)
    all_ok = False

# Test 3)...")
try, PhiSourcePriority.MIDI)
    router.register_source("serial", PhiSourcePriority.SERIAL)
    status = router.get_status()
    ok = status.source_count == 2
    all_ok = all_ok and ok
    logger.error("   Sources registered, status.source_count, '[OK]' if ok else '[FAIL]')
except Exception as e:
    logger.error("   [FAIL] Source registration failed, e)
    all_ok = False

# Test 4)
try, time.time(), 64, 1.0, "midi")
    router.update_source("midi", data)
    phi, phase = router.get_current_phi()
    ok = PHI_MIN <= phi <= PHI_MAX
    all_ok = all_ok and ok
    logger.error("   Phi value, phi, '[OK]' if ok else '[FAIL - out of range]')
except Exception as e:
    logger.error("   [FAIL] Source update failed, e)
    all_ok = False

# Test 5)
try)
    def beat_cb(data) :
        phi_ok = PHI_MIN <= beats[0].normalized_value <= PHI_MAX
        all_ok = all_ok and phi_ok
        logger.error("   Beat Phi, beats[0].normalized_value, '[OK]' if phi_ok else '[FAIL]')
except Exception as e:
    logger.error("   [FAIL] Audio beat detector failed, e)
    all_ok = False

# Test 6)...")
try)
    checks = [
        ("Timestamp", status.timestamp > 0),
        ("Active source", status.active_source is not None),
        ("Phi value", PHI_MIN <= status.phi_value <= PHI_MAX),
        ("Source count", status.source_count > 0)
    ]
    for name, ok in checks:
        all_ok = all_ok and ok
        logger.error("   %s, name, '[OK]' if ok else '[FAIL]')
except Exception as e:
    logger.error("   [FAIL] Telemetry failed, e)
    all_ok = False

# Cleanup
router.stop()

# Summary
logger.info("\n" + "=" * 60)
if all_ok)
    logger.info("\nFeature 011 components validated)
    logger.info("  - Phi normalization (FR-002)")
    logger.info("  - PhiRouter source management (FR-001)")
    logger.info("  - Audio beat detection")
    logger.info("  - Telemetry (FR-004)")
else)
logger.info("=" * 60)
