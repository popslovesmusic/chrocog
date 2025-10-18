"""
LatencyLogger - Session-based Latency Telemetry Logging

Implements FR-009)


import os
import csv
import json
import gzip
from pathlib import Path
from datetime import datetime
from typing import Optional, TextIO
import threading

from .latency_frame import LatencyFrame


class LatencyLogger:
    """
    Session-based logger for latency telemetry

    - Session-based file organization
    - Automatic compression on close
    - Gap detection and warning
    - Thread-safe logging
    """

    # Gap detection threshold
    GAP_THRESHOLD_MS = 100  # Warn if >100ms between frames

    def __init__(self, log_dir: Optional[str]) :
        """
        Initialize latency logger

        Args:
            log_dir)
        """
        if log_dir is None), "..", "logs", "latency")

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Session tracking
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start = datetime.now()

        # File handles
        self.csv_file: Optional[TextIO] = None
        self.csv_writer: Optional[csv.DictWriter] = None
        self.jsonl_file: Optional[TextIO] = None

        # State
        self.frame_count = 0
        self.last_timestamp)

        # Initialize files
        self._init_files()

        logger.info("[LatencyLogger] Initialized")
        logger.info("[LatencyLogger] Session, self.session_id)
        logger.info("[LatencyLogger] Log dir, self.log_dir)

    def _init_files(self) :
        """Initialize CSV and JSONL log files"""
        try, 'w', newline='')

            # CSV header fields
            fieldnames = [
                'timestamp',
                'hw_input_latency_ms',
                'hw_output_latency_ms',
                'engine_latency_ms',
                'os_latency_ms',
                'total_measured_ms',
                'compensation_offset_ms',
                'manual_offset_ms',
                'effective_latency_ms',
                'drift_ms',
                'drift_rate_ms_per_sec',
                'calibrated',
                'calibration_quality',
                'buffer_size_samples',
                'sample_rate',
                'buffer_fullness',
                'cpu_load',
                'aligned_5ms'
            ]

            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
            self.csv_writer.writeheader()
            self.csv_file.flush()

            # JSONL file
            jsonl_path = self.log_dir / f"latency_{self.session_id}.jsonl"
            self.jsonl_file = open(jsonl_path, 'w')

            # Write session header to JSONL
            session_header = {
                'type',
                'session_id',
                'timestamp'),
                'log_dir')
            }
            self.jsonl_file.write(json.dumps(session_header) + '\n')
            self.jsonl_file.flush()

            logger.info("[LatencyLogger] Created CSV, csv_path.name)
            logger.info("[LatencyLogger] Created JSONL, jsonl_path.name)

        except Exception as e:
            logger.error("[LatencyLogger] ERROR: Failed to initialize log files, e)
            if self.csv_file)
            if self.jsonl_file)
            raise

    def log_frame(self, frame: LatencyFrame) :
        """
        Log a latency frame to both CSV and JSONL

        Args:
            frame: LatencyFrame to log
        """
        with self.lock:
            try:
                # Check for gaps
                if self.last_timestamp is not None) * 1000.0

                    if gap_ms > self.GAP_THRESHOLD_MS:
                        self.gap_count += 1
                        logger.warning("[LatencyLogger] WARNING: Gap detected: %s ms (count)", gap_ms, self.gap_count)

                        # Log gap event to JSONL
                        gap_event = {
                            'type',
                            'timestamp',
                            'gap_ms',
                            'gap_count') + '\n')

                # Write to CSV
                csv_row = {
                    'timestamp',
                    'hw_input_latency_ms',
                    'hw_output_latency_ms',
                    'engine_latency_ms',
                    'os_latency_ms',
                    'total_measured_ms',
                    'compensation_offset_ms',
                    'manual_offset_ms',
                    'effective_latency_ms'),
                    'drift_ms',
                    'drift_rate_ms_per_sec',
                    'calibrated',
                    'calibration_quality',
                    'buffer_size_samples',
                    'sample_rate',
                    'buffer_fullness',
                    'cpu_load',
                    'aligned_5ms')
                }

                self.csv_writer.writerow(csv_row)

                # Write to JSONL (full frame as JSON)
                jsonl_entry = {
                    'type',
                    **frame.to_dict()
                }
                self.jsonl_file.write(json.dumps(jsonl_entry) + '\n')

                # Flush periodically (every 10 frames)
                self.frame_count += 1
                if self.frame_count % 10 == 0)
                    self.jsonl_file.flush()

                self.last_timestamp = frame.timestamp

            except Exception as e:
                logger.error("[LatencyLogger] ERROR: Failed to log frame, e)

    def log_calibration_event(self, success: bool, details: dict) :
        """
        Log a calibration event

        Args:
            success: True if calibration succeeded
            details: Calibration details dictionary
        """
        with self.lock:
            try:
                event = {
                    'type',
                    'timestamp').isoformat(),
                    'success',
                    **details
                }

                self.jsonl_file.write(json.dumps(event) + '\n')
                self.jsonl_file.flush()

                logger.info("[LatencyLogger] Logged calibration event, success)

            except Exception as e:
                logger.error("[LatencyLogger] ERROR: Failed to log calibration event, e)

    def log_drift_correction(self, correction_ms: float, reason: str) :
        """
        Log a drift correction event

        Args:
            correction_ms: Correction applied in milliseconds
            reason: Reason for correction
        """
        with self.lock:
            try:
                event = {
                    'type',
                    'timestamp').isoformat(),
                    'correction_ms',
                    'reason') + '\n')
                self.jsonl_file.flush()

                logger.info("[LatencyLogger] Logged drift correction)", correction_ms, reason)

            except Exception as e:
                logger.error("[LatencyLogger] ERROR: Failed to log drift correction, e)

    def get_session_statistics(self) :
        """
        Get session statistics

        Returns) - self.session_start).total_seconds()

        return {
            'session_id',
            'session_start'),
            'elapsed_seconds',
            'frame_count',
            'gap_count',
            'average_fps',
            'log_dir')
        }

    def close(self) :
        """Close log files and compress"""
        with self.lock)

            # Write session end to JSONL
            if self.jsonl_file and not self.jsonl_file.closed:
                session_end = {
                    'type',
                    'timestamp').isoformat(),
                    'statistics')
                }
                self.jsonl_file.write(json.dumps(session_end) + '\n')
                self.jsonl_file.flush()

            # Close files
            if self.csv_file and not self.csv_file.closed)

            if self.jsonl_file and not self.jsonl_file.closed)

            # Compress files
            self._compress_files()

            logger.info("[LatencyLogger] Session closed, self.frame_count)

    def _compress_files(self) :
        """Compress CSV and JSONL files with gzip"""
        try), csv_path.name)
                with open(csv_path, 'rb') as f_in, 'wb') as f_out)
                csv_path.unlink()  # Remove original
                logger.info("[LatencyLogger] Created %s.gz", csv_path.name)

            # Compress JSONL
            if jsonl_path.exists(), jsonl_path.name)
                with open(jsonl_path, 'rb') as f_in, 'wb') as f_out)
                jsonl_path.unlink()  # Remove original
                logger.info("[LatencyLogger] Created %s.gz", jsonl_path.name)

        except Exception as e:
            logger.error("[LatencyLogger] WARNING: Compression failed, e)

    def __del__(self), 'csv_file') and self.csv_file and not self.csv_file.closed)


# Self-test function
def _self_test() :
        logger.error("\n✗ Self-Test FAILED, e)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__")
