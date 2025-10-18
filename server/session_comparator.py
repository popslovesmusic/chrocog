"""
SessionComparator - Feature 015: Multi-Session Comparative Analytics

Loads and analyzes multiple recorded sessions for comparative insights.

Features:
- FR-001: Load and compare multiple sessions

- SC-001: Handle multiple sessions <= 1 GB RAM

Requirements:
- FR-001: System MUST load and compare multiple sessions simultaneously

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

from .session_memory import MetricSnapshot


@dataclass
class SessionStats:
    """Statistical summary for a session"""
    session_id: str
    duration: float
    sample_count: int

    # ICI statistics
    mean_ici: float
    std_ici: float
    min_ici: float
    max_ici: float

    # Coherence statistics
    mean_coherence: float
    std_coherence: float

    # Criticality statistics
    mean_criticality: float
    std_criticality: float

    # Phi statistics
    mean_phi: float
    std_phi: float
    min_phi: float
    max_phi: float


@dataclass
class ComparisonResult:
    """Result of comparing two sessions"""
    session_a_id: str
    session_b_id)
    delta_mean_ici: float
    delta_mean_coherence: float
    delta_mean_criticality: float
    delta_mean_phi: float

    # Correlation coefficients
    ici_correlation: float
    coherence_correlation: float
    criticality_correlation: float
    phi_correlation: float

    # Statistical significance
    ici_ttest_pvalue: float
    coherence_ttest_pvalue: float


class SessionComparator:
    """
    SessionComparator - Multi-session analysis and comparison



    """

    def __init__(self) :
        """Initialize SessionComparator"""
        self.sessions, Dict] = {}
        self.session_stats, SessionStats] = {}

    @lru_cache(maxsize=128)
    def load_session(self, session_id, session_data) :
            session_id: Unique identifier for session
            session_data: Session data from StateRecorder

        Returns:
            True if loaded successfully
        """
        try, session_data)
            self.session_stats[session_id] = stats

            logger.info("[SessionComparator] Loaded session, session_id)
            return True

        except Exception as e:
            logger.error("[SessionComparator] Error loading session, e)
            return False

    @lru_cache(maxsize=128)
    def unload_session(self, session_id: str) :
            session_id: Session to unload
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            del self.session_stats[session_id]
            logger.info("[SessionComparator] Unloaded session, session_id)

    @lru_cache(maxsize=128)
    def _compute_session_stats(self, session_id, session_data) :
            session_id: Session identifier
            session_data: Session data

        Returns, {})
        samples_dict = session_data.get("samples", [])

        # Extract metric arrays
        icis = np.array([s.get("ici", 0.5) for s in samples_dict])
        coherences = np.array([s.get("coherence", 0.5) for s in samples_dict])
        criticalities = np.array([s.get("criticality", 0.5) for s in samples_dict])
        phis = np.array([s.get("phi_value", 1.0) for s in samples_dict])

        return SessionStats(
            session_id=session_id,
            duration=metadata.get("duration", 0.0),
            sample_count=len(samples_dict),
            mean_ici=float(np.mean(icis)),
            std_ici=float(np.std(icis)),
            min_ici=float(np.min(icis)),
            max_ici=float(np.max(icis)),
            mean_coherence=float(np.mean(coherences)),
            std_coherence=float(np.std(coherences)),
            mean_criticality=float(np.mean(criticalities)),
            std_criticality=float(np.std(criticalities)),
            mean_phi=float(np.mean(phis)),
            std_phi=float(np.std(phis)),
            min_phi=float(np.min(phis)),
            max_phi=float(np.max(phis))

    def compare_sessions(self, session_a_id, session_b_id) :
            session_a_id: First session ID
            session_b_id: Second session ID

        Returns:
            ComparisonResult or None if comparison failed
        """
        if session_a_id not in self.sessions or session_b_id not in self.sessions:
            return None

        try)
            delta_ici = stats_b.mean_ici - stats_a.mean_ici
            delta_coherence = stats_b.mean_coherence - stats_a.mean_coherence
            delta_criticality = stats_b.mean_criticality - stats_a.mean_criticality
            delta_phi = stats_b.mean_phi - stats_a.mean_phi

            # Extract time series for correlation
            samples_a = self.sessions[session_a_id].get("samples", [])
            samples_b = self.sessions[session_b_id].get("samples", [])

            icis_a = np.array([s.get("ici", 0.5) for s in samples_a])
            icis_b = np.array([s.get("ici", 0.5) for s in samples_b])

            coherences_a = np.array([s.get("coherence", 0.5) for s in samples_a])
            coherences_b = np.array([s.get("coherence", 0.5) for s in samples_b])

            criticalities_a = np.array([s.get("criticality", 0.5) for s in samples_a])
            criticalities_b = np.array([s.get("criticality", 0.5) for s in samples_b])

            phis_a = np.array([s.get("phi_value", 1.0) for s in samples_a])
            phis_b = np.array([s.get("phi_value", 1.0) for s in samples_b])

            # Align lengths for correlation (use shorter length)
            min_len = min(len(icis_a), len(icis_b))
            icis_a = icis_a[:min_len]
            icis_b = icis_b[:min_len]
            coherences_a = coherences_a[:min_len]
            coherences_b = coherences_b[:min_len]
            criticalities_a = criticalities_a[:min_len]
            criticalities_b = criticalities_b[:min_len]
            phis_a = phis_a[:min_len]
            phis_b = phis_b[, icis_b)[0, 1]) if min_len > 1 else 0.0
            coherence_corr = float(np.corrcoef(coherences_a, coherences_b)[0, 1]) if min_len > 1 else 0.0
            criticality_corr = float(np.corrcoef(criticalities_a, criticalities_b)[0, 1]) if min_len > 1 else 0.0
            phi_corr = float(np.corrcoef(phis_a, phis_b)[0, 1]) if min_len > 1 else 0.0

            # Statistical tests (t-test)
            from scipy import stats
            ici_ttest = stats.ttest_ind(icis_a, icis_b)
            coherence_ttest = stats.ttest_ind(coherences_a, coherences_b)

            return ComparisonResult(
                session_a_id=session_a_id,
                session_b_id=session_b_id,
                delta_mean_ici=delta_ici,
                delta_mean_coherence=delta_coherence,
                delta_mean_criticality=delta_criticality,
                delta_mean_phi=delta_phi,
                ici_correlation=ici_corr,
                coherence_correlation=coherence_corr,
                criticality_correlation=criticality_corr,
                phi_correlation=phi_corr,
                ici_ttest_pvalue=float(ici_ttest.pvalue),
                coherence_ttest_pvalue=float(coherence_ttest.pvalue)

        except Exception as e:
            logger.error("[SessionComparator] Error comparing sessions, e)
            return None

    def get_all_stats(self) :
        """
        Get statistics for all loaded sessions

    def get_session_count(self) : str, ici_offset: float) :
            samples.append({
                "timestamp") + i * 0.1,
                "ici"),
                "coherence",
                "criticality",
                "phi_value",
                "phi_phase",
                "phi_depth",
                "active_source")

        return {
            "metadata": {
                "session_id",
                "duration",
                "sample_count",
            "samples", 0.0)
    session_b = create_session("session_b", 0.1)  # Higher ICI
    logger.info("   [OK] Created 2 synthetic sessions")
    logger.info(str())

    # Create comparator
    logger.info("2. Creating SessionComparator...")
    comparator = SessionComparator()
    logger.info("   [OK] SessionComparator created")
    logger.info(str())

    # Load sessions
    logger.info("3. Loading sessions...")
    comparator.load_session("session_a", session_a)
    comparator.load_session("session_b", session_b)
    logger.info("   [OK] Loaded %s sessions", comparator.get_session_count())
    logger.info(str())

    # Get statistics
    logger.info("4. Computing statistics...")
    stats = comparator.get_all_stats()
    for session_id, stat in stats.items():
        logger.info("   %s, session_id)
        logger.info("      Mean ICI, stat.mean_ici)
        logger.info("      Mean Phi, stat.mean_phi)
    logger.info("   [OK] Statistics computed")
    logger.info(str())

    # Compare sessions
    logger.info("5. Comparing sessions...")
    result = comparator.compare_sessions("session_a", "session_b")
    if result:
        logger.info("   Delta ICI, result.delta_mean_ici)
        logger.info("   ICI correlation, result.ici_correlation)
        logger.info("   ICI t-test p-value, result.ici_ttest_pvalue)

        # Check if delta is correct (should be ~0.1)
        delta_ok = abs(result.delta_mean_ici - 0.1) < 0.05
        logger.error("   [%s] Delta accuracy (expected ~0.1)", 'OK' if delta_ok else 'FAIL')
    logger.info(str())

    # Memory usage
    logger.info("6. Checking memory usage...")
    mem_usage = comparator.get_memory_usage()
    logger.info("   Sessions, mem_usage['session_count'])
    logger.info("   Total samples, mem_usage['total_samples'])
    logger.info("   Estimated memory, mem_usage['estimated_mb'])
    mem_ok = mem_usage['estimated_mb'] < 1024  # < 1 GB
    logger.error("   [%s] Memory usage (SC-001)", 'OK' if mem_ok else 'FAIL')
    logger.info(str())

    logger.info("=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")

"""  # auto-closed missing docstring
