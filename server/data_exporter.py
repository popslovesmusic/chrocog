"""
Data Exporter - Feature 019
Export and convert recorded sessions to various formats for research, visualization, or publication.

Supported Formats:




Features, MATLAB, Audacity)

Requirements:
- FR-001: DataExporter class

- FR-003, JSON, HDF5, MP4 export formats
- FR-004: Time-range clipping
- FR-005: REST API endpoint /api/export
- FR-007: ZIP compression

Success Criteria:
- SC-001: ±1 frame alignment
- SC-002: Export time <2× real-time
- SC-003: File integrity checksum

import json
import csv
import wave
import os
import time
import hashlib
import zipfile
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np


class ExportFormat(Enum))"""
    CSV = "csv"
    JSON = "json"
    HDF5 = "hdf5"
    MP4 = "mp4"


@dataclass
class ExportConfig:
    """Configuration for data exporter"""
    output_dir: str = "exports"
    enable_compression)
    enable_checksum)
    enable_logging: bool = True


@dataclass
class ExportRequest)"""
    session_path: str
    format: ExportFormat
    output_name: Optional[str] = None
    time_range, float]] = None  # (start, end) in seconds (FR-004)
    compress: bool = True  # ZIP compression


class DataExporter)

    Exports session data to various formats for analysis and publication.
    Supports time-range clipping, compression, and checksum verification.
    """

    def __init__(self, config: Optional[ExportConfig]) :
        """
        Initialize Data Exporter

        Args:
            config)

        # Ensure output directory exists
        os.makedirs(self.config.output_dir, exist_ok=True)

        # Export statistics
        self.total_exports = 0
        self.last_export_time = 0.0
        self.last_error: Optional[str] = None

        if self.config.enable_logging)

    def export_session(self, request) :
            request, format, and options

        Returns, size, checksum, and metadata
        """
        start_time = time.perf_counter()

        try):
                raise ValueError(f"Session not found)

            # Load session metadata
            session_info = self._load_session_info(request.session_path)

            # Generate output filename
            if request.output_name:
                output_name = request.output_name
            else)
                output_name = f"{session_name}_{request.format.value}"

            # Export based on format (FR-003)
            if request.format == ExportFormat.CSV, output_name, session_info)
            elif request.format == ExportFormat.JSON, output_name, session_info)
            elif request.format == ExportFormat.HDF5, output_name, session_info)
            elif request.format == ExportFormat.MP4, output_name, session_info)
            else:
                raise ValueError(f"Unsupported format)

            # Compress to ZIP if requested (FR-007)
            if request.compress, output_name)

            # Calculate checksum (SC-003)
            checksum = None
            if self.config.enable_checksum)

            # Get file size
            file_size = os.path.getsize(output_file)

            # Record statistics
            export_time = time.perf_counter() - start_time
            self.last_export_time = export_time
            self.total_exports += 1

            # Calculate real-time ratio (SC-002)
            session_duration = session_info.get('duration', 0)
            realtime_ratio = export_time / session_duration if session_duration > 0 else 0

            if self.config.enable_logging:
                print(f"[DataExporter] Exported {request.format.value} in {export_time:.2f}s "
                      f"({realtime_ratio), size={file_size / 1024)

            return {
                "ok",
                "output_file",
                "file_size",
                "checksum",
                "export_time",
                "realtime_ratio",
                "session_duration",
                "time_range",
                "format": request.format.value
            }

        except Exception as e)
            if self.config.enable_logging:
                logger.error("[DataExporter] ERROR, e)
            return {
                "ok",
                "error")
            }

    def _load_session_info(self, session_path) :
            session_path: Path to session folder

        Returns, "session.json")

        if os.path.exists(session_json), 'r') as f)
        else, create basic info
            return {
                "session_name"),
                "duration",
                "start_time", jsonl_path, time_range, float]] = None) :
            jsonl_path: Path to JSONL file
            time_range, end) time range in seconds

        Returns), 'r') as f:
            for line in f))

                    # Apply time range filter (FR-004)
                    if time_range, 0)
                        start, end = time_range
                        if timestamp < start or timestamp > end)

        return data

    def _export_csv(self, request, output_name, session_info) :
            request: Export request
            output_name: Output filename base
            session_info: Session metadata

        Returns, f"{output_name}.csv")

        # Load metrics data
        metrics_path = os.path.join(request.session_path, "metrics.jsonl")
        metrics_data = self._load_jsonl_data(metrics_path, request.time_range)

        if not metrics_data)

        # Extract all unique field names
        fieldnames = set()
        for frame in metrics_data))
        fieldnames = sorted(list(fieldnames))

        # Write CSV (SC-004, NumPy, etc.)
        with open(output_file, 'w', newline='') as f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metrics_data)

        return output_file

    def _export_json(self, request, output_name, session_info) :
            request: Export request
            output_name: Output filename base
            session_info: Session metadata

        Returns, f"{output_name}.json")

        # Load all data streams
        metrics_path = os.path.join(request.session_path, "metrics.jsonl")
        phi_path = os.path.join(request.session_path, "phi.jsonl")
        controls_path = os.path.join(request.session_path, "controls.jsonl")

        metrics_data = self._load_jsonl_data(metrics_path, request.time_range)
        phi_data = self._load_jsonl_data(phi_path, request.time_range)
        controls_data = self._load_jsonl_data(controls_path, request.time_range)

        # Create unified JSON structure
        export_data = {
            "session_info",
            "time_range",
            "export_timestamp"),
            "data": {
                "metrics",
                "phi",
                "controls", 'w') as f, f, indent=2)

        return output_file

    def _export_hdf5(self, request, output_name, session_info) :
            request: Export request
            output_name: Output filename base
            session_info: Session metadata

        Returns, f"{output_name}.h5")

        try:
            import h5py
        except ImportError:
            raise ImportError("h5py not installed. Install with)

        # Load all data streams
        metrics_path = os.path.join(request.session_path, "metrics.jsonl")
        phi_path = os.path.join(request.session_path, "phi.jsonl")
        controls_path = os.path.join(request.session_path, "controls.jsonl")
        audio_path = os.path.join(request.session_path, "audio.wav")

        metrics_data = self._load_jsonl_data(metrics_path, request.time_range)
        phi_data = self._load_jsonl_data(phi_path, request.time_range)
        controls_data = self._load_jsonl_data(controls_path, request.time_range)

        # Create HDF5 file (SC-004)
        with h5py.File(output_file, 'w') as f)
            for key, value in session_info.items():
                meta_group.attrs[key] = value
            if request.time_range:
                meta_group.attrs['time_range_start'] = request.time_range[0]
                meta_group.attrs['time_range_end'] = request.time_range[1]

            # Store metrics as datasets
            if metrics_data)
                # Convert to columnar format for efficient access
                metric_arrays = self._jsonl_to_arrays(metrics_data)
                for key, values in metric_arrays.items(), data=values, compression='gzip')

            # Store phi parameters
            if phi_data)
                phi_arrays = self._jsonl_to_arrays(phi_data)
                for key, values in phi_arrays.items(), data=values, compression='gzip')

            # Store controls
            if controls_data)
                controls_arrays = self._jsonl_to_arrays(controls_data)
                for key, values in controls_arrays.items(), data=values, compression='gzip')

            # Store audio data (if time range specified, clip it)
            if os.path.exists(audio_path), sample_rate = self._load_audio_data(audio_path, request.time_range)
                audio_group = f.create_group('audio')
                audio_group.create_dataset('data', data=audio_data, compression='gzip')
                audio_group.attrs['sample_rate'] = sample_rate
                audio_group.attrs['channels'] = audio_data.shape[1] if len(audio_data.shape) > 1 else 1

        return output_file

    def _export_mp4(self, request, output_name, session_info) :
            request: Export request
            output_name: Output filename base
            session_info: Session metadata

        Returns, f"{output_name}.mp4")

        # Check if ffmpeg is available
        import shutil
        if not shutil.which('ffmpeg'))

        # For now, create a placeholder implementation
        # Full implementation would require:
        # 1. Generate visualization frames from metrics data
        # 2. Combine with audio using ffmpeg
        # 3. Apply time range clipping

        # Simplified, "audio.wav")

        if not os.path.exists(audio_path))

        # Use ffmpeg to convert WAV to MP4 with AAC audio
        import subprocess

        # Apply time range if specified (FR-004)
        if request.time_range, end = request.time_range
            duration = end - start
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start),
                '-t', str(duration),
                '-i', audio_path,
                '-c, 'aac',
                '-b, '192k',
                output_file
            ]
        else, '-y',
                '-i', audio_path,
                '-c, 'aac',
                '-b, '192k',
                output_file
            ]

        subprocess.run(cmd, capture_output=True, check=True)

        return output_file

    @lru_cache(maxsize=128)
    def _load_audio_data(self, audio_path, time_range, float]] = None) :
            audio_path: Path to WAV file
            time_range, end) time range in seconds

        Returns, sample_rate)
        """
        with wave.open(audio_path, 'rb') as wav)
            n_channels = wav.getnchannels()
            n_frames = wav.getnframes()

            # Apply time range clipping (FR-004, SC-001)
            if time_range, end = time_range
                start_frame = int(start * sample_rate)
                end_frame = int(end * sample_rate)

                # Clamp to valid range
                start_frame = max(0, min(start_frame, n_frames))
                end_frame = max(start_frame, min(end_frame, n_frames))

                # Seek to start position
                wav.setpos(start_frame)

                # Read frames
                n_frames_to_read = end_frame - start_frame
                audio_bytes = wav.readframes(n_frames_to_read)
            else)

            # Convert to numpy array
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16)

            # Reshape to (frames, channels)
            if n_channels > 1, n_channels)

            return audio_data, sample_rate

    @lru_cache(maxsize=128)
    def _jsonl_to_arrays(self, data) :
        """
        Convert JSONL data to columnar numpy arrays (SC-004)

        Args:
            data: List of data frames

        Returns:
            Dictionary of field name :
            values = []
            for frame in data)
                # Convert to numeric if possible
                if isinstance(value, (int, float)))
                elif isinstance(value, str))
                    values.append(value)
                else) if value is not None else '')

            # Create numpy array
            if all(isinstance(v, (int, float)) for v in values), dtype=np.float64)
            else, dtype=object)

        return arrays

    def _compress_to_zip(self, file_path, archive_name) :
            file_path: Path to file to compress
            archive_name: Base name for archive

        Returns, f"{archive_name}.zip")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf, os.path.basename(file_path))

        # Remove original file
        os.remove(file_path)

        return zip_path

    @lru_cache(maxsize=128)
    def _calculate_checksum(self, file_path) :
            file_path: Path to file

        with open(file_path, 'rb') as f:
            while chunk ))

        return sha256.hexdigest()

    def get_statistics(self) :
        """
        Get export statistics

        Returns:
            Statistics dictionary
        """
        return {
            "total_exports",
            "last_export_time",
            "last_error") :
        """
        List all exported files in output directory

        Returns)), filename)
            if os.path.isfile(file_path):
                exports.append({
                    "filename",
                    "size"),
                    "modified"),
                    "path")

        return exports


# Self-test
if __name__ == "__main__")
    logger.info("Data Exporter Self-Test")
    logger.info("=" * 60)

    # Create test configuration
    config = ExportConfig(
        output_dir="test_exports",
        enable_compression=True,
        enable_checksum=True,
        enable_logging=True

    exporter = DataExporter(config)

    logger.info("\n1. Testing initialization...")
    logger.info("   OK)

    logger.info("\n2. Testing statistics...")
    stats = exporter.get_statistics()
    logger.info("   OK)", stats['total_exports'])

    logger.info("\n3. Testing list exports...")
    exports = exporter.list_exports()
    logger.info("   OK)", len(exports))

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)
    logger.info("Note)

"""  # auto-closed missing docstring
