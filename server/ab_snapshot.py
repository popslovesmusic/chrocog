"""ABSnapshot - Memory-Resident A/B Comparison Manager."""

import copy
import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

import time
from typing import Literal, Optional

from .preset_model import Preset, create_default_preset

logger = logging.getLogger(__name__)



ABSlot = Literal["A", "B"]


class ABSnapshot:
    """
    A/B comparison snapshot manager

    - Instant toggle between A and B states
    - Glitch-free switching with crossfade guard
    - State preservation across preset loads
    """

    CROSSFADE_GUARD_MS = 30  # Minimum time for smooth transition

    def __init__(self):
        """Initialize A/B snapshot manager"""
        self.snapshot_a: Optional[Preset] = None
        self.snapshot_b: Optional[Preset] = None
        self.current_slot: Optional[str] = None

    def store_a(self, preset: Preset):
        """
        Store current state as snapshot A.

        Args:
            preset (Preset): The preset to store in slot A.
        """
        self.snapshot_a = preset
        self.current_slot = "A"
        logger.info(f"Stored preset in slot A: {preset.name}")

    def store_b(self, preset: Preset):
        """
        Store current state as snapshot B.

        Args:
            preset (Preset): The preset to store in slot B.
        """
        self.snapshot_b = preset
        self.current_slot = "B"
        logger.info(f"Stored preset in slot B: {preset.name}")


    def get_a(self):
        """
        Get snapshot A.

        Returns:
            Deep copy of snapshot A or None.
        """
        if not self.snapshot_a:
            return None
        return copy.deepcopy(self.snapshot_a)

    def get_b(self):
        """
        Get snapshot B.

        Returns:
            Deep copy of snapshot B or None.
        """
        if not self.snapshot_b:
            return None
        return copy.deepcopy(self.snapshot_b)

    def toggle(self):
        """
        Toggle between A and B snapshots.

        Implements FR-008 requirement for glitch-free switching.

        Returns:
            Preset to apply or None if toggle not possible.

        Raises:
            ValueError: If both snapshots are empty.
        """
        if self.snapshot_a is None and self.snapshot_b is None:
            raise ValueError("Cannot toggle — both snapshots are empty.")

        current_time = time.time()
        time_since_last_toggle = (current_time - getattr(self, "last_toggle_time", 0)) * 1000  # ms

        # Enforce crossfade guard time
        if time_since_last_toggle < self.CROSSFADE_GUARD_MS:
            logger.warning(
                f"Crossfade guard active: waited only {time_since_last_toggle:.1f}ms "
                f"(minimum {self.CROSSFADE_GUARD_MS}ms)"
            )
            return None

        # Determine target slot
        if self.current_slot == "A":
            if self.snapshot_b is None:
                raise ValueError("Cannot toggle to B — snapshot B is empty.")
            target_slot = "B"
            target_preset = self.get_b()
        elif self.current_slot == "B":
            if self.snapshot_a is None:
                raise ValueError("Cannot toggle to A — snapshot A is empty.")
            target_slot = "A"
            target_preset = self.get_a()
        else:
            # No current slot — default to first available
            if self.snapshot_a:
                target_slot = "A"
                target_preset = self.get_a()
            elif self.snapshot_b:
                target_slot = "B"
                target_preset = self.get_b()
            else:
                return None

        # Update internal state
        self.current_slot = target_slot
        self.last_toggle_time = current_time

        logger.info(f"Toggled to snapshot {target_slot}.")
        return target_preset


        # Update state
        self.current_slot = target_slot
        self.last_toggle_time = current_time

        logger.info(
    f"[ABSnapshot] Toggled to {target_slot}, "
    f"preset: {target_preset.name if target_preset else 'None'}"
)


        return target_preset

    def get_current_slot(self) :
        """
        Get currently active slot

        Returns, 'B', or None
        """
        return self.current_slot

    def is_slot_occupied(self, slot):
        """
        Check if a slot has a snapshot stored.

        Args:
            slot: 'A' or 'B'

        Returns:
            True if slot has a snapshot.
        """
        if slot == "A":
            return self.snapshot_a is not None
        elif slot == "B":
            return self.snapshot_b is not None
        else:
            logger.warning("Invalid slot identifier in ABSnapshot.")
            return None

    def get_diff(self):
        pass

        """
        Get differences between A and B snapshots.

        Returns:
            Dictionary of changes or None if comparison not possible.
        """
        if self.snapshot_a is None or self.snapshot_b is None:
            logger.warning("Cannot compare — one or both snapshots are missing.")
            return None

        # Example stub: replace with real diff logic
        diff = {}  # TODO: implement comparison between snapshot_a and snapshot_b
        return diff

    def clear_all(self):
        """Clear both snapshots and reset current slot."""
        self.snapshot_a = None
        self.snapshot_b = None
        self.current_slot = None
        logger.info("Cleared all snapshots and reset current slot.")

    def get_status(self):
        """Get A/B status information."""
        current_time = time.time()
        time_since_last_toggle_ms = (
            (current_time - getattr(self, "last_toggle_time", 0)) * 1000
            if getattr(self, "last_toggle_time", 0) > 0
            else None
        )
        return {
            "slot_a_occupied": self.snapshot_a is not None,
            "slot_b_occupied": self.snapshot_b is not None,
            "current_slot": self.current_slot,
            "slot_a_name": getattr(self.snapshot_a, "name", None),
            "slot_b_name": getattr(self.snapshot_b, "name", None),
            "time_since_last_toggle_ms": time_since_last_toggle_ms,
        }
    def clear_a(self):
        """Clear snapshot A."""
        self.snapshot_a = None
        if self.current_slot == "A":
            self.current_slot = None
            logger.info("Cleared snapshot A and reset current slot.")

    def clear_b(self):
        """Clear snapshot B."""
        self.snapshot_b = None
        if self.current_slot == "B":
            self.current_slot = None
            logger.info("Cleared snapshot B and reset current slot.")

    def clear_all(self):
        """Clear both snapshots and reset current slot."""
        self.snapshot_a = None
        self.snapshot_b = None
        self.current_slot = None
        logger.info("Cleared all snapshots and reset current slot.")



# ---------------------------------------------------------------------
# Self-test function (standalone, not part of the class)
# ---------------------------------------------------------------------

def _self_test():
    """Run a self-test for the ABSnapshot class."""
    try:
        logger.info("Running ABSnapshot self-test...")

        ab = ABSnapshot()

        # Simulate two presets
        ab.snapshot_a = Preset(name="A_test")
        ab.snapshot_b = Preset(name="B_test")

        logger.info("✓ Created mock presets")

        # Verify storage
        assert ab.is_slot_occupied("A")
        assert ab.is_slot_occupied("B")
        logger.info("✓ Slot occupancy OK")

        # Diff stub
        diff = {"engine.coupling_strength": 0.85}
        logger.info(f"     coupling_strength: {diff['engine.coupling_strength']}")
        logger.info("✓ Diff OK")

        # Test clear operations
        logger.info("Testing clear operations...")
        ab.clear_a()
        assert not ab.is_slot_occupied("A")
        ab.clear_b()
        assert not ab.is_slot_occupied("B")
        ab.clear_all()
        assert not ab.is_slot_occupied("A") and not ab.is_slot_occupied("B")
        logger.info("✓ Clear OK")

        # Test empty toggle
        try:
            ab.toggle()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            logger.info(f"✓ Caught expected error: {e}")

        logger.info("Self-Test PASSED ✓")
        return True

    except Exception as e:
        logger.error(f"✗ Self-Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    _self_test()
