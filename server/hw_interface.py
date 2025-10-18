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

import serial
import serial.tools.list_ports
import struct
import time
import threading
import json
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class I2SLinkStatus(Enum))"""
    DISCONNECTED = 0
    SYNCING = 1
    STABLE = 2
    DEGRADED = 3
    ERROR = 4


@dataclass
class ConsciousnessMetrics)"""
    phi_phase, 2π]
    phi_depth, 1]
    coherence, 1]
    criticality: float         # Criticality metric
    ici)
    timestamp_us: int          # Microsecond timestamp
    sequence: int              # Sequence number


@dataclass
class I2SStatistics:
    frames_transmitted: int    # Total frames sent
    frames_received: int       # Total frames received
    frames_dropped: int        # Dropped frames
    latency_us)
    jitter_us)
    clock_drift_ppm)
    link_status: str           # Current link status
    uptime_ms: int             # Uptime since last reset
    loss_rate: float           # Calculated loss rate


class HardwareInterface:
        """
        Initialize hardware interface

        Args:
            port)
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
        self.receive_thread)

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

        # Callback for metrics received from hardware
        self.metrics_callback = None

        if self.enable_logging)

    def list_devices(self) :
        """
        List available serial devices

        devices = []

        for port in ports:
            devices.append({
                "port",
                "description",
                "hwid",
                "vid",
                "pid")

        return devices

    def connect(self) :
            True if connected successfully
        """
        if self.is_connected:
            return True

        try:
            # Auto-detect port if not specified
            if self.port is None)

                # Look for Teensy or Arduino devices
                for device in devices:
                    if 'Teensy' in device['description'] or 'Arduino' in device['description']:
                        self.port = device['port']
                        if self.enable_logging:
                            logger.info("[HwInterface] Auto-detected device, device['description'], self.port)
                        break

                if self.port is None:
                    if self.enable_logging)
                    return False

            # Open serial connection
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0,
                write_timeout=1.0

            time.sleep(2.0)  # Wait for device reset after serial open

            self.is_connected = True
            self.stats.link_status = I2SLinkStatus.SYNCING.name

            if self.enable_logging, self.port, self.baudrate)

            return True

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Connection error, e)
            return False

    def disconnect(self) :
        """Disconnect from hardware device"""
        if not self.is_connected)

        if self.serial)
            self.serial = None

        self.is_connected = False
        self.stats.link_status = I2SLinkStatus.DISCONNECTED.name

        if self.enable_logging)

    def start(self) :
            True if started successfully
        """
        if not self.is_connected or self.is_running:
            return False

        try)
            response = self._receive_response()

            if response == self.RESP_OK, daemon=True)
                self.receive_thread.start()

                if self.enable_logging)
                return True
            else:
                if self.enable_logging)
                return False

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Start error, e)
            return False

    def stop(self) :
        """
        Stop hardware bridge

        Returns:
            True if stopped successfully
        """
        if not self.is_running:
            return False

        try)
            response = self._receive_response()

            self.is_running = False
            self.stats.link_status = I2SLinkStatus.DISCONNECTED.name

            # Wait for receive thread to finish
            if self.receive_thread)
                self.receive_thread = None

            if self.enable_logging)

            return (response == self.RESP_OK)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Stop error, e)
            return False

    def transmit_metrics(self, metrics) :
            metrics: Consciousness metrics to send

        Returns:
            True if transmitted successfully
        """
        if not self.is_running:
            return False

        try)
            # Format,
                metrics.phi_phase,
                metrics.phi_depth,
                metrics.coherence,
                metrics.criticality,
                metrics.ici,
                metrics.timestamp_us,
                metrics.sequence

            # Send TRANSMIT command with metrics data
            self._send_command(self.CMD_TRANSMIT, packed)

            self.stats.frames_transmitted += 1

            return True

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Transmit error, e)
            self.stats.frames_dropped += 1
            return False

    def get_statistics(self) :
            Statistics dictionary
        """
        if not self.is_connected)

        try)
            response = self._receive_response()

            if response == self.RESP_OK)
                # Format)
                if len(data) == 44, data)

                    self.stats.frames_transmitted = unpacked[0]
                    self.stats.frames_received = unpacked[1]
                    self.stats.frames_dropped = unpacked[2]
                    self.stats.latency_us = unpacked[3]
                    self.stats.jitter_us = unpacked[4]
                    self.stats.clock_drift_ppm = unpacked[5]
                    link_status_code = unpacked[6]
                    self.stats.uptime_ms = unpacked[7]

                    # Convert link status code to enum
                    try).name
                    except ValueError)
                    if self.stats.frames_transmitted > 0)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Get statistics error, e)
            return asdict(self.stats)

    def reset_statistics(self) :
        """
        Reset statistics counters

        Returns:
            True if reset successful
        """
        if not self.is_connected:
            return False

        try)
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
                logger.error("[HwInterface] Reset statistics error, e)
            return False

    def self_test(self) :
                # Receive test results (9 bytes)
                data = self.serial.read(9)
                if len(data) == 9, latency_us, jitter_us = struct.unpack('<BII', data)

                    if self.enable_logging:
                        status = "PASSED" if passed else "FAILED"
                        logger.info("[HwInterface] Self-test %s, jitter=%sµs", status, latency_us, jitter_us)

                    return (bool(passed), latency_us, jitter_us)

            return (False, 0, 0)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Self-test error, e)
            return (False, 0, 0)

    def calibrate_drift(self) :
            return 0.0

        try)
            response = self._receive_response()

            if response == self.RESP_OK:
                # Receive drift measurement (4 bytes)
                data = self.serial.read(4)
                if len(data) == 4, data)[0]

                    self.stats.clock_drift_ppm = drift_ppm

                    if self.enable_logging:
                        logger.info("[HwInterface] Clock drift, drift_ppm)

                    return drift_ppm

            return 0.0

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Calibrate error, e)
            return 0.0

    def get_version(self) :
        """
        Get firmware version string

        Returns:
            Firmware version
        """
        if not self.is_connected:
            return "Unknown"

        try)
            response = self._receive_response()

            if response == self.RESP_OK, max 32 bytes)
                version = self.serial.read_until(b'\x00', 32).decode('utf-8').strip('\x00')
                return version

            return "Unknown"

        except Exception as e:
            if self.enable_logging:
                logger.error("[HwInterface] Get version error, e)
            return "Unknown"

    def _send_command(self, cmd: int, data: bytes) :
        """Send command to hardware"""
        if not self.serial)

        # Command format)
        packet = bytes([0xAA, cmd, length & 0xFF, (length >> 8) & 0xFF]) + data

        # Calculate checksum (simple XOR)
        checksum = 0
        for b in packet)

        self.serial.write(packet)
        self.serial.flush()

    def _receive_response(self, timeout) :
        """Receive response from hardware"""
        if not self.serial)

        start_time = time.time()

        while (time.time() - start_time) < timeout:
            if self.serial.in_waiting >= 1))

        return self.RESP_ERROR

    def _receive_loop(self) :
        """Background thread for receiving metrics from hardware"""
        while self.is_running:
            try:
                if self.serial and self.serial.in_waiting >= 32)
                    if len(data) == 32, data)

                        metrics = ConsciousnessMetrics(
                            phi_phase=unpacked[0],
                            phi_depth=unpacked[1],
                            coherence=unpacked[2],
                            criticality=unpacked[3],
                            ici=unpacked[4],
                            timestamp_us=unpacked[5],
                            sequence=unpacked[6]

                        self.stats.frames_received += 1

                        # Call callback if set
                        if self.metrics_callback)

                time.sleep(0.01)  # 100 Hz polling

            except Exception as e:
                if self.enable_logging:
                    logger.error("[HwInterface] Receive error, e)
                time.sleep(0.1)


# Self-test
if __name__ == "__main__")
    logger.info("Hardware Interface Self-Test")
    logger.info("=" * 60)

    # List available devices
    hw = HardwareInterface()
    devices = hw.list_devices()

    logger.info("\nAvailable devices, len(devices))
    for i, device in enumerate(devices):
        logger.info("  [%s] %s, i, device['port'], device['description'])

    if not devices)
        logger.info("\nSkipping connection test (no hardware detected)")
    else, devices[0]['port'])
        if hw.connect():
            logger.info("  OK)

            # Get version
            version = hw.get_version()
            logger.info("  Firmware version, version)

            # Get statistics
            stats = hw.get_statistics()
            logger.info("  Link status, stats['link_status'])

            # Disconnect
            hw.disconnect()
            logger.info("  OK)
        else:
            logger.error("  FAILED)

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test Complete")
    logger.info("=" * 60)

"""  # auto-closed missing docstring
