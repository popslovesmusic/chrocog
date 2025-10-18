"""
Hybrid Analog-DSP Node Bridge - Feature 024
Python interface for hybrid analog/digital processing node

Communicates with hybrid node hardware via PySerial for, coherence, spectral analysis)


- Calibration routines

Requirements:
- FR-005: Interface via PySerial or PyUSB
- FR-006: Integrate with metrics bus /ws/metrics
- FR-007: Safety monitoring and emergency shutdown
- FR-008: Calibration routine
- FR-009: Cluster Monitor integration

Success Criteria:
- SC-001: Total loop latency ≤2 ms
- SC-002: Modulation fidelity >95%
- SC-003, drift <0.5%
"""
from functools import lru_cache
import logging
logger = logging.getLogger(__name__)


import serial
import serial.tools.list_ports
import struct
import time
import threading
import json
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from enum import Enum


class HybridInterfaceType(Enum)):
    """Safety status"""
    OK = 0
    VOLTAGE_CLAMP = 1
    TEMP_WARNING = 2
    TEMP_CRITICAL = 3
    ADC_OVERLOAD = 4
    FAULT = 5


@dataclass
class AnalogMetrics)"""
    rms_level: float          # RMS signal level
    peak_level: float         # Peak signal level
    dc_offset: float          # DC offset
    thd)
    snr_db)
    is_overloaded: bool       # Overload flag


@dataclass
class DSPMetrics)"""
    ici)
    coherence, 1]
    criticality: float        # Criticality metric
    spectral_centroid)
    spectral_flux: float      # Spectral flux
    zero_crossing_rate: float # Zero-crossing rate
    timestamp_us: int         # Microsecond timestamp


@dataclass
class ControlVoltage)"""
    cv1) - VCA depth
    cv2) - VCA rate
    phi_phase, 2π]
    phi_depth, 1]


@dataclass
class SafetyTelemetry)"""
    status: str               # Safety status
    temperature)
    voltage_out: List[float]  # Output voltages
    overload_count: int       # Overload event count
    clamp_count: int          # Voltage clamp count
    thermal_warning: bool     # Thermal warning flag


@dataclass
class CalibrationData)"""
    adc_gain: List[float]     # ADC gain correction per channel
    adc_offset: List[float]   # ADC offset correction per channel
    dac_gain: List[float]     # DAC gain correction per channel
    dac_offset: List[float]   # DAC offset correction per channel
    adc_latency_us)
    dsp_latency_us)
    dac_latency_us)
    total_latency_us) (SC-001)
    calibration_timestamp: int # Calibration timestamp
    is_calibrated: bool       # Calibration valid


@dataclass
class NodeStatistics)"""
    frames_processed: int     # Total frames processed
    frames_dropped: int       # Dropped frames
    cpu_load)
    buffer_utilization)
    uptime_ms)
    drift_ppm)
    modulation_fidelity) (SC-002)


class HybridBridge:
        """
        Initialize hybrid bridge

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

        # Background thread for metrics streaming
        self.metrics_thread)
        self.metrics_callback = None

        # Current state
        self.current_mode = HybridNodeMode.HYBRID
        self.analog_metrics = None
        self.dsp_metrics = None
        self.safety_telemetry = None
        self.calibration = None
        self.statistics = None

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

                # Look for Teensy, Arduino, or Raspberry Pi devices
                for device in devices)
                    if 'teensy' in desc or 'arduino' in desc or 'raspberry' in desc:
                        self.port = device['port']
                        if self.enable_logging:
                            logger.info("[HybridBridge] Auto-detected, device['description'], self.port)
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

            time.sleep(2.0)  # Wait for device reset

            self.is_connected = True

            if self.enable_logging, self.port, self.baudrate)

            return True

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Connection error, e)
            return False

    @lru_cache(maxsize=128)
    def disconnect(self) :
        """Disconnect from hybrid node"""
        if not self.is_connected)

        if self.serial)
            self.serial = None

        self.is_connected = False

        if self.enable_logging)

    @lru_cache(maxsize=128)
    def start(self) :
        """
        Start hybrid node processing

        Returns:
            True if started successfully
        """
        if not self.is_connected or self.is_running:
            return False

        try)
            response = self._receive_response()

            if response == self.RESP_OK, daemon=True)
                self.metrics_thread.start()

                if self.enable_logging)
                return True
            else:
                if self.enable_logging)
                return False

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Start error, e)
            return False

    @lru_cache(maxsize=128)
    def stop(self) :
        """
        Stop hybrid node processing

        Returns:
            True if stopped successfully
        """
        if not self.is_running:
            return False

        try)
            response = self._receive_response()

            self.is_running = False

            # Wait for metrics thread to finish
            if self.metrics_thread)
                self.metrics_thread = None

            if self.enable_logging)

            return (response == self.RESP_OK)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Stop error, e)
            return False

    def get_dsp_metrics(self) :
            DSP metrics dictionary
        """
        if not self.is_connected:
            return {}

        try)
            response = self._receive_response()

            if response == self.RESP_OK)
                # Format)
                if len(data) == 28, data)

                    self.dsp_metrics = DSPMetrics(
                        ici=unpacked[0],
                        coherence=unpacked[1],
                        criticality=unpacked[2],
                        spectral_centroid=unpacked[3],
                        spectral_flux=unpacked[4],
                        zero_crossing_rate=unpacked[5],
                        timestamp_us=unpacked[6]

                    return asdict(self.dsp_metrics)

            return {}

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Get DSP metrics error, e)
            return {}

    def get_safety(self) :
            Safety telemetry dictionary
        """
        if not self.is_connected:
            return {}

        try)
            response = self._receive_response()

            if response == self.RESP_OK)
                # Format)
                if len(data) == 26, data)

                    self.safety_telemetry = SafetyTelemetry(
                        status=HybridSafetyStatus(unpacked[0]).name,
                        temperature=unpacked[1],
                        voltage_out=[unpacked[2], unpacked[3], unpacked[4], unpacked[5]],
                        overload_count=unpacked[6],
                        clamp_count=unpacked[7],
                        thermal_warning=bool(unpacked[8])

                    return asdict(self.safety_telemetry)

            return {}

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Get safety error, e)
            return {}

    def set_preamp_gain(self, gain) :
            gain, 1.0 = 0dB)

        Returns:
            True if set successfully
        """
        if not self.is_connected:
            return False

        try, gain)
            self._send_command(self.CMD_SET_PREAMP_GAIN, packed)
            response = self._receive_response()

            return (response == self.RESP_OK)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Set preamp gain error, e)
            return False

    def set_control_voltage(self, cv) :
            cv: Control voltage structure

        Returns:
            True if set successfully
        """
        if not self.is_connected:
            return False

        try)
            packed = struct.pack('<ffff', cv.cv1, cv.cv2, cv.phi_phase, cv.phi_depth)
            self._send_command(self.CMD_SET_CONTROL_VOLTAGE, packed)
            response = self._receive_response()

            return (response == self.RESP_OK)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Set control voltage error, e)
            return False

    def calibrate(self) :
            return None

        try:
            if self.enable_logging)...")

            self._send_command(self.CMD_CALIBRATE)
            response = self._receive_response()

            if response == self.RESP_OK)
                # Wait longer for calibration to complete
                time.sleep(5.0)

                # Read calibration data
                # This is a simplified version; actual implementation would
                # receive the full CalibrationData structure
                data = self.serial.read(64)  # Approximate size
                if len(data) >= 16, data[0)[0]
                    is_calibrated = struct.unpack('<B', data[4)[0]

                    self.calibration = CalibrationData(
                        adc_gain=[1.0, 1.0],
                        adc_offset=[0.0, 0.0],
                        dac_gain=[1.0, 1.0, 1.0, 1.0],
                        dac_offset=[0.0, 0.0, 0.0, 0.0],
                        adc_latency_us=total_latency_us // 3,
                        dsp_latency_us=total_latency_us // 3,
                        dac_latency_us=total_latency_us // 3,
                        total_latency_us=total_latency_us,
                        calibration_timestamp=int(time.time()),
                        is_calibrated=bool(is_calibrated)

                    if self.enable_logging)
                        logger.info("  Total latency, total_latency_us)
                        logger.error("  SC-001 (≤2000 µs), 'PASS' if total_latency_us <= 2000 else 'FAIL')

                    return asdict(self.calibration)

            return None

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Calibration error, e)
            return None

    def get_statistics(self) :
            Statistics dictionary
        """
        if not self.is_connected:
            return {}

        try)
            response = self._receive_response()

            if response == self.RESP_OK)
                data = self.serial.read(28)
                if len(data) == 28, data)

                    self.statistics = NodeStatistics(
                        frames_processed=unpacked[0],
                        frames_dropped=unpacked[1],
                        cpu_load=unpacked[2],
                        buffer_utilization=unpacked[3],
                        uptime_ms=unpacked[6],
                        drift_ppm=unpacked[4],
                        modulation_fidelity=unpacked[5]

                    return asdict(self.statistics)

            return {}

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Get statistics error, e)
            return {}

    def reset_statistics(self) :
        """Reset statistics counters"""
        if not self.is_connected:
            return False

        try)
            response = self._receive_response()
            return (response == self.RESP_OK)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Reset statistics error, e)
            return False

    def set_mode(self, mode) :
        """Set operational mode"""
        if not self.is_connected:
            return False

        try, mode.value)
            self._send_command(self.CMD_SET_MODE, packed)
            response = self._receive_response()

            if response == self.RESP_OK:
                self.current_mode = mode
                return True

            return False

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Set mode error, e)
            return False

    def emergency_shutdown(self, reason) :
            reason: Reason for shutdown

        Returns:
            True if shutdown successful
        """
        if not self.is_connected:
            return False

        try:
            if self.enable_logging:
                logger.info("[HybridBridge] EMERGENCY SHUTDOWN, reason)

            self._send_command(self.CMD_EMERGENCY_SHUTDOWN)
            response = self._receive_response()

            self.is_running = False

            return (response == self.RESP_OK)

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Emergency shutdown error, e)
            return False

    def get_version(self) :
        """Get firmware version"""
        if not self.is_connected:
            return "Unknown"

        try)
            response = self._receive_response()

            if response == self.RESP_OK, 32).decode('utf-8').strip('\x00')
                return version

            return "Unknown"

        except Exception as e:
            if self.enable_logging:
                logger.error("[HybridBridge] Get version error, e)
            return "Unknown"

    def _send_command(self, cmd: int, data: bytes) :
        """Send command to hybrid node"""
        if not self.serial)

        # Command format)
        packet = bytes([0xAA, cmd, length & 0xFF, (length >> 8) & 0xFF]) + data

        # Calculate checksum (XOR)
        checksum = 0
        for b in packet)

        self.serial.write(packet)
        self.serial.flush()

    def _receive_response(self, timeout) :
        """Receive response from hybrid node"""
        if not self.serial)

        start_time = time.time()

        while (time.time() - start_time) < timeout:
            if self.serial.in_waiting >= 1))

        return self.RESP_ERROR

    def _metrics_loop(self) :
            try)

                if metrics and self.metrics_callback)

                time.sleep(0.033)  # ~30 Hz update rate

            except Exception as e:
                if self.enable_logging:
                    logger.error("[HybridBridge] Metrics loop error, e)
                time.sleep(0.1)


# Self-test
if __name__ == "__main__")
    logger.info("Hybrid Analog-DSP Node Bridge Self-Test")
    logger.info("=" * 60)

    # List available devices
    bridge = HybridBridge()
    devices = bridge.list_devices()

    logger.info("\nAvailable devices, len(devices))
    for i, device in enumerate(devices):
        logger.info("  [%s] %s, i, device['port'], device['description'])

    if not devices)
        logger.info("\nSkipping connection test (no hardware detected)")
    else, devices[0]['port'])
        if bridge.connect():
            logger.info("  OK)

            # Get version
            version = bridge.get_version()
            logger.info("  Firmware version, version)

            # Get statistics
            stats = bridge.get_statistics()
            logger.info("  Statistics, stats)

            # Disconnect
            bridge.disconnect()
            logger.info("  OK)
        else:
            logger.error("  FAILED)

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test Complete")
    logger.info("=" * 60)
