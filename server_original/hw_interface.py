"""
Hardware Interface - Feature 023
Python bridge for I²S hardware synchronization

Communicates with embedded I²S bridge via PySerial for:
- Consciousness metrics transmission
- Hardware link status monitoring
- Clock drift calibration
- Diagnostic logging

Requirements:
- FR-007: PySerial/PyUSB communication
- FR-008: Cluster Monitor integration
- SC-001: Round-trip latency ≤40 µs
- SC-002: Metrics loss <0.1%
- SC-003: Failover recovery <1s
"""
import logging
logger = logging.getLogger(__name__)


import serial
import serial.tools.list_ports
import struct
import time
import threading
import json
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class I2SLinkStatus(Enum):
    """Hardware link status (matches C enum)"""
    DISCONNECTED = 0
    SYNCING = 1
    STABLE = 2
    DEGRADED = 3
    ERROR = 4


@dataclass
class ConsciousnessMetrics:
    """Consciousness metrics structure (FR-003)"""
    phi_phase: float           # Φ-phase [0, 2π]
    phi_depth: float           # Φ-depth [0, 1]
    coherence: float           # Phase coherence [0, 1]
    criticality: float         # Criticality metric
    ici: float                 # Inter-Criticality Interval (ms)
    timestamp_us: int          # Microsecond timestamp
    sequence: int              # Sequence number


@dataclass
class I2SStatistics:
    """Hardware statistics (SC-001, SC-002)"""
    frames_transmitted: int    # Total frames sent
    frames_received: int       # Total frames received
    frames_dropped: int        # Dropped frames
    latency_us: int            # Round-trip latency (µs)
    jitter_us: int             # Latency jitter (µs)
    clock_drift_ppm: float     # Clock drift (parts per million)
    link_status: str           # Current link status
    uptime_ms: int             # Uptime since last reset
    loss_rate: float           # Calculated loss rate


class HardwareInterface:
    """
    Hardware I²S Bridge Interface

    Provides Python API for communicating with embedded I²S bridge
    via serial/USB connection.
    """

    # Protocol constants
    CMD_INIT = 0x01
    CMD_START = 0x02
    CMD_STOP = 0x03
    CMD_TRANSMIT = 0x04
    CMD_GET_STATS = 0x05
    CMD_RESET_STATS = 0x06
    CMD_SELF_TEST = 0x07
    CMD_CALIBRATE = 0x08
    CMD_GET_VERSION = 0x09

    RESP_OK = 0x00
    RESP_ERROR = 0xFF

    def __init__(self, port: Optional[str]: Any = None, baudrate: int: Any = 115200, enable_logging: bool: Any = True) -> None:
        """
        Initialize hardware interface

        Args:
            port: Serial port path (auto-detect if None)
            baudrate: Serial baud rate
            enable_logging: Enable diagnostic logging
        """
        self.port = port
        self.baudrate = baudrate
        self.enable_logging = enable_logging

        self.serial: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_running = False

        # Background thread for receiving data
        self.receive_thread: Optional[threading.Thread] = None
        self.receive_lock = threading.Lock()

        # Statistics
        self.stats = I2SStatistics(
            frames_transmitted=0,
            frames_received=0,
            frames_dropped=0,
            latency_us=0,
            jitter_us=0,
            clock_drift_ppm=0.0,
            link_status=I2SLinkStatus.DISCONNECTED.name,
            uptime_ms=0,
            loss_rate=0.0
        )

        # Callback for metrics received from hardware
        self.metrics_callback = None

        if self.enable_logging:
            logger.info("[HwInterface] Initialized")

    def list_devices(self) -> List[Dict]:
        """
        List available serial devices

        Returns:
            List of device info dictionaries
        """
        ports = serial.tools.list_ports.comports()
        devices = []

        for port in ports:
            devices.append({
                "port": port.device,
                "description": port.description,
                "hwid": port.hwid,
                "vid": port.vid,
                "pid": port.pid
            })

        return devices

    def connect(self) -> bool:
        """
        Connect to hardware device (FR-007)

        Returns:
            True if connected successfully
        """
        if self.is_connected:
            return True

        try:
            # Auto-detect port if not specified
            if self.port is None:
                devices = self.list_devices()

                # Look for Teensy or Arduino devices
                for device in devices:
                    if 'Teensy' in device['description'] or 'Arduino' in device['description']:
                        self.port = device['port']
                        if self.enable_logging:
                            logger.info("[HwInterface] Auto-detected device: %s on %s", device['description'], self.port)
                        break

                if self.port is None:
                    if self.enable_logging:
                        logger.info("[HwInterface] No compatible device found")
                    return False

            # Open serial connection
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0,
                write_timeout=1.0
            )

            time.sleep(2.0)  # Wait for device reset after serial open

            self.is_connected = True
            self.stats.link_status = I2SLinkStatus.SYNCING.name

            if self.enable_logging:
                logger.info("[HwInterface] Connected to %s @ %s baud", self.port, self.baudrate)

            return True

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Connection error: %s", e)
            return False

    def disconnect(self) -> Any:
        """Disconnect from hardware device"""
        if not self.is_connected:
            return

        self.stop()

        if self.serial:
            self.serial.close()
            self.serial = None

        self.is_connected = False
        self.stats.link_status = I2SLinkStatus.DISCONNECTED.name

        if self.enable_logging:
            logger.info("[HwInterface] Disconnected")

    def start(self) -> bool:
        """
        Start hardware bridge (FR-002)

        Returns:
            True if started successfully
        """
        if not self.is_connected or self.is_running:
            return False

        try:
            # Send START command
            self._send_command(self.CMD_START)
            response = self._receive_response()

            if response == self.RESP_OK:
                self.is_running = True
                self.stats.link_status = I2SLinkStatus.STABLE.name

                # Start receive thread
                self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
                self.receive_thread.start()

                if self.enable_logging:
                    logger.info("[HwInterface] Hardware bridge started")
                return True
            else:
                if self.enable_logging:
                    logger.error("[HwInterface] Start command failed")
                return False

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Start error: %s", e)
            return False

    def stop(self) -> bool:
        """
        Stop hardware bridge

        Returns:
            True if stopped successfully
        """
        if not self.is_running:
            return False

        try:
            # Send STOP command
            self._send_command(self.CMD_STOP)
            response = self._receive_response()

            self.is_running = False
            self.stats.link_status = I2SLinkStatus.DISCONNECTED.name

            # Wait for receive thread to finish
            if self.receive_thread:
                self.receive_thread.join(timeout=2.0)
                self.receive_thread = None

            if self.enable_logging:
                logger.info("[HwInterface] Hardware bridge stopped")

            return (response == self.RESP_OK)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Stop error: %s", e)
            return False

    def transmit_metrics(self, metrics: ConsciousnessMetrics) -> bool:
        """
        Transmit consciousness metrics to hardware (FR-003)

        Args:
            metrics: Consciousness metrics to send

        Returns:
            True if transmitted successfully
        """
        if not self.is_running:
            return False

        try:
            # Pack metrics into binary format (32-byte struct)
            # Format: 5 floats + 2 uint32
            packed = struct.pack(
                '<fffffII',
                metrics.phi_phase,
                metrics.phi_depth,
                metrics.coherence,
                metrics.criticality,
                metrics.ici,
                metrics.timestamp_us,
                metrics.sequence
            )

            # Send TRANSMIT command with metrics data
            self._send_command(self.CMD_TRANSMIT, packed)

            self.stats.frames_transmitted += 1

            return True

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Transmit error: %s", e)
            self.stats.frames_dropped += 1
            return False

    def get_statistics(self) -> Dict:
        """
        Get hardware statistics (SC-001, SC-002)

        Returns:
            Statistics dictionary
        """
        if not self.is_connected:
            return asdict(self.stats)

        try:
            # Send GET_STATS command
            self._send_command(self.CMD_GET_STATS)
            response = self._receive_response()

            if response == self.RESP_OK:
                # Receive statistics packet (44 bytes)
                # Format: 3 uint64 + 2 uint32 + 1 float + 1 uint8 + 1 uint32
                data = self.serial.read(44)
                if len(data) == 44:
                    unpacked = struct.unpack('<QQQIIfBI', data)

                    self.stats.frames_transmitted = unpacked[0]
                    self.stats.frames_received = unpacked[1]
                    self.stats.frames_dropped = unpacked[2]
                    self.stats.latency_us = unpacked[3]
                    self.stats.jitter_us = unpacked[4]
                    self.stats.clock_drift_ppm = unpacked[5]
                    link_status_code = unpacked[6]
                    self.stats.uptime_ms = unpacked[7]

                    # Convert link status code to enum
                    try:
                        self.stats.link_status = I2SLinkStatus(link_status_code).name
                    except ValueError:
                        self.stats.link_status = I2SLinkStatus.ERROR.name

                    # Calculate loss rate (SC-002)
                    if self.stats.frames_transmitted > 0:
                        self.stats.loss_rate = self.stats.frames_dropped / self.stats.frames_transmitted

            return asdict(self.stats)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Get statistics error: %s", e)
            return asdict(self.stats)

    def reset_statistics(self) -> bool:
        """
        Reset statistics counters

        Returns:
            True if reset successful
        """
        if not self.is_connected:
            return False

        try:
            self._send_command(self.CMD_RESET_STATS)
            response = self._receive_response()

            if response == self.RESP_OK:
                # Reset local stats
                self.stats.frames_transmitted = 0
                self.stats.frames_received = 0
                self.stats.frames_dropped = 0
                self.stats.uptime_ms = 0
                self.stats.loss_rate = 0.0

                return True

            return False

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Reset statistics error: %s", e)
            return False

    def self_test(self) -> Tuple[bool, int, int]:
        """
        Run hardware self-test (FR-010, SC-001)

        Returns:
            Tuple of (passed, latency_us, jitter_us)
        """
        if not self.is_connected:
            return (False, 0, 0)

        try:
            # Send SELF_TEST command
            self._send_command(self.CMD_SELF_TEST)
            response = self._receive_response()

            if response == self.RESP_OK:
                # Receive test results (9 bytes: 1 bool + 2 uint32)
                data = self.serial.read(9)
                if len(data) == 9:
                    passed, latency_us, jitter_us = struct.unpack('<BII', data)

                    if self.enable_logging:
                        status = "PASSED" if passed else "FAILED"
                        logger.info("[HwInterface] Self-test %s: latency=%sµs, jitter=%sµs", status, latency_us, jitter_us)

                    return (bool(passed), latency_us, jitter_us)

            return (False, 0, 0)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Self-test error: %s", e)
            return (False, 0, 0)

    def calibrate_drift(self) -> float:
        """
        Calibrate clock drift (FR-005)

        Returns:
            Measured drift in parts per million (ppm)
        """
        if not self.is_connected:
            return 0.0

        try:
            # Send CALIBRATE command
            self._send_command(self.CMD_CALIBRATE)
            response = self._receive_response()

            if response == self.RESP_OK:
                # Receive drift measurement (4 bytes: float)
                data = self.serial.read(4)
                if len(data) == 4:
                    drift_ppm = struct.unpack('<f', data)[0]

                    self.stats.clock_drift_ppm = drift_ppm

                    if self.enable_logging:
                        logger.info("[HwInterface] Clock drift: %s ppm", drift_ppm:.3f)

                    return drift_ppm

            return 0.0

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Calibrate error: %s", e)
            return 0.0

    def get_version(self) -> str:
        """
        Get firmware version string

        Returns:
            Firmware version
        """
        if not self.is_connected:
            return "Unknown"

        try:
            # Send GET_VERSION command
            self._send_command(self.CMD_GET_VERSION)
            response = self._receive_response()

            if response == self.RESP_OK:
                # Receive version string (null-terminated, max 32 bytes)
                version = self.serial.read_until(b'\x00', 32).decode('utf-8').strip('\x00')
                return version

            return "Unknown"

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Get version error: %s", e)
            return "Unknown"

    def _send_command(self, cmd: int: Any, data: bytes: List = b'') -> None:
        """Send command to hardware"""
        if not self.serial:
            raise RuntimeError("Serial not connected")

        # Command format: [0xAA] [CMD] [LEN_L] [LEN_H] [DATA...] [CHECKSUM]
        length = len(data)
        packet = bytes([0xAA, cmd, length & 0xFF, (length >> 8) & 0xFF]) + data

        # Calculate checksum (simple XOR)
        checksum = 0
        for b in packet:
            checksum ^= b

        packet += bytes([checksum])

        self.serial.write(packet)
        self.serial.flush()

    def _receive_response(self, timeout: float = 1.0) -> int:
        """Receive response from hardware"""
        if not self.serial:
            raise RuntimeError("Serial not connected")

        start_time = time.time()

        while (time.time() - start_time) < timeout:
            if self.serial.in_waiting >= 1:
                return ord(self.serial.read(1))

        return self.RESP_ERROR

    def _receive_loop(self) -> None:
        """Background thread for receiving metrics from hardware"""
        while self.is_running:
            try:
                if self.serial and self.serial.in_waiting >= 32:  # Size of ConsciousnessMetrics
                    # Read metrics packet
                    data = self.serial.read(32)
                    if len(data) == 32:
                        # Unpack metrics
                        unpacked = struct.unpack('<fffffII', data)

                        metrics = ConsciousnessMetrics(
                            phi_phase=unpacked[0],
                            phi_depth=unpacked[1],
                            coherence=unpacked[2],
                            criticality=unpacked[3],
                            ici=unpacked[4],
                            timestamp_us=unpacked[5],
                            sequence=unpacked[6]
                        )

                        self.stats.frames_received += 1

                        # Call callback if set
                        if self.metrics_callback:
                            self.metrics_callback(metrics)

                time.sleep(0.01)  # 100 Hz polling

            except Exception as e:
                if self.enable_logging:
                    logger.error("[HwInterface] Receive error: %s", e)
                time.sleep(0.1)


# Self-test
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Hardware Interface Self-Test")
    logger.info("=" * 60)

    # List available devices
    hw = HardwareInterface()
    devices = hw.list_devices()

    logger.info("\nAvailable devices: %s", len(devices))
    for i, device in enumerate(devices):
        logger.info("  [%s] %s: %s", i, device['port'], device['description'])

    if not devices:
        logger.info("  No devices found")
        logger.info("\nSkipping connection test (no hardware detected)")
    else:
        # Try to connect to first device
        logger.info("\nAttempting connection to %s...", devices[0]['port'])
        if hw.connect():
            logger.info("  OK: Connected")

            # Get version
            version = hw.get_version()
            logger.info("  Firmware version: %s", version)

            # Get statistics
            stats = hw.get_statistics()
            logger.info("  Link status: %s", stats['link_status'])

            # Disconnect
            hw.disconnect()
            logger.info("  OK: Disconnected")
        else:
            logger.error("  FAILED: Could not connect")

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test Complete")
    logger.info("=" * 60)
