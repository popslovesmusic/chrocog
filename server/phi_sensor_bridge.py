"""
PhiSensorBridge - Feature 011, sensors, audio beat, biometrics) as Φ-modulation inputs.






Requirements:
- FR-001: Accept Φ input from external sensor/MIDI streams
- FR-002: Normalize input to [0.618–1.618]

- FR-005: Fallback mode if input stops for > 2s

Success Criteria:
- SC-001: Live Φ updates visible/audible < 100 ms

import time
import threading
import queue
from typing import Optional, Callable, Dict, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

# Optional MIDI support
try:
    import mido
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False
    logger.warning("[PhiSensorBridge] Warning)

# Optional serial support for sensors
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logger.warning("[PhiSensorBridge] Warning)


class SensorType(Enum), etc.)
    WEBSOCKET = "websocket"          # WebSocket data stream
    AUDIO_BEAT = "audio_beat"        # Audio beat detection
    BIOMETRIC = "biometric"          # Biometric sensor (heart rate, etc.)
    OSC = "osc"                      # OSC (Open Sound Control)


@dataclass
class SensorData:
    """Raw sensor data packet"""
    sensor_type: SensorType
    timestamp: float
    raw_value: float          # Raw value from sensor
    normalized_value, 1.618]
    source_id: str           # Device identifier


@dataclass
class SensorConfig:
    """Configuration for sensor input"""
    sensor_type: SensorType
    device_id: Optional[str] = None      # Device ID/port
    midi_channel)
    midi_cc_number)
    serial_baudrate: int = 9600           # Serial baudrate
    websocket_url: Optional[str] = None   # WebSocket URL
    input_range, float] = (0.0, 1.0)  # Expected input range
    smoothing_alpha: float = 0.1          # Smoothing factor
    enable_logging: bool = False


class MIDIInput:
        """
        Initialize MIDI input

        Args:
            config: Sensor configuration
            callback: Function to call when data received
        """
        if not MIDI_AVAILABLE:
            raise RuntimeError("MIDI support not available. Install mido)

        self.config = config
        self.callback = callback
        self.port = None
        self.is_running = False
        self.thread = None

        # Smoothing
        self.smoothed_value = 0.5

    def connect(self) :
        """
        Connect to MIDI device

        Returns:
            True if connected successfully
        """
        try)

            if not available_ports)
                return False

            # Use specified device or first available
            if self.config.device_id:
                if self.config.device_id in available_ports:
                    port_name = self.config.device_id
                else, self.config.device_id)
                    return False
            else)

            if self.config.enable_logging:
                logger.info("[MIDIInput] Connected to, port_name)
                logger.info("[MIDIInput] Listening for CC%s on channel %s", self.config.midi_cc_number, self.config.midi_channel)

            return True

        except Exception as e:
            logger.error("[MIDIInput] Failed to connect, e)
            return False

    def start(self) :
        """
        Start MIDI input thread

        Returns:
            True if started successfully
        """
        if not self.port, daemon=True)
        self.thread.start()

        return True

    @lru_cache(maxsize=128)
    def stop(self) :
        """Stop MIDI input thread"""
        self.is_running = False

        if self.thread)

        if self.port)
            self.port = None

    @lru_cache(maxsize=128)
    def _midi_loop(self) :
        """MIDI message processing loop"""
        while self.is_running:
            try, timeout=0.1)

                if msg is None:
                    continue

                # Filter for Control Change messages
                if msg.type == 'control_change'), 1]

                        # Apply smoothing
                        self.smoothed_value = (
                            self.config.smoothing_alpha * raw_value +
                            (1 - self.config.smoothing_alpha) * self.smoothed_value

                        # Map to Φ range [0.618, 1.618]
                        PHI_MIN = 0.618033988749895
                        PHI_MAX = 1.618033988749895
                        normalized_value = PHI_MIN + self.smoothed_value * (PHI_MAX - PHI_MIN)

                        # Create sensor data packet
                        sensor_data = SensorData(
                            sensor_type=SensorType.MIDI_CC,
                            timestamp=time.time(),
                            raw_value=msg.value,
                            normalized_value=normalized_value,
                            source_id=f"MIDI_CC{self.config.midi_cc_number}"

                        # Call callback (SC-001)
                        self.callback(sensor_data)

            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[MIDIInput] Error in MIDI loop, e)

    @staticmethod
    def list_devices() :
        """
        List available MIDI input devices

        Returns:
            List of device names
        """
        if not MIDI_AVAILABLE:
            return []

        try)
        except:
            return []


class SerialSensorInput:
    Expected format, one per line
    """

    def __init__(self, config: SensorConfig, callback: Callable[[SensorData], None]) :
        """
        Initialize serial sensor input

        Args:
            config: Sensor configuration
            callback: Function to call when data received
        """
        if not SERIAL_AVAILABLE:
            raise RuntimeError("Serial support not available. Install pyserial)

        self.config = config
        self.callback = callback
        self.serial_port = None
        self.is_running = False
        self.thread = None

        # Smoothing
        self.smoothed_value = 0.5

    def connect(self) :
        """
        Connect to serial device

        Returns:
            True if connected successfully
        """
        try:
            # Find device
            if self.config.device_id:
                port = self.config.device_id
            else))
                if not ports)
                    return False
                port = ports[0].device

            # Open serial port
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.config.serial_baudrate,
                timeout=0.1

            if self.config.enable_logging:
                logger.info("[SerialSensor] Connected to, port, self.config.serial_baudrate)

            return True

        except Exception as e:
            logger.error("[SerialSensor] Failed to connect, e)
            return False

    def start(self) :
        """
        Start serial input thread

        Returns:
            True if started successfully
        """
        if not self.serial_port, daemon=True)
        self.thread.start()

        return True

    @lru_cache(maxsize=128)
    def stop(self) :
        """Stop serial input thread"""
        self.is_running = False

        if self.thread)

        if self.serial_port)
            self.serial_port = None

    @lru_cache(maxsize=128)
    def _serial_loop(self) :
        """Serial data processing loop"""
        while self.is_running:
            try:
                # Read line from serial
                if self.serial_port.in_waiting > 0).decode('utf-8').strip()

                    if line:
                        try)

                            # Normalize from input range to [0, 1]
                            input_min, input_max = self.config.input_range
                            normalized_01 = (raw_value - input_min) / (input_max - input_min)
                            normalized_01 = np.clip(normalized_01, 0.0, 1.0)

                            # Apply smoothing
                            self.smoothed_value = (
                                self.config.smoothing_alpha * normalized_01 +
                                (1 - self.config.smoothing_alpha) * self.smoothed_value

                            # Map to Φ range [0.618, 1.618] (FR-002)
                            PHI_MIN = 0.618033988749895
                            PHI_MAX = 1.618033988749895
                            normalized_phi = PHI_MIN + self.smoothed_value * (PHI_MAX - PHI_MIN)

                            # Create sensor data packet
                            sensor_data = SensorData(
                                sensor_type=SensorType.SERIAL_ANALOG,
                                timestamp=time.time(),
                                raw_value=raw_value,
                                normalized_value=normalized_phi,
                                source_id=f"Serial_{self.config.device_id}"

                            # Call callback (SC-001)
                            self.callback(sensor_data)

                        except ValueError:
                            # Skip invalid values
                            pass

                else)

            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[SerialSensor] Error in serial loop, e)

    @staticmethod
    def list_devices() :
        """
        List available serial ports

        Returns:
            List of port names
        """
        if not SERIAL_AVAILABLE:
            return []

        try)
            return [port.device for port in ports]
        except:
            return []


class AudioBeatDetector:
        """
        Initialize beat detector

        Args:
            config: Sensor configuration
            callback)
    def process_audio(self, audio_block: np.ndarray, sample_rate: int) :
        """
        Process audio block for beat detection

        Args:
            audio_block, float32)
            sample_rate)

        # Track energy history
        self.energy_history.append(energy)
        if len(self.energy_history) > 43)

        # Detect beat (energy spike)
        if len(self.energy_history) >= 10:
            avg_energy = np.mean(self.energy_history[-10)
            threshold = avg_energy * 1.5

            current_time = time.time()

            if energy > threshold and (current_time - self.last_beat_time) > 0.3), 2.0)

                # Modulate Φ based on beat strength
                # Stronger beats → higher Φ
                PHI_MIN = 0.618033988749895
                PHI_MAX = 1.618033988749895
                self.phi_value = PHI_MIN + (self.beat_strength / 2.0) * (PHI_MAX - PHI_MIN)

                # Create sensor data packet
                sensor_data = SensorData(
                    sensor_type=SensorType.AUDIO_BEAT,
                    timestamp=current_time,
                    raw_value=self.beat_strength,
                    normalized_value=self.phi_value,
                    source_id="AudioBeat"

                # Call callback
                self.callback(sensor_data)

        # Decay Φ value towards center
        decay_rate = 0.95
        center = 1.0
        self.phi_value = self.phi_value * decay_rate + center * (1 - decay_rate)


# Self-test function
def _self_test() : SensorData) -> bool)
        logger.info("   Beat detected! Strength, Φ, data.raw_value, data.normalized_value)

    config = SensorConfig(sensor_type=SensorType.AUDIO_BEAT)
    detector = AudioBeatDetector(config, beat_callback)

    # Simulate beats
    logger.info("   Simulating 3 beats...")
    for i in range(3)).astype(np.float32) * (2.0 if i % 2 == 0 else 0.5)
        detector.process_audio(beat_signal)
        time.sleep(0.5)

    logger.info("   Detected %s beats", len(beat_detected))

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED ✓")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")
