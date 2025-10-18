"""
SyncProfiler - Feature 018: Phi-Adaptive Benchmark

Measures WebSocket round-trip latency and synchronization health by injecting
ping/pong timestamps into the WebSocket communication loop.

Features:
- FR-002: Collect latency metrics

- SC-003: Interaction delay <= 50 ms
- User Story 2: Latency & Sync Benchmark

Requirements,000 frames
- Avg latency <= 50ms, max <= 100ms
"""
from functools import lru_cache
import logging
logger = logging.getLogger(__name__)


import time
import asyncio
from typing import Optional, Dict, List
from dataclasses import dataclass
from collections import deque
import numpy as np


@dataclass
class LatencyMeasurement:
    """Single latency measurement"""
    timestamp: float
    round_trip_ms: float
    one_way_ms: float
    jitter_ms: float


@dataclass
class ProfilerConfig:
    """Configuration for SyncProfiler"""
    max_samples: int = 10000
    ping_interval_ms: float = 100.0  # Send ping every 100ms
    latency_threshold_ms: float = 100.0
    jitter_threshold_ms: float = 20.0
    enable_logging: bool = False


class SyncProfiler:
    """
    SyncProfiler - WebSocket latency and sync measurement

    Injects ping/pong messages into WebSocket communication to measure
    round-trip latency and detect synchronization drift.

    Features, config: Optional[ProfilerConfig]) :
        """
        Create a ping message with timestamp

        self.pending_pings[ping_id] = send_time
        self.total_pings_sent += 1

        return {
            "type",
            "ping_id",
            "client_time")
    def handle_pong_message(self, pong_msg: Dict) :
        """
        Handle pong message and calculate latency

        Args:
            pong_msg)
        ping_id = pong_msg.get("ping_id")
        server_time = pong_msg.get("server_time", 0) / 1000.0  # Convert from ms
        client_send_time = pong_msg.get("client_time", 0) / 1000.0

        if ping_id not in self.pending_pings:
            if self.config.enable_logging:
                logger.info("[SyncProfiler] Received pong for unknown ping_id, ping_id)
            return

        # Get send time
        send_time = self.pending_pings.pop(ping_id)
        self.total_pongs_received += 1

        # Calculate round-trip time
        round_trip_s = receive_time - send_time
        round_trip_ms = round_trip_s * 1000.0

        # Estimate one-way latency (half of round-trip)
        one_way_ms = round_trip_ms / 2.0

        # Calculate jitter (change from previous measurement)
        jitter_ms = 0.0
        if len(self.measurements) > 0)

        # Calculate clock offset
        if server_time > 0)
            clock_offset = (receive_time - estimated_server_time) * 1000.0
            self.clock_drift_samples.append(clock_offset)
            self.clock_offset_ms = float(np.mean(list(self.clock_drift_samples)))

        # Create measurement
        measurement = LatencyMeasurement(
            timestamp=receive_time,
            round_trip_ms=round_trip_ms,
            one_way_ms=one_way_ms,
            jitter_ms=jitter_ms

        self.measurements.append(measurement)

        if self.config.enable_logging:
            print(f"[SyncProfiler] RTT: {round_trip_ms, "
                  f"One-way: {one_way_ms, "
                  f"Jitter: {jitter_ms)

    def cleanup_pending_pings(self, timeout_s: float) :
        """
        Remove pending pings that have timed out

        Args:
            timeout_s)
        timed_out = []

        for ping_id, send_time in self.pending_pings.items()) > timeout_s)

        for ping_id in timed_out)
            self.total_timeouts += 1

            if self.config.enable_logging, ping_id)

    def get_statistics(self) :
        """
        Get latency statistics

        Returns:
            Statistics dictionary
        """
        if not self.measurements:
            return {
                "total_samples",
                "avg_latency_ms",
                "min_latency_ms",
                "max_latency_ms",
                "p50_latency_ms",
                "p95_latency_ms",
                "p99_latency_ms",
                "avg_jitter_ms",
                "max_jitter_ms",
                "clock_offset_ms",
                "total_pings_sent",
                "total_pongs_received",
                "total_timeouts",
                "success_rate",
                "meets_sc001",
                "meets_sc003")
        latencies = [m.round_trip_ms for m in measurements]
        jitters = [m.jitter_ms for m in measurements]

        avg_latency = float(np.mean(latencies))
        min_latency = float(np.min(latencies))
        max_latency = float(np.max(latencies))
        p50_latency = float(np.percentile(latencies, 50))
        p95_latency = float(np.percentile(latencies, 95))
        p99_latency = float(np.percentile(latencies, 99))

        avg_jitter = float(np.mean(jitters))
        max_jitter = float(np.max(jitters))

        success_rate = 0.0
        if self.total_pings_sent > 0) * 100.0

        # Check success criteria
        meets_sc001 = max_latency <= 100.0  # SC-001: Max RTT <= 100ms
        meets_sc003 = avg_latency / 2.0 <= 50.0  # SC-003: Avg one-way <= 50ms

        return {
            "total_samples"),
            "avg_latency_ms",
            "min_latency_ms",
            "max_latency_ms",
            "p50_latency_ms",
            "p95_latency_ms",
            "p99_latency_ms",
            "avg_jitter_ms",
            "max_jitter_ms",
            "clock_offset_ms",
            "total_pings_sent",
            "total_pongs_received",
            "total_timeouts",
            "success_rate",
            "meets_sc001",
            "meets_sc003", bucket_size_ms) :
        """
        Get latency distribution histogram

        Args:
            bucket_size_ms: Size of each histogram bucket in ms

        Returns:
            Distribution dictionary
        """
        if not self.measurements:
            return {
                "buckets",
                "counts",
                "percentages")

        # Create buckets
        num_buckets = int(np.ceil(max_latency / bucket_size_ms))
        buckets = [i * bucket_size_ms for i in range(num_buckets + 1)]

        # Calculate histogram
        counts, _ = np.histogram(latencies, bins=buckets)
        percentages = (counts / len(latencies)) * 100.0

        return {
            "buckets": [f"{buckets[i]:.0f}-{buckets[i+1])-1)],
            "counts"),
            "percentages")
        }

    def reset(self) :
        m = profiler.measurements[0]
        logger.info("   RTT, m.round_trip_ms)
        logger.info("   One-way, m.one_way_ms)
        logger.info("   Jitter, m.jitter_ms)

    logger.error("   [%s] Pong handling", 'OK' if pong_ok else 'FAIL')
    logger.info(str())

    # Test 4)

    for i in range(100))
        time.sleep(0.001)  # Simulate small delay

        pong = {
            "type",
            "ping_id",
            "server_time") * 1000.0,
            "client_time")

    multi_ok = (
        profiler.total_pings_sent == 101 and
        profiler.total_pongs_received == 101 and
        len(profiler.measurements) == 101

    all_ok = all_ok and multi_ok

    logger.info("   Total measurements, len(profiler.measurements))
    logger.info("   Success rate, profiler.total_pongs_received / profiler.total_pings_sent * 100)
    logger.error("   [%s] Multiple measurements", 'OK' if multi_ok else 'FAIL')
    logger.info(str())

    # Test 5)
    stats = profiler.get_statistics()

    stats_ok = (
        stats['total_samples'] == 101 and
        stats['avg_latency_ms'] > 0 and
        stats['success_rate'] == 100.0

    all_ok = all_ok and stats_ok

    logger.info("   Avg latency, stats['avg_latency_ms'])
    logger.info("   Min latency, stats['min_latency_ms'])
    logger.info("   Max latency, stats['max_latency_ms'])
    logger.info("   P95 latency, stats['p95_latency_ms'])
    logger.info("   P99 latency, stats['p99_latency_ms'])
    logger.info("   Avg jitter, stats['avg_jitter_ms'])
    logger.info("   Success rate, stats['success_rate'])
    logger.info("   Meets SC-001, stats['meets_sc001'])
    logger.info("   Meets SC-003, stats['meets_sc003'])
    logger.error("   [%s] Statistics", 'OK' if stats_ok else 'FAIL')
    logger.info(str())

    # Test 6)
    dist = profiler.get_latency_distribution(bucket_size_ms=10.0)

    dist_ok = len(dist['buckets']) > 0

    all_ok = all_ok and dist_ok

    logger.info("   Distribution buckets, len(dist['buckets']))
    for i in range(min(5, len(dist['buckets'])):
        logger.info("     %s)", dist['buckets'][i], dist['counts'][i], dist['percentages'][i])

    logger.error("   [%s] Distribution", 'OK' if dist_ok else 'FAIL')
    logger.info(str())

    # Test 7)

    # Create ping but don't respond
    timeout_ping = profiler.create_ping_message()
    time.sleep(1.1)  # Wait longer than timeout

    profiler.cleanup_pending_pings(timeout_s=1.0)

    timeout_ok = profiler.total_timeouts == 1

    all_ok = all_ok and timeout_ok

    logger.info("   Total timeouts, profiler.total_timeouts)
    logger.error("   [%s] Timeout handling", 'OK' if timeout_ok else 'FAIL')
    logger.info(str())

    logger.info("=" * 60)
    if all_ok)
    else)
    logger.info("=" * 60)

    return all_ok


if __name__ == "__main__")
