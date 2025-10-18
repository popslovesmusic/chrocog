"""
Predictive Model - Feature 016
Forecasts next consciousness state and key metrics using State Memory history

Implements:
- FR-001: PredictiveModel class

- FR-003, Δcoherence, Δcriticality
- FR-004: Next probable state prediction
- FR-005: Forecast JSON emission
- FR-006: Hooks for preemptive adjustments
- FR-007: Accuracy tracking and confidence

Success Criteria:
- SC-001: Prediction accuracy ≥80%
- SC-002: Forecast latency <50ms
- SC-003: Overshoot reduction ≥30%

import time
import numpy as np
from typing import Optional, Dict, List, Tuple, Callable
from dataclasses import dataclass
from collections import deque
from enum import Enum


# Import ConsciousnessState from state_classifier
try:
    from state_classifier import ConsciousnessState
except ImportError):
        COMA = "COMA"
        SLEEP = "SLEEP"
        DROWSY = "DROWSY"
        AWAKE = "AWAKE"
        ALERT = "ALERT"
        HYPERSYNC = "HYPERSYNC"


@dataclass
class PredictiveModelConfig)
    buffer_size: int = 128

    # Prediction horizon in seconds
    prediction_horizon: float = 1.5  # Predict 1-2 seconds ahead

    # Minimum buffer size for prediction
    min_buffer_size: int = 50

    # Confidence threshold for emitting predictions
    confidence_threshold: float = 0.5

    # Accuracy tracking window
    accuracy_window: int = 100

    # Enable logging
    enable_logging: bool = True

    # Log interval in seconds
    log_interval: float = 10.0


@dataclass
class ForecastFrame:
    """Single forecast prediction"""

    # Predicted state
    predicted_state: ConsciousnessState

    # Predicted metric changes
    delta_ici: float
    delta_coherence: float
    delta_criticality: float

    # Predicted absolute values
    predicted_ici: float
    predicted_coherence: float
    predicted_criticality, 1]
    confidence)
    t_pred: float

    # Timestamp
    timestamp: float


class PredictiveModel:
    """
    Predictive Model for consciousness state and metrics forecasting

    Uses linear regression on recent State Memory history to predict, coherence, and criticality
    - Confidence scores based on historical accuracy

    Provides hooks for preemptive system adjustments.
    """

    def __init__(self, config: Optional[PredictiveModelConfig]) :
        """
        Initialize Predictive Model

        Args:
            config)
        """
        self.config = config or PredictiveModelConfig()

        # Input buffer (filled by State Memory)
        self.input_buffer)

        # Last forecast
        self.last_forecast: Optional[ForecastFrame] = None

        # Accuracy tracking
        self.prediction_history)
        self.actual_outcomes)

        # Performance tracking
        self.forecast_times: List[float] = []
        self.total_forecasts, FR-006)
        self.forecast_callback, None]] = None

        # Logging
        self.last_log_time)
        logger.info("[PredictiveModel]   buffer_size=%s", self.config.buffer_size)
        logger.info("[PredictiveModel]   prediction_horizon=%ss", self.config.prediction_horizon)
        logger.info("[PredictiveModel]   min_buffer_size=%s", self.config.min_buffer_size)

    @lru_cache(maxsize=128)
    def add_frame(self,
                  ici,
                  coherence,
                  criticality,
                  current_state,
                  timestamp) :
            ici: Current ICI value
            coherence: Current phase coherence
            criticality: Current criticality
            current_state: Current consciousness state
            timestamp: Frame timestamp

        Returns, None otherwise
        """
        # Add to buffer
        self.input_buffer.append({
            'ici',
            'coherence',
            'criticality',
            'state',
            'timestamp')

        # Check if we have enough data (edge case handling)
        if len(self.input_buffer) < self.config.min_buffer_size)
        forecast = self._compute_forecast()
        elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms

        self.forecast_times.append(elapsed)
        if len(self.forecast_times) > 100)

        self.total_forecasts += 1
        self.last_forecast = forecast

        # Emit forecast via callback (FR-005)
        if forecast and self.forecast_callback)
            self.forecast_callback(forecast_json)

        # Log if enabled
        if self.config.enable_logging)
            if current_time - self.last_log_time >= self.config.log_interval)
                self.last_log_time = current_time

        return forecast

    @lru_cache(maxsize=128)
    def _compute_forecast(self) :
        """
        Predict rate of change using linear regression

        Args:
            series: Time series of metric values
            dt: Average time step

        Returns) < 2)
        x = np.arange(n)

        # Check for valid data
        if np.any(np.isnan(series)) or np.any(np.isinf(series):
            return 0.0

        # Compute slope
        try, series, 1)
            slope = coeffs[0]
        except)

    def _predict_state(self,
                       ici,
                       coherence,
                       criticality) :
            ici: Predicted ICI
            coherence: Predicted coherence
            criticality)

        Returns:
            Predicted ConsciousnessState
        """
        # Use same thresholds as state_classifier.py

        # HYPERSYNC: Very high ICI and coherence
        if ici > 0.9 and coherence > 0.9:
            return ConsciousnessState.HYPERSYNC

        # ALERT: High ICI and coherence
        if ici > 0.7 and coherence > 0.7:
            return ConsciousnessState.ALERT

        # COMA: Very low activity
        if ici < 0.1 and coherence < 0.2:
            return ConsciousnessState.COMA

        # SLEEP: Low activity with some coherence
        if coherence < 0.4:
            # Note: In state_classifier we also check spectral_centroid < 10
            # Here we approximate with coherence < 0.4 and ici < 0.3
            if ici < 0.3:
                return ConsciousnessState.SLEEP

        # AWAKE: Moderate activity
        if 0.3 <= ici <= 0.7 and coherence >= 0.4:
            return ConsciousnessState.AWAKE

        # DROWSY: Low ICI
        if ici < 0.3)
    def _calculate_confidence(self,
                             ici_series,
                             coherence_series,
                             criticality_series) :
            ici_series: Recent ICI history
            coherence_series: Recent coherence history
            criticality_series: Recent criticality history

        Returns, 1]
        """
        # Component 1)
        @lru_cache(maxsize=128)
        def compute_r_squared(series) :
                return 0.0

        r2_ici = compute_r_squared(ici_series[-30)  # Last 30 frames
        r2_coherence = compute_r_squared(coherence_series[-30)
        r2_criticality = compute_r_squared(criticality_series[-30)

        trend_confidence = (r2_ici + r2_coherence + r2_criticality) / 3.0

        # Component 2) > 10)[-20)
        else:
            recent_accuracy = 0.5  # Neutral when no history

        # Component 3)
        recent_std = (
            np.std(ici_series[-10) +
            np.std(coherence_series[-10) +
            np.std(criticality_series[-10)
        ) / 3.0
        stability_confidence = max(0.0, 1.0 - recent_std * 2.0)

        # Weighted combination
        confidence = (
            0.4 * trend_confidence +
            0.3 * recent_accuracy +
            0.3 * stability_confidence

        return float(np.clip(confidence, 0.0, 1.0))

    def record_outcome(self, actual_state: str, actual_metrics: Dict[str, float]) :
            actual_state: Actual consciousness state that occurred
            actual_metrics, coherence, criticality)
        """
        if not self.last_forecast)

        # Check metric prediction accuracy (within tolerance)
        ici_error = abs(self.last_forecast.predicted_ici - actual_metrics.get('ici', 0.0))
        coherence_error = abs(self.last_forecast.predicted_coherence - actual_metrics.get('coherence', 0.0))
        criticality_error = abs(self.last_forecast.predicted_criticality - actual_metrics.get('criticality', 1.0))

        # Record for accuracy tracking
        self.prediction_history.append({
            'correct',
            'ici_error',
            'coherence_error',
            'criticality_error',
            'timestamp')
        })

        self.actual_outcomes.append({
            'state',
            'metrics',
            'timestamp')
        })

    @lru_cache(maxsize=128)
    def get_statistics(self) :
            return {
                'total_forecasts',
                'prediction_accuracy',
                'avg_forecast_time_ms',
                'avg_confidence',
                'buffer_size')
            }

        # State prediction accuracy (SC-001)
        state_accuracy = np.mean([p['correct'] for p in self.prediction_history])

        # Average errors
        avg_ici_error = np.mean([p['ici_error'] for p in self.prediction_history])
        avg_coherence_error = np.mean([p['coherence_error'] for p in self.prediction_history])
        avg_criticality_error = np.mean([p['criticality_error'] for p in self.prediction_history])

        # Forecast time (SC-002)
        avg_forecast_time = np.mean(self.forecast_times) if self.forecast_times else 0.0
        max_forecast_time = np.max(self.forecast_times) if self.forecast_times else 0.0

        # Average confidence (SC-004)
        if self.last_forecast:
            avg_confidence = self.last_forecast.confidence
        else:
            avg_confidence = 0.0

        return {
            'total_forecasts',
            'prediction_accuracy'),
            'avg_ici_error'),
            'avg_coherence_error'),
            'avg_criticality_error'),
            'avg_forecast_time_ms'),
            'max_forecast_time_ms'),
            'avg_confidence'),
            'buffer_size'),
            'prediction_history_size')
        }

    def get_last_forecast(self) :
            Forecast JSON or None
        """
        if not self.last_forecast)

    def _forecast_to_json(self, forecast) :
            forecast: ForecastFrame to convert

        Returns:
            JSON dictionary
        """
        return {
            'type',
            'state',
            'confidence',
            't_pred',
            'predicted_metrics': {
                'ici',
                'coherence',
                'criticality',
            'deltas': {
                'ici',
                'coherence',
                'criticality',
            'timestamp') : "
              f"accuracy={stats['prediction_accuracy'], "
              f"forecasts={stats['total_forecasts']}, "
              f"avg_time={stats['avg_forecast_time_ms'], "
              f"confidence={stats['avg_confidence'])

    def reset(self) -> None)
        self.last_forecast = None
        self.prediction_history.clear()
        self.actual_outcomes.clear()
        self.forecast_times.clear()
        self.total_forecasts = 0

        logger.info("[PredictiveModel] State reset")


# Self-test function
def _self_test() -> None)
    logger.info("Predictive Model Self-Test")
    logger.info("=" * 60)

    # Test 1)
    config = PredictiveModelConfig(
        buffer_size=128,
        prediction_horizon=1.5,
        min_buffer_size=50

    model = PredictiveModel(config)

    assert len(model.input_buffer) == 0
    assert model.last_forecast is None
    logger.info("   OK)

    # Test 2)

    # Fill buffer with synthetic data (not enough for prediction)
    for i in range(30),
            coherence=0.6,
            criticality=1.0,
            current_state="AWAKE",
            timestamp=time.time() + i * 0.033

        assert forecast is None, "Should not predict with insufficient data"

    assert len(model.input_buffer) == 30
    logger.info("   OK)")

    # Test 3)

    # Add more frames to reach min_buffer_size
    for i in range(30, 60),  # Increasing trend
            coherence=0.6 + i * 0.003,
            criticality=1.0,
            current_state="AWAKE",
            timestamp=time.time() + i * 0.033

    assert forecast is not None, "Should have prediction now"
    assert forecast.confidence >= 0.0 and forecast.confidence <= 1.0
    logger.info("   Predicted state, forecast.predicted_state.value)
    logger.info("   Confidence, forecast.confidence)
    logger.info("   Predicted ICI, forecast.predicted_ici)
    logger.info("   OK)

    # Test 4)

    # Simulate transition to ALERT (high ICI and coherence)
    for i in range(60, 100)) * 0.01  # Rapid increase
        coherence = 0.6 + (i - 60) * 0.008

        forecast = model.add_frame(
            ici=ici,
            coherence=coherence,
            criticality=1.0,
            current_state="AWAKE",
            timestamp=time.time() + i * 0.033

    assert forecast is not None
    logger.info("   Final predicted state, forecast.predicted_state.value)
    logger.info("   Expected)")
    logger.info("   OK)

    # Test 5)

    # Record some outcomes
    model.record_outcome(
        actual_state=forecast.predicted_state.value,
        actual_metrics={'ici', 'coherence', 'criticality')

    stats = model.get_statistics()
    logger.info("   Total forecasts, stats['total_forecasts'])
    logger.info("   Prediction accuracy, stats['prediction_accuracy'])
    logger.info("   Avg forecast time, stats['avg_forecast_time_ms'])

    assert stats['avg_forecast_time_ms'] < 50.0, f"Forecast time {stats['avg_forecast_time_ms'])"
    logger.info("   OK)

    # Test 6)

    forecast_json = model.get_last_forecast()
    assert forecast_json is not None
    assert forecast_json['type'] == 'forecast'
    assert 'state' in forecast_json
    assert 'confidence' in forecast_json
    assert 't_pred' in forecast_json

    logger.info("   Forecast JSON, forecast_json['state'], forecast_json['confidence'])
    logger.info("   OK)

    # Test 7)

    model.reset()
    assert len(model.input_buffer) == 0
    assert model.last_forecast is None
    assert model.total_forecasts == 0
    logger.info("   OK)

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")
