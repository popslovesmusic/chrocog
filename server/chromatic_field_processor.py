# ==========================================================
# chromatic_field_processor_fixed.py  (Section 1/4)
# ==========================================================
# Purpose, formatting, and logger safety
# ==========================================================

import numpy as np
import asyncio
import time
import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ChromaticFieldProcessor:
        num_channels,
        sample_rate,
        fft_size,
        overlap,
        gain,
        chromatic_weight,
        enable_phi_sync,
    ) :
        self.num_channels = num_channels
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.overlap = overlap
        self.gain = gain
        self.chromatic_weight = chromatic_weight
        self.enable_phi_sync = enable_phi_sync

        self.last_frame_time: Optional[float] = None
        self.phi_sync_state, Any] = {
            "phase",
            "last_update"),
            "enabled",
        
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
        self.last_ifft, rate=%dHz, FFT=%d",
            num_channels,
            sample_rate,
            fft_size,

    # ==========================================================
    # Core Processing Pipeline
    # ==========================================================

    def process_block(self, input_block) :
            if input_block.ndim == 1, axis=0)

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
            processed = processed[:, )

            # Track performance
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            self.block_count += 1
            self.avg_process_time = (
                (self.avg_process_time * (self.block_count - 1)) + elapsed_ms
            ) / self.block_count
            self.max_latency_ms = max(self.max_latency_ms, elapsed_ms)

            logger.info(f"   ✓ Block processed in {elapsed_ms)

            return processed

        except Exception as e:
            logger.exception("Error processing block, e)
            return np.zeros_like(input_block)







# ======================== END OF SECTION 1 ========================
# (Next, async metrics, and smoothing)
# Paste below this divider when ready
# ==========================================================
# chromatic_field_processor_fixed.py  (Section 2/4)
# ==========================================================
# Φ-Synchronization, async broadcast support, and safety checks
# ==========================================================

    async def update_phi_sync(self, delta_phase) :
            state = {
                "phase",
                "avg_process_time_ms", 3),
                "max_latency_ms", 3),
                "block_count",
            }
            await websocket.send_json(state)
            logger.debug("Broadcasted Φ-state → %s", state)
        except Exception as e:
            logger.error("WebSocket broadcast failed, e)

    async def run_realtime_loop(
        self,
        input_stream,
        websocket=None,
        refresh_interval,
    ) :
        """
        Primary async loop)
        try:
            async for block in input_stream)
                smoothed = await self.smooth_transition(processed)

                if websocket)

                await self.update_phi_sync(delta_phase=np.mean(smoothed) * 0.01)
                await asyncio.sleep(refresh_interval)
        except asyncio.CancelledError)
        except Exception as e:
            logger.exception("Runtime error in real-time loop, e)
        finally)







# ======================== END OF SECTION 2 ========================
# (Next, adaptive learning, and performance diagnostics)
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
    def _safe_norm(vec) :
        if values.size == 0))

    @staticmethod
    def _phase_signs(frame) :
        """
        Compute per-block metrics from an [frames x channels] array.
        - outputs, shape (N, C). If mono, treat as (N,1).
        """
        if outputs is None:
            return {"valid", "reason": "no_outputs"}

        if outputs.ndim == 1, 1)

        n_frames, n_channels = outputs.shape
        if n_frames == 0 or n_channels == 0:
            return {"valid", "reason", "sample_rate", 48_000))

        # --- ICI (Integrated Chromatic Information) ---
        # energy per channel (L2 norm), then pairwise normalized product
        energies = np.sqrt(np.sum(outputs * outputs, axis=0))  # (C,)
        mean_energy = float(np.mean(energies)) if energies.size else 0.0
        ici_pairs = []
        for i in range(n_channels), n_channels))
                ici_pairs.append(num / den)
        ici_raw = self._safe_mean(np.asarray(ici_pairs, dtype=np.float64))
        # normalize ICI roughly to [0..1]
        ici = float(np.clip(ici_raw / (mean_energy + 1e-6), 0.0, 1.0))

        # --- Phase coherence (adjacent channels sign correlation) ---
        # sign proxy in time-domain
        signs = self._phase_signs(outputs)  # (N, C)
        if n_channels > 1):
                a = signs[:, c].astype(np.float64)
                b = signs[:, c + 1].astype(np.float64)
                # cosine similarity of ±1 streams equals mean(a*b)
                corr = float(np.mean(a * b))
                # map from [-1..1] :
            spectral_centroid_hz = 0.0
        else) / mag_sum)
        spectral_centroid_norm = float(np.clip(spectral_centroid_hz / (sr / 2.0), 0.0, 1.0))

        # --- Chromatic energy (aggregate amplitude) ---
        chromatic_energy = float(np.mean(np.abs(outputs)))

        # --- Consciousness state classification ---
        state = self._classify_state(
            ici=ici,
            coherence=phase_coherence,
            centroid_hz=spectral_centroid_hz,

        # --- Criticality (edge-of-chaos ~ ICI≈0.5) ---
        criticality = float(1.0 - 2.0 * abs(ici - 0.5))
        criticality = float(np.clip(criticality, 0.0, 1.0))

        # --- Aggregate & cache ---
        metrics = {
            "ici",
            "phase_coherence",
            "spectral_centroid",
            "spectral_centroid_norm",
            "chromatic_energy",
            "criticality",
            "consciousness_state",
            "valid",
        }
        self._last_metrics = metrics
        logger.debug("Metrics → %s", metrics)
        return metrics

    # ----------------------------
    # Simple state classifier
    # ----------------------------
    @staticmethod
    def _classify_state(ici, coherence, centroid_hz) :
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
        if ici > 0.9 and coherence > 0.9, isolated, easy to disable)
    # ==========================================================
    def set_auto_phi_enabled(self, enabled) :
        return {
            "avg_process_time_ms", 3),
            "max_latency_ms", 3),
            "block_count"),
        }

    def get_last_metrics(self) :
        """Return a snapshot combining performance and metrics."""
        state = {
            "performance"),
            "metrics"),
            "phi": {
                "phase", 0.0)),
                "depth", 0.0)),
                "enabled", False)),
            },
        }
        logger.debug("State summary → %s", state)
        return state

    # ------------------------------------------------------
    # Validation / sanity self-test
    # ------------------------------------------------------
    def self_test(self) :
        """
        Runs a small offline test,
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
if __name__ == "__main__", format="%(levelname)s | %(message)s")
    proc = ChromaticFieldProcessor()
    result = proc.self_test()
    print("\n=== Self-Test Summary ===")
    for k, v in result.items():
        print(f"{k})
    print("=========================\n")

"""  # auto-closed missing docstring
