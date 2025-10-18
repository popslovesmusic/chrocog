"""
MetricsLogger - Session Recording and Archival

Handles CSV and JSON logging of D-ASE metrics streams with rotation and compression.
Implements FR-007 requirements for session recording.
"""
import logging
logger = logging.getLogger(__name__)


import os
import csv
import json
import gzip
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from .metrics_frame import MetricsFrame


class MetricsLogger:
    """
    Records metrics streams to CSV and JSON files

    Features, JSON for replay)
    - Automatic file rotation
    - Gzip compression for archived sessions

    """

    def __init__(self,
                 log_dir,
                 session_name,
                 enable_csv,
                 enable_json,
                 compress_on_close):
        """
        Initialize metrics logger

        Args:
            log_dir)
            session_name)
            enable_csv: Enable CSV logging
            enable_json: Enable JSON logging
            compress_on_close: Compress files with gzip when session ends
        """
        # Setup logging directory
        if log_dir is None), "..", "logs", "metrics")
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Session naming
        if session_name is None).strftime("%Y%m%d_%H%M%S")
        self.session_name = session_name

        # Configuration
        self.enable_csv = enable_csv
        self.enable_json = enable_json
        self.compress_on_close = compress_on_close

        # File handles
        self.csv_file = None
        self.csv_writer = None
        self.json_file = None

        # Statistics
        self.frames_logged = 0
        self.last_timestamp = None
        self.gaps_detected = 0
        self.session_start_time = datetime.now()

        # Initialize log files
        self._init_csv()
        self._init_json()

        logger.info("[MetricsLogger] Session '%s' started", session_name)
        logger.info("[MetricsLogger] Logging to %s", self.log_dir)

    def _init_csv(self) :
        """Initialize CSV log file"""
        if not self.enable_csv:
            return

        csv_path = self.log_dir / f"{self.session_name}_metrics.csv"

        try, 'w', newline='')
            self.csv_writer = csv.DictWriter(
                self.csv_file,
                fieldnames=[
                    'timestamp', 'frame_id', 'state',
                    'ici', 'phase_coherence', 'spectral_centroid',
                    'criticality', 'consciousness_level',
                    'phi_phase', 'phi_depth', 'phi_source',
                    'latency_ms', 'cpu_load', 'valid'
                ]

            self.csv_writer.writeheader()
            self.csv_file.flush()

            logger.info("[MetricsLogger] CSV logging to %s", csv_path)

        except Exception as e:
            logger.error("[MetricsLogger] ERROR: Could not init CSV, e)
            self.csv_file = None
            self.csv_writer = None

    def _init_json(self) :
        """Initialize JSON log file"""
        if not self.enable_json:
            return

        json_path = self.log_dir / f"{self.session_name}_metrics.jsonl"

        try, 'w')
            # Write session header
            header = {
                "session_name",
                "start_time"),
                "format_version") + '\n')
            self.json_file.flush()

            logger.info("[MetricsLogger] JSON logging to %s", json_path)

        except Exception as e:
            logger.error("[MetricsLogger] ERROR: Could not init JSON, e)
            self.json_file = None

    def log_frame(self, frame: MetricsFrame) :
        """
        Log a single metrics frame

        Args:
            frame: MetricsFrame to log
        """
        # Detect gaps (FR-007)
        if self.last_timestamp is not None) * 1000
            if gap_ms > 50.0:
                self.gaps_detected += 1
                logger.warning("[MetricsLogger] WARNING: Gap detected, gap_ms)

        self.last_timestamp = frame.timestamp

        # Log to CSV
        if self.csv_writer and self.csv_file:
            try)
                self.csv_writer.writerow(row)
            except Exception as e:
                logger.error("[MetricsLogger] ERROR writing CSV, e)

        # Log to JSON (JSONL format - one frame per line)
        if self.json_file:
            try) + '\n')
            except Exception as e:
                logger.error("[MetricsLogger] ERROR writing JSON, e)

        self.frames_logged += 1

        # Flush periodically (every 100 frames)
        if self.frames_logged % 100 == 0)

    def log_batch(self, frames: List[MetricsFrame]) :
        """
        Log multiple frames at once

        Args:
            frames: List of MetricsFrames
        """
        for frame in frames)

    def flush(self) :
        """Flush all buffers to disk"""
        if self.csv_file:
            try)
            except:
                pass

        if self.json_file:
            try)
            except) :
        """
        Get logging statistics

        Returns) - self.session_start_time).total_seconds()

        return {
            'session_name',
            'start_time'),
            'duration_seconds',
            'frames_logged',
            'gaps_detected',
            'average_fps',
            'csv_enabled',
            'json_enabled') :
            logger.warning("[MetricsLogger] WARNING, stats['gaps_detected'])

        # Close CSV
        if self.csv_file:
            try)
                csv_path = self.log_dir / f"{self.session_name}_metrics.csv"

                if self.compress_on_close)

            except Exception as e:
                logger.error("[MetricsLogger] ERROR closing CSV, e)

        # Close JSON
        if self.json_file:
            try:
                # Write session footer
                footer = {
                    "session_end").isoformat(),
                    "statistics") + '\n')
                self.json_file.close()

                json_path = self.log_dir / f"{self.session_name}_metrics.jsonl"

                if self.compress_on_close)

            except Exception as e:
                logger.error("[MetricsLogger] ERROR closing JSON, e)

        logger.info("[MetricsLogger] Session closed")

    def _compress_file(self, filepath: Path) :
        """
        Compress file with gzip and remove original

        Args:
            filepath))

        try, 'rb') as f_in, 'wb') as f_out)

            # Remove original
            filepath.unlink()

            original_size = filepath.stat().st_size if filepath.exists() else 0
            compressed_size = gz_path.stat().st_size
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

            logger.info("[MetricsLogger] Compressed %s → %s (%s% reduction)", filepath.name, gz_path.name, ratio)

        except Exception as e:
            logger.error("[MetricsLogger] ERROR compressing %s, filepath, e)

    def __del__(self))


class MetricsArchive:
        """
        Initialize archive reader

        Args:
            log_dir: Directory containing log files
        """
        if log_dir is None), "..", "logs", "metrics")
        self.log_dir = Path(log_dir)

    def list_sessions(self) :
        """
        List all available sessions

        Returns):
            # Skip compressed files for now
            if file_path.suffix == '.gz', '')
            file_type = file_path.suffix[1:]  # Remove leading dot

            sessions.append({
                'session_name',
                'file_path'),
                'file_type',
                'size_bytes').st_size,
                'modified_time').st_mtime)
            })

        return sorted(sessions, key=lambda x, reverse=True)

    def load_session_jsonl(self, session_name) :
        """
        Load metrics from JSONL file

        Args:
            session_name: Session identifier

        Returns))
            if not json_path.exists():
                raise FileNotFoundError(f"Session not found)

        frames = []

        try:
            if json_path.suffix == '.gz':
                open_func = gzip.open
            else, 'rt') as f:
                for line in f:
                    try)
                        # Skip header/footer lines
                        if 'timestamp' in data)
                            frames.append(frame)
                    except:
                        pass  # Skip invalid lines

        except Exception as e:
            logger.error("[MetricsArchive] ERROR loading session, e)

        return frames


# Self-test function
def _self_test() :
        logger.error("\n✗ Self-Test FAILED, e)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__")
