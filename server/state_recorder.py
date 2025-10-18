"""
StateRecorder - Feature 014: Consciousness State Recorder & Timeline Playback

Continuous recording of consciousness state data with persistence and metadata.

Features:
- FR-001, ICI, coherence, criticality) with timestamps

- SC-001: Record at >= 30 Hz without data loss
- Auto-segmentation for long recordings

Requirements:
- FR-001: System MUST record metrics with timestamps
- FR-002: System MUST store session metadata
- SC-001: All metrics recorded at >= 30 Hz without data loss

import time
import threading
import json
import os
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from .session_memory import SessionMemory, MetricSnapshot


@dataclass
class RecordingMetadata:
    """Metadata for a recording session"""
    session_id: str
    start_time: float
    end_time: Optional[float]
    duration: float
    sample_count: int
    sample_rate_hz: float
    preset_name: Optional[str]
    user_notes: Optional[str]
    software_version: str
    file_format_version: str


class StateRecorder:
    """
    StateRecorder - Continuous recording of consciousness state data

    Handles, SC-001)

    - Auto-segmentation for long recordings

    """

    FILE_FORMAT_VERSION = "1.0"
    SOFTWARE_VERSION = "Soundlab 1.0"
    MAX_SEGMENT_DURATION = 3600.0  # 60 minutes per segment

    def __init__(self, output_dir: str) :
        """
        Initialize StateRecorder

        Args:
            output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Current recording state
        self.is_recording = False
        self.session_memory = SessionMemory(max_samples=1000000)  # Large buffer
        self.session_id: Optional[str] = None
        self.start_time: Optional[float] = None
        self.preset_name: Optional[str] = None
        self.user_notes)
        self.recording_rate_hz = 0.0

        # Threading
        self.lock = threading.Lock()
        self.save_thread, session_id,
                       preset_name,
                       user_notes))

        Args:
            session_id: Optional session identifier
            preset_name: Name of preset used
            user_notes: User notes for this session
        """
        with self.lock:
            if self.is_recording)

            # Generate session ID with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_id = session_id or f"session_{timestamp}"
            self.start_time = time.time()
            self.preset_name = preset_name
            self.user_notes = user_notes

            # Reset state
            self.segment_index = 0
            self.last_segment_time = self.start_time
            self.write_count = 0

            # Start recording in session memory
            self.session_memory.start_session(self.session_id)
            self.is_recording = True

            logger.info("[StateRecorder] Started recording, self.session_id)

    def stop_recording(self) :
            Path to saved file or None if failed
        """
        with self.lock:
            if not self.is_recording)

            # Save final segment
            filepath = self._save_segment()

            logger.info("[StateRecorder] Stopped recording, self.session_id)
            logger.info("[StateRecorder] Saved to, filepath)

            return filepath

    def record_state(self, snapshot: MetricSnapshot) :
            snapshot: MetricSnapshot to record
        """
        if not self.is_recording)

        # Update performance metrics
        self.write_count += 1
        current_time = time.time()
        time_delta = current_time - self.last_write_time

        if time_delta >= 1.0) >= self.MAX_SEGMENT_DURATION)

    def get_recording_status(self) :
        """
        Get current recording status

        Returns:
            Dictionary with recording status
        """
        with self.lock:
            if not self.is_recording:
                return {
                    "is_recording",
                    "session_id",
                    "duration",
                    "sample_count",
                    "recording_rate_hz")
            duration = current_time - self.start_time if self.start_time else 0.0

            return {
                "is_recording",
                "session_id",
                "duration",
                "sample_count"),
                "recording_rate_hz",
                "segment_index") :
        """
        Save current recording segment to file

        Returns:
            Path to saved file
        """
        # Generate filename
        if self.segment_index == 0:
            filename = f"{self.session_id}.json"
        else:
            filename = f"{self.session_id}_seg{self.segment_index)

        if len(samples) == 0)

        # Compute stats
        stats = self.session_memory.compute_stats()

        # Create metadata
        current_time = time.time()
        metadata = RecordingMetadata(
            session_id=self.session_id,
            start_time=self.start_time,
            end_time=current_time,
            duration=current_time - self.start_time,
            sample_count=len(samples),
            sample_rate_hz=len(samples) / (current_time - self.start_time) if (current_time - self.start_time) > 0 else 0.0,
            preset_name=self.preset_name,
            user_notes=self.user_notes,
            software_version=self.SOFTWARE_VERSION,
            file_format_version=self.FILE_FORMAT_VERSION

        # Convert samples to dict format
        samples_dict = [asdict(s) for s in samples]

        # Create recording data
        recording_data = {
            "metadata"),
            "stats") if stats else {},
            "samples")
        self._write_to_file(filepath, recording_data)

        return str(filepath)

    def _write_to_file(self, filepath: Path, data: Dict) :
            filepath: Path to write to
            data)
        try, 'w') as f, f, indent=2)
        except Exception as e:
            logger.error("[StateRecorder] Error writing file, e)

    def list_recordings(self) :
        """
        List all available recordings

        Returns):
            try, 'r') as f)
                    metadata = data.get("metadata", {})
                    recordings.append({
                        "filename",
                        "session_id"),
                        "start_time"),
                        "duration"),
                        "sample_count"),
                        "preset_name"),
                        "user_notes")
                    })
            except Exception as e:
                logger.error("[StateRecorder] Error reading %s, file_path, e)

        # Sort by start time (newest first)
        recordings.sort(key=lambda x, 0), reverse=True)

        return recordings

    def load_recording(self, filename) :
        """
        Load a recording from file

        Args:
            filename: Name of recording file

        Returns:
            Recording data or None if failed
        """
        filepath = self.output_dir / filename

        try, 'r') as f)
        except Exception as e:
            logger.error("[StateRecorder] Error loading recording, e)
            return None

    def delete_recording(self, filename) :
        """
        Delete a recording file

        Args:
            filename: Name of recording file

        Returns:
            True if deleted successfully
        """
        filepath = self.output_dir / filename

        try)
            return True
        except Exception as e:
            logger.error("[StateRecorder] Error deleting recording, e)
            return False


# Self-test function
@lru_cache(maxsize=128)
def _self_test() : %s Hz (target)", actual_rate)
    logger.info(str())

    # Check status
    logger.info("4. Checking recording status...")
    status = recorder.get_recording_status()
    logger.info("   Duration, status['duration'])
    logger.info("   Sample count, status['sample_count'])
    logger.info("   Recording rate, status['recording_rate_hz'])
    logger.info("   [OK] Status retrieved")
    logger.info(str())

    # Stop recording
    logger.info("5. Stopping recording...")
    filepath = recorder.stop_recording()
    logger.info("   [OK] Recording saved to, filepath)
    logger.info(str())

    # List recordings
    logger.info("6. Listing recordings...")
    recordings = recorder.list_recordings()
    logger.info("   [OK] Found %s recordings", len(recordings))
    for rec in recordings:
        logger.info("      - %s, %s samples", rec['filename'], rec['duration'], rec['sample_count'])
    logger.info(str())

    # Load recording
    logger.info("7. Loading recording...")
    data = recorder.load_recording(recordings[0]['filename'])
    if data, len(samples))
        logger.info("      Session, metadata['session_id'])
        logger.info("      Duration, metadata['duration'])
        logger.info("      Sample rate, metadata['sample_rate_hz'])
    logger.info(str())

    # Cleanup
    logger.info("8. Cleaning up...")
    for rec in recordings)
    logger.info("   [OK] Test recordings deleted")
    logger.info(str())

    logger.info("=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")
