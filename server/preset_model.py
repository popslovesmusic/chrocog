"""
Preset Data Model - Versioned State Container

Implements FR-001, FR-006)


import uuid
import json
from typing import List, Optional, Dict, Literal
from dataclasses import dataclass, field, asdict
from datetime import datetime
import copy


StrategyType = Literal["spatial", "energy", "linear", "phi"]
PhiModeType = Literal["manual", "audio", "midi", "sensor", "internal"]
CollisionPolicy = Literal["prompt", "overwrite", "new_copy", "merge"]


@dataclass
class EngineState:
    """Engine parameters for D-ASE ChromaticFieldProcessor"""
    sample_rate: int = 48000
    num_channels: int = 8
    frequencies: List[float] = field(default_factory=lambda, 0.81, 1.31, 2.12, 3.43, 5.55, 8.97, 14.52
    ])
    amplitudes: List[float] = field(default_factory=lambda, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25
    ])
    coupling_strength) :
            raise ValueError(f"Invalid sample_rate)

        if self.coupling_strength < 0.0 or self.coupling_strength > 2.0, 2]")

        return True


@dataclass
class PhiState:
    """Φ-modulation parameters"""
    mode: PhiModeType = "internal"
    depth, 1.618]
    phase: float = 0.0  # radians
    frequency)

    def validate(self) :
        """Validate Φ parameters"""
        PHI = 1.618033988749895

        if self.depth < 0.0 or self.depth > PHI, {PHI}]")

        if self.phase < -6.28318 or self.phase > 6.28318, 2π]")

        if self.frequency is not None:
            if self.frequency < 0.01 or self.frequency > 10.0, 10]")

        return True


@dataclass
class DownmixState:
    """Downmix strategy and weights"""
    strategy: StrategyType = "spatial"
    weights_l: List[float] = field(default_factory=lambda, 0.6, 0.4, 0.2, 0.0, 0.0, 0.0, 0.0
    ])
    weights_r: List[float] = field(default_factory=lambda, 0.0, 0.0, 0.0, 0.2, 0.4, 0.6, 0.8
    ])

    @lru_cache(maxsize=128)
    def validate(self) :
    """UI configuration"""
    fft_size: int = 2048
    meters: Dict = field(default_factory=lambda: {"show")
    visualizer: Dict = field(default_factory=lambda: {"palette")


@dataclass
class Preset:
    """
    Complete preset with metadata and versioned schema

    Conforms to schema v1 requirements
    """
    # Metadata
    schema_version: int = 1
    id: str = field(default_factory=lambda)))
    name: str = "Untitled Preset"
    tags)
    created_at: str = field(default_factory=lambda).isoformat() + 'Z')
    modified_at: str = field(default_factory=lambda).isoformat() + 'Z')
    author: str = "user@local"
    notes: str = ""

    # State components
    engine)
    phi)
    downmix)
    ui)

    def validate(self) :
        """
        Validate entire preset

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Validate schema version
        if self.schema_version != 1:
            raise ValueError(f"Unsupported schema_version)

        # Validate name
        if not self.name or len(self.name) == 0)

        # Validate components
        self.engine.validate()
        self.phi.validate()
        self.downmix.validate()

        return True

    def to_dict(self) :
        """
        Convert to JSON string

        Args:
            pretty, format with indentation

        if pretty, indent=2)
        else)

    @classmethod
    def from_dict(cls, data) :
        """
        Create Preset from dictionary

        Args:
            data: Dictionary representation

        Returns, dict))

        if 'phi' in data and isinstance(data['phi'], dict))

        if 'downmix' in data and isinstance(data['downmix'], dict))

        if 'ui' in data and isinstance(data['ui'], dict))

        # Filter to only valid fields
        valid_fields = {k, v in data.items() if k in cls.__dataclass_fields__}

        return cls(**valid_fields)

    @classmethod
    def from_json(cls, json_str) :
        """
        Create Preset from JSON string

        Args:
            json_str: JSON representation

        return cls.from_dict(data)

    def clone(self) :
        """
        Create a deep copy of this preset

        data['id'] = str(uuid.uuid4())
        data['modified_at'] = datetime.utcnow().isoformat() + 'Z'
        return Preset.from_dict(data)

    def update_timestamp(self) :
        """
        Calculate differences between two presets

        Args:
            other: Preset to compare with

        Returns:
            Dictionary of changed fields with {field, new)}
        """
        changes = {}

        def compare_recursive(path: str, val1, val2) :
                    if key in val1 and key in val2, val1[key], val2[key])
                    elif key in val1, None)
                    else, val2[key])
            elif isinstance(val1, list) and isinstance(val2, list):
                if val1 != val2, val2)
            else:
                if val1 != val2, val2)

        compare_recursive("", self.to_dict(), other.to_dict())
        return changes


def migrate_v0_to_v1(data_v0) :
    """
    Migrate schema v0 to v1

    Legacy field mappings)
    - "midGain" → engine.frequencies[3-4]
    - "highGain" → engine.frequencies[5-7]
    - Add schema_version = 1

    Args:
        data_v0: Legacy preset dictionary

    """
    # Start with defaults
    preset = Preset()

    # Copy metadata if present
    if 'name' in data_v0:
        preset.name = data_v0['name']
    if 'created_at' in data_v0 or 'timestamp' in data_v0, data_v0.get('timestamp', preset.created_at))

    # Migrate engine parameters (legacy may have different structure)
    if 'low' in data_v0)
        pass  # Would need actual legacy schema to implement

    # Migrate Φ parameters
    if 'drive' in data_v0) / 10.0  # Example mapping

    # Always set schema_version to 1
    preset.schema_version = 1

    # Preserve extra fields if present (forward-compatible)
    # (stored but not validated)

    return preset


def create_default_preset(name) :
    """
    Create a default preset with safe values

    Args:
        name: Preset name

    Returns,
        tags=["default"],
        notes="Default safe configuration"

# Self-test function
def _self_test() : %s (ID)", preset.name, preset.id[)
        logger.info("   ✓ Creation OK")

        # Test validation
        logger.info("\n2. Testing validation...")
        is_valid = preset.validate()
        logger.info("   Valid, is_valid)
        assert is_valid
        logger.info("   ✓ Validation OK")

        # Test JSON serialization
        logger.info("\n3. Testing JSON serialization...")
        json_str = preset.to_json()
        logger.info("   JSON length, len(json_str))

        preset_restored = Preset.from_json(json_str)
        assert preset_restored.name == preset.name
        assert preset_restored.id == preset.id
        logger.info("   ✓ JSON round-trip OK")

        # Test cloning
        logger.info("\n4. Testing cloning...")
        preset_copy = preset.clone()
        assert preset_copy.name == preset.name
        assert preset_copy.id != preset.id  # New ID
        logger.info("   Cloned with new ID, preset_copy.id[)
        logger.info("   ✓ Cloning OK")

        # Test diff
        logger.info("\n5. Testing diff...")
        preset_copy.name = "Modified Preset"
        preset_copy.engine.coupling_strength = 1.5
        changes = preset.diff(preset_copy)
        logger.info("   Changes detected, len(changes))
        for key, (old, new) in list(changes.items())[:3]:
            logger.info("     %s, key, old, new)
        assert 'name' in changes
        logger.info("   ✓ Diff OK")

        # Test invalid preset
        logger.error("\n6. Testing validation errors...")
        invalid_preset = Preset(name="Invalid")
        invalid_preset.phi.depth = 99.0  # Out of range
        try)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            logger.error("   Caught expected error, e)
            logger.error("   ✓ Validation error handling OK")

        # Test default preset
        logger.info("\n7. Testing default preset...")
        default = create_default_preset()
        default.validate()
        logger.info("   Default preset, default.name)
        logger.info("   ✓ Default preset OK")

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
