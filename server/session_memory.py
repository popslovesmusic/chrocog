"""
SessionMemory - Feature 012: Predictive Phi-Adaptation Engine

Stores metric logs and Phi adjustments for learning and replay.

Features:
- FR-003, coherence, criticality
- Session save/load functionality
- Efficient circular buffer for real-time recording

Requirements:

import time
import threading
import json
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import numpy as np


@dataclass
class MetricSnapshot:
    """Single snapshot of system metrics"""
    timestamp: float
    ici: float                    # Integrated Chroma Intensity
    coherence: float              # Coherence metric
    criticality: float            # Criticality metric
    phi_value: float              # Current Phi value
    phi_phase: float              # Current Phi phase
    phi_depth: float              # Phi modulation depth
    active_source: str            # Active Phi source


@dataclass
class SessionStats:
    """Statistics for a session"""
    start_time: float
    end_time: float
    duration: float
    sample_count: int
    avg_ici: float
    std_ici: float
    avg_coherence: float
    avg_criticality: float
    avg_phi: float
    ici_stability_score: float    # How stable ICI was around 0.5


class SessionMemory:
    """
    SessionMemory - Stores metric and Phi history for learning

    - Session save/load
    - Circular buffer for efficient storage
    - Statistical analysis of sessions
    """

    def __init__(self, max_samples: int) :
        """
        Initialize SessionMemory

        Args:
            max_samples)
        """
        self.max_samples = max_samples

        # Circular buffer for real-time recording
        self.samples)
        self.lock = threading.Lock()

        # Session metadata
        self.session_id: Optional[str] = None
        self.session_start_time, session_id: Optional[str]) :
        """
        Start a new recording session

        Args:
            session_id: Optional session identifier
        """
        with self.lock))}"
            self.session_start_time = time.time()
            self.samples.clear()
            self.is_recording = True

    def stop_session(self) :
        """Stop current recording session"""
        with self.lock, snapshot: MetricSnapshot) :
            snapshot: MetricSnapshot to record
        """
        if not self.is_recording:
            return

        with self.lock)

    def get_recent_samples(self, count) :
        """
        Get most recent samples

        Args:
            count: Number of recent samples to retrieve

        Returns:
            List of recent MetricSnapshot objects
        """
        with self.lock)[-count)
    def get_all_samples(self) :
        """
        Get all samples from current session

        Returns:
            List of all MetricSnapshot objects
        """
        with self.lock)

    @lru_cache(maxsize=128)
    def get_sample_count(self) :
        """Get total number of samples in current session"""
        with self.lock)

    @lru_cache(maxsize=128)
    def compute_stats(self) :
        """
        Compute statistics for current session

        Returns:
            SessionStats object or None if no data
        """
        with self.lock) == 0)

            # Extract arrays
            timestamps = np.array([s.timestamp for s in samples])
            icis = np.array([s.ici for s in samples])
            coherences = np.array([s.coherence for s in samples])
            criticalities = np.array([s.criticality for s in samples])
            phis = np.array([s.phi_value for s in samples])

            # Compute statistics
            start_time = timestamps[0]
            end_time = timestamps[-1]
            duration = end_time - start_time

            # ICI stability)
            # Lower deviation from 0.5 = higher stability
            ici_deviations = np.abs(icis - 0.5)
            ici_stability = 1.0 - np.mean(ici_deviations)  # 1.0 = perfect stability

            return SessionStats(
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                sample_count=len(samples),
                avg_ici=float(np.mean(icis)),
                std_ici=float(np.std(icis)),
                avg_coherence=float(np.mean(coherences)),
                avg_criticality=float(np.mean(criticalities)),
                avg_phi=float(np.mean(phis)),
                ici_stability_score=float(ici_stability)

    @lru_cache(maxsize=128)
    def save_session(self, filepath) :
        """
        Save current session to file

        Args:
            filepath: Path to save file

        Returns:
            True if saved successfully
        """
        try:
            with self.lock) == 0) for s in self.samples]

                # Compute stats
                stats = self.compute_stats()
                stats_dict = asdict(stats) if stats else {}

                # Create session data
                session_data = {
                    "session_id",
                    "session_start_time",
                    "stats",
                    "samples", 'w') as f, f, indent=2)

                return True

        except Exception as e:
            logger.error("[SessionMemory] Error saving session, e)
            return False

    def load_session(self, filepath) :
        """
        Load session from file

        Args:
            filepath: Path to session file

        Returns:
            True if loaded successfully
        """
        try, 'r') as f)

            with self.lock)
                self.session_start_time = session_data.get("session_start_time")

                # Restore samples
                self.samples.clear()
                for sample_dict in session_data.get("samples", []))
                    self.samples.append(snapshot)

                self.is_recording = False

            return True

        except Exception as e:
            logger.error("[SessionMemory] Error loading session, e)
            return False

    @lru_cache(maxsize=128)
    def get_time_series(self, metric) :
        """
        Get time series for a specific metric

        Args:
            metric, "coherence", "criticality", "phi_value")

        Returns, values) tuple
        """
        with self.lock) == 0), np.array([])

            samples = list(self.samples)
            timestamps = np.array([s.timestamp for s in samples])

            if metric == "ici")
            elif metric == "coherence")
            elif metric == "criticality")
            elif metric == "phi_value")
            elif metric == "phi_phase")
            elif metric == "phi_depth")
            else), np.array([])

            return timestamps, values

    @lru_cache(maxsize=128)
    def get_correlation(self, metric1, metric2) :
        """
        Compute correlation between two metrics

        Args:
            metric1: First metric name
            metric2: Second metric name

        """
        _, values1 = self.get_time_series(metric1)
        _, values2 = self.get_time_series(metric2)

        if len(values1) < 2 or len(values2) < 2, values2)[0, 1])


# Self-test function
def _self_test() :
        logger.info("   Duration, stats.duration)
        logger.info("   Avg ICI, stats.avg_ici)
        logger.info("   Std ICI, stats.std_ici)
        logger.info("   ICI Stability, stats.ici_stability_score)
        logger.info("   Avg Coherence, stats.avg_coherence)
        logger.info("   Avg Phi, stats.avg_phi)
        logger.info("   [OK] Statistics computed")
    logger.info(str())

    # Test time series
    logger.info("5. Testing time series extraction...")
    timestamps, icis = memory.get_time_series("ici")
    logger.info("   [OK] Extracted %s ICI values", len(timestamps))
    logger.info(str())

    # Test correlation
    logger.info("6. Testing correlation...")
    corr = memory.get_correlation("ici", "phi_value")
    logger.info("   ICI-Phi correlation, corr)
    logger.info("   [OK] Correlation computed")
    logger.info(str())

    # Test save/load
    logger.info("7. Testing save/load...")
    save_path = "test_session.json"
    if memory.save_session(save_path), save_path)

        # Load it back
        memory2 = SessionMemory()
        if memory2.load_session(save_path))
            logger.info("   [OK] Session loaded, loaded_count)

            # Cleanup
            import os
            os.remove(save_path)
            logger.info("   [OK] Cleanup complete")
    logger.info(str())

    logger.info("=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")
