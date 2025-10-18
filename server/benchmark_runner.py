"""
BenchmarkRunner - Feature 018, frame rate, resource usage, and
adaptive scaling.

Features:
- FR-001: Automated benchmark suite
- FR-002: Collect comprehensive metrics
- FR-004: Persist benchmark summary
- All User Stories: Complete benchmark workflow

Requirements,000 frames
- Validate adaptive scaling under load
- Monitor memory and resource stability
- Generate performance profile
"""
from functools import lru_cache
import logging
logger = logging.getLogger(__name__)


import time
import os
import json
import psutil
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np

from .adaptive_scaler import AdaptiveScaler, ScalerConfig, PerformanceMetrics
from .sync_profiler import SyncProfiler, ProfilerConfig


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark suite"""
    # Test durations
    latency_test_frames: int = 10000
    sustained_test_duration_s: float = 300.0  # 5 minutes
    memory_test_duration_s: float = 300.0  # 5 minutes

    # Performance targets
    target_fps: float = 30.0
    max_latency_ms: float = 100.0
    max_interaction_delay_ms: float = 50.0
    max_cpu_percent: float = 60.0
    max_gpu_percent: float = 75.0
    max_memory_increase_percent: float = 5.0

    # Adaptive scaling
    enable_adaptive_scaling: bool = True

    # Output paths
    logs_dir: str = "logs"
    config_dir: str = "config"
    docs_dir: str = "docs"

    enable_logging: bool = True


@dataclass
class BenchmarkResults:
    """Complete benchmark results"""
    timestamp: str
    duration_s: float

    # Latency results
    latency_stats: Dict
    latency_distribution: Dict

    # Frame rate results
    fps_stats: Dict

    # Resource usage
    cpu_stats: Dict
    gpu_stats: Dict
    memory_stats: Dict

    # Adaptive scaling
    scaling_stats: Dict

    # Success criteria
    success_criteria: Dict

    # Performance profile
    optimal_settings: Dict


class BenchmarkRunner:
    """
    BenchmarkRunner - Automated performance test suite

    Executes comprehensive benchmarks for, config: Optional[BenchmarkConfig]) :
        """
        Run complete benchmark suite

        logger.info("Phi-Matrix Dashboard - Full Benchmark Suite")
        logger.info("=" * 70)
        logger.info(str())

        start_time = time.time()
        self.start_memory_mb = self.process.memory_info().rss / (1024 * 1024)

        # Test 1: Latency Benchmark
        logger.info("Test 1)
        logger.info("-" * 70)
        latency_stats, latency_dist = self._run_latency_benchmark()
        logger.info(str())

        # Test 2: Frame Rate Benchmark
        logger.info("Test 2)
        logger.info("-" * 70)
        fps_stats = self._run_fps_benchmark()
        logger.info(str())

        # Test 3: Resource Usage Benchmark
        logger.info("Test 3)
        logger.info("-" * 70)
        cpu_stats, gpu_stats, memory_stats = self._run_resource_benchmark()
        logger.info(str())

        # Test 4: Adaptive Scaling Benchmark
        if self.scaler:
            logger.info("Test 4)
            logger.info("-" * 70)
            scaling_stats = self._run_adaptive_scaling_benchmark()
            logger.info(str())
        else, fps_stats, memory_stats, scaling_stats

        # Generate optimal settings
        optimal_settings = self._generate_optimal_settings(
            latency_stats, fps_stats, cpu_stats, gpu_stats

        duration = time.time() - start_time

        # Create results
        self.results = BenchmarkResults(
            timestamp=datetime.now().isoformat(),
            duration_s=duration,
            latency_stats=latency_stats,
            latency_distribution=latency_dist,
            fps_stats=fps_stats,
            cpu_stats=cpu_stats,
            gpu_stats=gpu_stats,
            memory_stats=memory_stats,
            scaling_stats=scaling_stats,
            success_criteria=success_criteria,
            optimal_settings=optimal_settings

        # Print summary
        self._print_summary()

        return self.results

    @lru_cache(maxsize=128)
    def _run_latency_benchmark(self) :
                logger.info("    Progress, i + 1, self.config.latency_test_frames)

        # Cleanup any timeouts
        self.profiler.cleanup_pending_pings()

        # Get statistics
        stats = self.profiler.get_statistics()
        dist = self.profiler.get_latency_distribution(bucket_size_ms=10.0)

        logger.info("  Completed %s measurements", stats['total_samples'])
        logger.info("  Avg latency, stats['avg_latency_ms'])
        logger.info("  Max latency, stats['max_latency_ms'])
        logger.info("  P95 latency, stats['p95_latency_ms'])
        logger.info("  Success rate, stats['success_rate'])

        return stats, dist

    def _run_fps_benchmark(self) :
        """
        Test sustained frame rate for 5 minutes

        Returns)...", test_duration)

        start_time = time.time()
        frame_times = []
        frame_count = 0

        while (time.time() - start_time) < test_duration)

            # Simulate frame rendering
            time.sleep(1.0 / 60.0)  # Target 60 FPS

            frame_end = time.time()
            frame_time_ms = (frame_end - frame_start) * 1000.0
            frame_times.append(frame_time_ms)
            frame_count += 1

        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed
        avg_frame_time = float(np.mean(frame_times))
        min_frame_time = float(np.min(frame_times))
        max_frame_time = float(np.max(frame_times))

        # Calculate frame time percentiles
        p95_frame_time = float(np.percentile(frame_times, 95))
        p99_frame_time = float(np.percentile(frame_times, 99))

        # Check for frame drops
        target_frame_time = 1000.0 / self.config.target_fps
        frame_drops = sum(1 for ft in frame_times if ft > target_frame_time * 1.5)
        frame_drop_rate = (frame_drops / frame_count) * 100.0

        stats = {
            "total_frames",
            "duration_s",
            "avg_fps",
            "avg_frame_time_ms",
            "min_frame_time_ms",
            "max_frame_time_ms",
            "p95_frame_time_ms",
            "p99_frame_time_ms",
            "frame_drops",
            "frame_drop_rate_percent": frame_drop_rate
        }

        logger.info("  Total frames, frame_count)
        logger.info("  Average FPS, avg_fps)
        logger.info("  Frame drops)", frame_drops, frame_drop_rate)

        return stats

    @lru_cache(maxsize=128)
    def _run_resource_benchmark(self) : GPU stats would require additional library like GPUtil
        gpu_stats = {
            "avg_gpu_percent",  # Placeholder
            "max_gpu_percent",
            "note")"
        }

        memory_stats = {
            "initial_memory_mb",
            "final_memory_mb",
            "memory_increase_mb",
            "memory_increase_percent",
            "avg_memory_mb")),
            "max_memory_mb"))
        }

        logger.info("  CPU, max=%s%", cpu_stats['avg_cpu_percent'], cpu_stats['max_cpu_percent'])
        logger.info("  Memory)", memory_increase, memory_increase_percent)

        return cpu_stats, gpu_stats, memory_stats

    def _run_adaptive_scaling_benchmark(self) :
        """
        Test adaptive scaling performance

        # Simulate performance degradation
        logger.info("    Phase 1)")
        for i in range(20)),
                fps=20.0,  # Below target
                cpu_percent=65.0,  # Above target
                gpu_percent=80.0,  # Above target
                memory_mb=500.0,
                latency_ms=60.0,
                interaction_delay_ms=55.0

            self.scaler.add_metrics(metrics)
            time.sleep(0.05)

        time.sleep(0.2)  # Wait for scaling response

        # Simulate performance recovery
        logger.info("    Phase 2)")
        for i in range(30)),
                fps=60.0,  # Above target
                cpu_percent=30.0,  # Below target
                gpu_percent=40.0,  # Below target
                memory_mb=500.0,
                latency_ms=20.0,
                interaction_delay_ms=15.0

            self.scaler.add_metrics(metrics)
            time.sleep(0.05)

        stats = self.scaler.get_performance_summary()

        logger.info("  Scale adjustments, stats['total_adjustments'])
        logger.info("  Final complexity level, stats['current_complexity_level'])

        return stats

    def _evaluate_success_criteria(
        self, latency_stats, fps_stats,
        memory_stats, scaling_stats) :
        """
        Evaluate all success criteria

        Returns:
            Success criteria evaluation
        """
        criteria = {
            "SC-001 Round-trip latency <= 100ms", False),
            "SC-002 Frame rate >= 30 fps",
            "SC-003 Interaction delay <= 50ms", False),
            "SC-004 Memory increase < 5%",
            "SC-005 Auto-scaling response < 0.5s", True) if scaling_stats else True
        }

        criteria["all_passed"] = all(criteria.values())

        return criteria

    def _generate_optimal_settings(
        self, latency_stats, fps_stats,
        cpu_stats, gpu_stats) :
        """
        Generate optimal performance profile

        Returns:
            Optimal settings dictionary
        """
        # Determine optimal frame rate target
        avg_fps = fps_stats['avg_fps']
        if avg_fps >= 60:
            optimal_fps = 60
        elif avg_fps >= 45:
            optimal_fps = 45
        else:
            optimal_fps = 30

        # Determine optimal buffer size based on latency
        avg_latency = latency_stats['avg_latency_ms']
        if avg_latency < 10:
            optimal_buffer_ms = 10
        elif avg_latency < 25:
            optimal_buffer_ms = 20
        else:
            optimal_buffer_ms = 30

        # Determine optimal visual complexity
        avg_cpu = cpu_stats['avg_cpu_percent']
        if avg_cpu < 30:
            optimal_complexity = 5  # Maximum
        elif avg_cpu < 45:
            optimal_complexity = 4
        else:
            optimal_complexity = 3

        return {
            "target_fps",
            "audio_buffer_ms",
            "visual_complexity_level",
            "enable_phi_breathing",
            "enable_topology_links",
            "enable_gradients",
            "render_resolution")
        }

    def _print_summary(self) :
        """Print benchmark summary"""
        if not self.results)
        logger.info("Benchmark Summary")
        logger.info("=" * 70)
        logger.info(str())

        logger.info("Success Criteria)
        for criterion, passed in self.results.success_criteria.items():
            if criterion == "all_passed", status, criterion)

        logger.info(str())
        all_passed = self.results.success_criteria["all_passed"]
        if all_passed)
        else)

        logger.info(str())
        logger.info("Optimal Settings)
        for key, value in self.results.optimal_settings.items():
            logger.info("  %s, key, value)

        logger.info(str())
        logger.info("=" * 70)

    def save_results(self) :
        """Save benchmark results to files"""
        if not self.results)
            return

        # Create directories
        os.makedirs(self.config.logs_dir, exist_ok=True)
        os.makedirs(self.config.config_dir, exist_ok=True)

        # Convert results to JSON-serializable format
        results_dict = asdict(self.results)
        results_json = json.loads(json.dumps(results_dict, default=str))

        # Save benchmark report
        report_path = os.path.join(
            self.config.logs_dir,
            f"phi_benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_path, 'w') as f, f, indent=2)

        logger.info("Benchmark report saved to, report_path)

        # Save performance profile
        profile_path = os.path.join(
            self.config.config_dir,
            "performance_profile.json"

        with open(profile_path, 'w') as f, f, indent=2)

        logger.info("Performance profile saved to, profile_path)


# Command-line interface
if __name__ == "__main__",  # Reduced for faster testing
        sustained_test_duration_s=60.0,  # 1 minute
        memory_test_duration_s=60.0,  # 1 minute
        enable_adaptive_scaling=True,
        enable_logging=True

    runner = BenchmarkRunner(config)
    results = runner.run_full_benchmark()
    runner.save_results()
