# ==========================================================
# chromatic_field_processor_fixed.py  (Section 1/4)
# ==========================================================
# Purpose: Real-time chromatic field computation and DSP
# corrections applied for type hints, formatting, and logger safety
# ==========================================================

import numpy as np
import asyncio
import time
import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ChromaticFieldProcessor:
    def __init__(
        self,
        num_channels: int = 8,
        sample_rate: int = 48000,
        fft_size: int = 2048,
        overlap: float = 0.5,
        gain: float = 1.0,
        chromatic_weight: float = 1.0,
        enable_phi_sync: bool = True,
    ) -> None:
        self.num_channels = num_channels
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.overlap = overlap
        self.gain = gain
        self.chromatic_weight = chromatic_weight
        self.enable_phi_sync = enable_phi_sync

        self.last_frame_time: Optional[float] = None
        self.phi_sync_state: Dict[str, Any] = {
            "phase": 0.0,
            "last_update": time.time(),
            "enabled": enable_phi_sync,
        
        }
                # ----------------------------------------
        # Auto-Φ learner defaults (prevents AttributeError)
        # ----------------------------------------
        self.auto_phi_enabled = False
        self._last_metrics = {"valid": False}


        # Buffers
        self.input_buffer: List[np.ndarray] = []
        self.output_buffer: List[np.ndarray] = []

        # Diagnostic and metrics tracking
        self.block_count = 0
        self.avg_process_time = 0.0
        self.latency_ms = 0.0
        self.max_latency_ms = 0.0
        self.last_fft: Optional[np.ndarray] = None
        self.last_ifft: Optional[np.ndarray] = None

        logger.info(
            "ChromaticFieldProcessor initialized — channels=%d, rate=%dHz, FFT=%d",
            num_channels,
            sample_rate,
            fft_size,
        )

    # ==========================================================
    # Core Processing Pipeline
    # ==========================================================

    def process_block(self, input_block: np.ndarray) -> np.ndarray:
        """
        Main entry point for per-block DSP computation.
        Handles FFT, chromatic weighting, inverse FFT, and timing.
        """
        start_time = time.perf_counter()
        try:
            if input_block.ndim == 1:
                input_block = np.expand_dims(input_block, axis=0)

            # Apply gain normalization
            block = np.clip(input_block * self.gain, -1.0, 1.0)

            # FFT transform
            spectrum = np.fft.rfft(block, n=self.fft_size)
            magnitude = np.abs(spectrum)
            phase = np.angle(spectrum)

            # Apply chromatic weighting
            weighted_magnitude = magnitude * self.chromatic_weight

            # Reconstruct signal
            processed = np.fft.irfft(weighted_magnitude * np.exp(1j * phase), n=self.fft_size)
            processed = processed[:, : block.shape[1]]

            # Store last outputs for diagnostics
            self.last_fft = spectrum
            self.last_ifft = processed
            self.output_buffer.append(processed)

            # Track performance
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            self.block_count += 1
            self.avg_process_time = (
                (self.avg_process_time * (self.block_count - 1)) + elapsed_ms
            ) / self.block_count
            self.max_latency_ms = max(self.max_latency_ms, elapsed_ms)

            logger.info(f"   ✓ Block processed in {elapsed_ms:.2f}ms")

            return processed

        except Exception as e:
            logger.exception("Error processing block: %s", e)
            return np.zeros_like(input_block)







# ======================== END OF SECTION 1 ========================
# (Next: Section 2 — Φ synchronization, async metrics, and smoothing)
# Paste below this divider when ready
# ==========================================================
# chromatic_field_processor_fixed.py  (Section 2/4)
# ==========================================================
# Φ-Synchronization, async broadcast support, and safety checks
# ==========================================================

    async def update_phi_sync(self, delta_phase: float = 0.0) -> None:
        """
        Update Φ-phase synchronization in real time.
        Adjusts internal phase offset and timestamps for coherence monitoring.
        """
        if not self.phi_sync_state.get("enabled", False):
            return

        now = time.time()
        dt = now - self.phi_sync_state["last_update"]

        self.phi_sync_state["phase"] = (
            (self.phi_sync_state["phase"] + delta_phase + dt * 0.1) % (2 * np.pi)
        )
        self.phi_sync_state["last_update"] = now

        logger.debug(
            f"Φ-sync updated → phase={self.phi_sync_state['phase']:.4f}, dt={dt:.3f}s"
        )

    async def smooth_transition(self, signal: np.ndarray, alpha: float = 0.1) -> np.ndarray:
        """
        Simple exponential smoothing filter for temporal continuity across frames.
        """
        if not hasattr(self, "_last_signal"):
            self._last_signal = np.zeros_like(signal)

        smoothed = alpha * signal + (1 - alpha) * self._last_signal
        self._last_signal = smoothed
        return smoothed

    # ==========================================================
    # Async Broadcast and Integration Hooks
    # ==========================================================

    async def broadcast_state(self, websocket=None) -> None:
        """
        Send real-time state to connected WebSocket clients.
        Ensures thread-safe, async-safe delivery.
        """
        if websocket is None:
            logger.warning("broadcast_state called without WebSocket; skipping.")
            return

        try:
            state = {
                "phase": self.phi_sync_state["phase"],
                "avg_process_time_ms": round(self.avg_process_time, 3),
                "max_latency_ms": round(self.max_latency_ms, 3),
                "block_count": self.block_count,
            }
            await websocket.send_json(state)
            logger.debug("Broadcasted Φ-state → %s", state)
        except Exception as e:
            logger.error("WebSocket broadcast failed: %s", e)

    async def run_realtime_loop(
        self,
        input_stream,
        websocket=None,
        refresh_interval: float = 0.05,
    ) -> None:
        """
        Primary async loop:
        - Reads blocks from input_stream
        - Processes via ChromaticFieldProcessor
        - Periodically broadcasts Φ-sync metrics
        """
        logger.info("Starting real-time processing loop…")
        try:
            async for block in input_stream:
                processed = self.process_block(block)
                smoothed = await self.smooth_transition(processed)

                if websocket:
                    await self.broadcast_state(websocket)

                await self.update_phi_sync(delta_phase=np.mean(smoothed) * 0.01)
                await asyncio.sleep(refresh_interval)
        except asyncio.CancelledError:
            logger.warning("Real-time loop cancelled.")
        except Exception as e:
            logger.exception("Runtime error in real-time loop: %s", e)
        finally:
            logger.info("Real-time loop stopped.")







# ======================== END OF SECTION 2 ========================
# (Next: Section 3 — Metrics computation, adaptive learning, and performance diagnostics)
# Paste below this divider when ready
# ==========================================================
# chromatic_field_processor_fixed.py  (Section 3/4)
# ==========================================================
# Metrics (ICI, phase coherence, centroid, criticality, state)
# + Small, isolated Auto-Φ learner (optional)
# ==========================================================

    # -----------------------------
    # Utility: safe norms and helpers
    # -----------------------------
    @staticmethod
    def _safe_norm(vec: "np.ndarray") -> float:
        denom = float(np.linalg.norm(vec))
        return denom if denom > 1e-12 else 1e-12

    @staticmethod
    def _safe_mean(values: "np.ndarray") -> float:
        if values.size == 0:
            return 0.0
        return float(np.mean(values))

    @staticmethod
    def _phase_signs(frame: "np.ndarray") -> "np.ndarray":
        # sign proxy from time-domain amplitude (fast, robust)
        return np.where(frame >= 0.0, 1.0, -1.0)

    # -----------------------------------------
    # Metrics: ICI, phase coherence, centroid…
    # -----------------------------------------
    def compute_metrics(
        self,
        outputs: "np.ndarray",
        *,
        sample_rate: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Compute per-block metrics from an [frames x channels] array.
        - outputs: float32/float64, shape (N, C). If mono, treat as (N,1).
        """
        if outputs is None:
            return {"valid": False, "reason": "no_outputs"}

        if outputs.ndim == 1:
            outputs = outputs.reshape(-1, 1)

        n_frames, n_channels = outputs.shape
        if n_frames == 0 or n_channels == 0:
            return {"valid": False, "reason": "empty"}

        sr = int(sample_rate or getattr(self, "sample_rate", 48_000))

        # --- ICI (Integrated Chromatic Information) ---
        # energy per channel (L2 norm), then pairwise normalized product
        energies = np.sqrt(np.sum(outputs * outputs, axis=0))  # (C,)
        mean_energy = float(np.mean(energies)) if energies.size else 0.0
        ici_pairs = []
        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                num = energies[i] * energies[j]
                den = (energies[i] + energies[j] + 1e-9)
                ici_pairs.append(num / den)
        ici_raw = self._safe_mean(np.asarray(ici_pairs, dtype=np.float64))
        # normalize ICI roughly to [0..1]
        ici = float(np.clip(ici_raw / (mean_energy + 1e-6), 0.0, 1.0))

        # --- Phase coherence (adjacent channels sign correlation) ---
        # sign proxy in time-domain
        signs = self._phase_signs(outputs)  # (N, C)
        if n_channels > 1:
            corrs = []
            for c in range(n_channels - 1):
                a = signs[:, c].astype(np.float64)
                b = signs[:, c + 1].astype(np.float64)
                # cosine similarity of ±1 streams equals mean(a*b)
                corr = float(np.mean(a * b))
                # map from [-1..1] -> [0..1]
                corrs.append(0.5 * (corr + 1.0))
            phase_coherence = self._safe_mean(np.asarray(corrs, dtype=np.float64))
        else:
            phase_coherence = 1.0  # single channel is trivially coherent with itself

        # --- Spectral centroid (mono mix) ---
        mono = np.mean(outputs, axis=1)
        # Hann window
        w = np.hanning(n_frames)
        spec = np.fft.rfft(mono * w)
        mag = np.abs(spec)
        freqs = np.fft.rfftfreq(n_frames, d=1.0 / sr)
        mag_sum = float(np.sum(mag))
        if mag_sum <= 1e-12:
            spectral_centroid_hz = 0.0
        else:
            spectral_centroid_hz = float(np.sum(freqs * mag) / mag_sum)
        spectral_centroid_norm = float(np.clip(spectral_centroid_hz / (sr / 2.0), 0.0, 1.0))

        # --- Chromatic energy (aggregate amplitude) ---
        chromatic_energy = float(np.mean(np.abs(outputs)))

        # --- Consciousness state classification ---
        state = self._classify_state(
            ici=ici,
            coherence=phase_coherence,
            centroid_hz=spectral_centroid_hz,
        )

        # --- Criticality (edge-of-chaos ~ ICI≈0.5) ---
        criticality = float(1.0 - 2.0 * abs(ici - 0.5))
        criticality = float(np.clip(criticality, 0.0, 1.0))

        # --- Aggregate & cache ---
        metrics = {
            "ici": ici,
            "phase_coherence": phase_coherence,
            "spectral_centroid": spectral_centroid_hz,
            "spectral_centroid_norm": spectral_centroid_norm,
            "chromatic_energy": chromatic_energy,
            "criticality": criticality,
            "consciousness_state": state,
            "valid": True,
        }
        self._last_metrics = metrics
        logger.debug("Metrics → %s", metrics)
        return metrics

    # ----------------------------
    # Simple state classifier
    # ----------------------------
    @staticmethod
    def _classify_state(ici: float, coherence: float, centroid_hz: float) -> str:
        # thresholds mirror your spec’s intent; adjust freely
        if ici < 0.1 and coherence < 0.2:
            return "COMA"
        if centroid_hz < 10.0 and coherence < 0.4:
            return "SLEEP"
        if ici < 0.3 and coherence < 0.5:
            return "DROWSY"
        if 0.3 <= ici <= 0.7 and coherence >= 0.4:
            return "AWAKE"
        if ici > 0.7 and coherence > 0.7:
            return "ALERT"
        if ici > 0.9 and coherence > 0.9:
            return "HYPERSYNC"
        return "UNKNOWN"

    # ==========================================================
    # Auto-Φ Learner (minimal, isolated, easy to disable)
    # ==========================================================
    def set_auto_phi_enabled(self, enabled: bool) -> None:
        self.auto_phi_enabled = bool(enabled)
        logger.info("Auto-Φ learner %s", "ENABLED" if self.auto_phi_enabled else "DISABLED")

    def auto_phi_step(self, metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        Tiny, safe adaptation step:
          • Drives ICI toward ~0.5 (criticality peak)
          • Nudges internal φ-phase slowly to avoid oscillation
        You can call this once per processed block (if enabled).
        """
        if not self.auto_phi_enabled:
            return
        m = metrics or getattr(self, "_last_metrics", None)
        if not m or not m.get("valid", False):
            return

        target_ici = 0.5
        err = float(m["ici"] - target_ici)

        # Adjust an internal 'phi_depth' knob (bounded)
        depth = float(self.phi_sync_state.get("depth", 0.5))
        k_depth = 0.05   # conservative step
        new_depth = float(np.clip(depth - k_depth * err, 0.0, 1.0))
        self.phi_sync_state["depth"] = new_depth

        # Very slow phase stroll to help explore local basin
        k_phase = 0.01
        self.phi_sync_state["phase"] = float(
            (self.phi_sync_state["phase"] + k_phase * np.sign(-err)) % (2 * np.pi)
        )

        logger.debug(
            "Auto-Φ step: err=%.4f, depth=%.3f→%.3f, phase=%.3f",
            err, depth, new_depth, self.phi_sync_state["phase"]
        )

    # --------------------------------------------
    # Diagnostics: performance and meter snapshots
    # --------------------------------------------
    def get_performance_snapshot(self) -> Dict[str, Any]:
        return {
            "avg_process_time_ms": round(self.avg_process_time, 3),
            "max_latency_ms": round(self.max_latency_ms, 3),
            "block_count": int(self.block_count),
        }

    def get_last_metrics(self) -> Dict[str, Any]:
        return dict(getattr(self, "_last_metrics", {"valid": False}))
# ==========================================================
# chromatic_field_processor_fixed.py  (Section 4/4)
# ==========================================================
# Public interface, test hooks, and self-validation
# ==========================================================

    # ------------------------------------------------------
    # Public Facade (safe wrappers for external calls)
    # ------------------------------------------------------
    def reset_state(self) -> None:
        """Clear buffers, counters, and cached metrics."""
        self.input_buffer.clear()
        self.output_buffer.clear()
        self.block_count = 0
        self.avg_process_time = 0.0
        self.max_latency_ms = 0.0
        self._last_signal = None
        self._last_metrics = {"valid": False}
        logger.info("ChromaticFieldProcessor state reset.")

    def get_state_summary(self) -> Dict[str, Any]:
        """Return a snapshot combining performance and metrics."""
        state = {
            "performance": self.get_performance_snapshot(),
            "metrics": self.get_last_metrics(),
            "phi": {
                "phase": float(self.phi_sync_state.get("phase", 0.0)),
                "depth": float(self.phi_sync_state.get("depth", 0.0)),
                "enabled": bool(self.phi_sync_state.get("enabled", False)),
            },
        }
        logger.debug("State summary → %s", state)
        return state

    # ------------------------------------------------------
    # Validation / sanity self-test
    # ------------------------------------------------------
    def self_test(self) -> Dict[str, Any]:
        """
        Runs a small offline test: generate a sine sweep,
        process through the pipeline, compute metrics, and verify stability.
        """
        logger.info("Running self-test sweep…")

        # generate 1-second sine sweep
        sr = self.sample_rate
        t = np.linspace(0, 1.0, sr, endpoint=False)
        sweep = np.sin(2 * np.pi * (220 * (t**2)))  # chirp-like
        multi = np.stack([sweep * (i + 1) / self.num_channels for i in range(self.num_channels)])

        processed = self.process_block(multi)
        metrics = self.compute_metrics(processed)
        self.auto_phi_step(metrics)

        summary = self.get_state_summary()
        logger.info("Self-test complete.  ICI=%.3f  coherence=%.3f",
                    metrics.get("ici", 0.0), metrics.get("phase_coherence", 0.0))
        return summary


# ==========================================================
# Standalone module check
# ==========================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    proc = ChromaticFieldProcessor()
    result = proc.self_test()
    print("\n=== Self-Test Summary ===")
    for k, v in result.items():
        print(f"{k}: {v}")
    print("=========================\n")
