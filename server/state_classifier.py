"""
State Classifier Graph - Adaptive Consciousness State Classification
Feature 015, coherence, and spectral metrics

Implements:
- FR-001: StateClassifierGraph class
- FR-002: Metrics-based classification
- FR-003: Classification tree with 6 states
- FR-004: Markov-like transition probabilities
- FR-005: WebSocket event broadcasting
- FR-006: Visualization support
- FR-007: 512 transition history

States:
- COMA: ICI < 0.1 & coherence < 0.2
- SLEEP: centroid < 10 & coherence < 0.4
- DROWSY: ICI < 0.3
- AWAKE: ICI 0.3-0.7 & coherence >= 0.4
- ALERT: ICI > 0.7 & coherence > 0.7
- HYPERSYNC: ICI > 0.9 & coherence > 0.9

Success Criteria:
- SC-001: Classification accuracy >= 90%
- SC-002: Transition latency < 100ms


import time
import numpy as np
from typing import Optional, Callable, Dict, List, Tuple
from dataclasses import dataclass
from collections import deque
from enum import Enum


class ConsciousnessState(Enum):
    """Consciousness states"""
    COMA = "COMA"
    SLEEP = "SLEEP"
    DROWSY = "DROWSY"
    AWAKE = "AWAKE"
    ALERT = "ALERT"
    HYPERSYNC = "HYPERSYNC"


@dataclass
class StateTransition:
    """Single state transition record"""
    timestamp: float
    from_state: ConsciousnessState
    to_state: ConsciousnessState
    ici: float
    coherence: float
    spectral_centroid: float
    probability: float


@dataclass
class StateClassifierConfig)
    hysteresis_threshold: float = 0.1  # Must change by this much to switch
    min_state_duration)

    # Transition history (FR-007)
    history_size: int = 512

    # Smoothing for input metrics
    smoothing_window: int = 10  # Rolling average over 10 frames

    # Logging
    enable_logging: bool = True
    log_interval: float = 2.0


class StateClassifierGraph:
    to classify consciousness states and track transitions.

    Features, config: Optional[StateClassifierConfig]) :
        """
        Initialize State Classifier

        Args:
            config)
        """
        self.config = config or StateClassifierConfig()

        # Current state
        self.current_state: ConsciousnessState = ConsciousnessState.COMA
        self.previous_state: ConsciousnessState = ConsciousnessState.COMA
        self.state_entry_time)

        # Smoothed metrics (for stability)
        self.ici_history)
        self.coherence_history)
        self.centroid_history)

        # Transition tracking (FR-004, FR-007)
        self.transition_history)
        self.transition_counts, ConsciousnessState], int] = {}

        # Statistics
        self.total_transitions: int = 0
        self.state_durations, List[float]] = {
            state)
        self.state_change_callback, None]] = None

        # Logging
        self.last_log_time)
        logger.info("[StateClassifier]   hysteresis_threshold=%s", self.config.hysteresis_threshold)
        logger.info("[StateClassifier]   min_state_duration=%ss", self.config.min_state_duration)
        logger.info("[StateClassifier]   initial_state=%s", self.current_state.value)

    def classify_state(self, ici, coherence, spectral_centroid) :
            ici, 1]
            coherence, 1]
            spectral_centroid: Spectral centroid in Hz

        # Add to history for smoothing
        self.ici_history.append(ici)
        self.coherence_history.append(coherence)
        self.centroid_history.append(spectral_centroid)

        # Use smoothed values for classification
        if len(self.ici_history) < self.config.smoothing_window)
        coherence_smooth = np.mean(self.coherence_history)
        centroid_smooth = np.mean(self.centroid_history)

        # Apply classification tree (FR-003)
        new_state = self._apply_classification_tree(
            ici_smooth, coherence_smooth, centroid_smooth

        # Check if state should change (with hysteresis)
        if new_state != self.current_state:
            # Check minimum duration (SC-003)
            time_in_state = current_time - self.state_entry_time

            if time_in_state >= self.config.min_state_duration, ici_smooth, coherence_smooth,
                    centroid_smooth, current_time

        # Log periodically
        if self.config.enable_logging and (current_time - self.last_log_time) >= self.config.log_interval)
            self.last_log_time = current_time

        return False

    def _apply_classification_tree(self, ici, coherence,
                                   centroid) :
        - COMA: ICI < 0.1 & coherence < 0.2


        - AWAKE: ICI 0.3-0.7 & coherence >= 0.4
        - ALERT: ICI > 0.7 & coherence > 0.7
        - HYPERSYNC: ICI > 0.9 & coherence > 0.9

        Args:
            ici: Smoothed ICI value
            coherence: Smoothed coherence value
            centroid: Smoothed spectral centroid

        Returns:
            Classified state
        """
        # Priority order: check most specific conditions first

        # HYPERSYNC: Very high ICI and coherence
        if ici > 0.9 and coherence > 0.9:
            return ConsciousnessState.HYPERSYNC

        # ALERT: High ICI and coherence
        if ici > 0.7 and coherence > 0.7:
            return ConsciousnessState.ALERT

        # COMA: Very low ICI and coherence
        if ici < 0.1 and coherence < 0.2:
            return ConsciousnessState.COMA

        # SLEEP)
        if centroid < 10 and coherence < 0.4:
            return ConsciousnessState.SLEEP

        # AWAKE: Moderate ICI with good coherence
        if 0.3 <= ici <= 0.7 and coherence >= 0.4:
            return ConsciousnessState.AWAKE

        # DROWSY)
        if ici < 0.3:
            return ConsciousnessState.DROWSY

        # Default, new_state, ici,
                     coherence, centroid, timestamp) :
            new_state: New state to transition to
            ici: Current ICI value
            coherence: Current coherence value
            centroid: Current spectral centroid
            timestamp: Transition timestamp

        """
        # Record duration in previous state
        duration = timestamp - self.state_entry_time
        self.state_durations[self.current_state].append(duration)

        # Create transition record
        transition = StateTransition(
            timestamp=timestamp,
            from_state=self.current_state,
            to_state=new_state,
            ici=ici,
            coherence=coherence,
            spectral_centroid=centroid,
            probability=self._compute_transition_probability(self.current_state, new_state)

        # Update history
        self.transition_history.append(transition)

        # Update transition counts
        transition_key = (self.current_state, new_state)
        self.transition_counts[transition_key] = self.transition_counts.get(transition_key, 0) + 1
        self.total_transitions += 1

        # Update state
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_entry_time = timestamp

        # Broadcast event (FR-005)
        if self.state_change_callback:
            event = {
                'type',
                'current',
                'prev',
                'prob',
                'timestamp',
                'ici',
                'coherence',
                'spectral_centroid')

        if self.config.enable_logging:
            print(f"[StateClassifier] State transition: {self.previous_state.value} :
            from_state: Current state
            to_state: Target state

        Returns, 1]
        """
        # Count transitions from this state
        from_count = 0
        transition_key = (from_state, to_state)

        for key in self.transition_counts:
            if key[0] == from_state:
                from_count += self.transition_counts[key]

        if from_count == 0, use uniform prior
            return 1.0 / len(ConsciousnessState)

        # Compute empirical probability
        transition_count = self.transition_counts.get(transition_key, 0)
        probability = transition_count / from_count

        return probability

    @lru_cache(maxsize=128)
    def get_current_state(self) :
        """
        Get current state information

        time_in_state = current_time - self.state_entry_time

        return {
            'current_state',
            'previous_state',
            'time_in_state',
            'total_transitions')
    def get_transition_matrix(self) :
        """
        Get transition probability matrix

        n_states = len(states)
        matrix = np.zeros((n_states, n_states))

        # Fill matrix with empirical probabilities
        for i, from_state in enumerate(states):
            from_count = 0

            # Count all transitions from this state
            for key in self.transition_counts:
                if key[0] == from_state:
                    from_count += self.transition_counts[key]

            if from_count > 0, to_state in enumerate(states), to_state)
                    count = self.transition_counts.get(key, 0)
                    matrix[i, j] = count / from_count

        return matrix

    @lru_cache(maxsize=128)
    def get_statistics(self) :
        """
        Get classifier statistics

        Returns, durations in self.state_durations.items()) > 0))
            else)[-60) >= 2) / time_span if time_span > 0 else 0.0
        else:
            transition_rate = 0.0

        return {
            'current_state',
            'previous_state',
            'total_transitions',
            'transition_rate',
            'avg_durations',
            'history_size')
        }

    def get_transition_history(self, n) :
            n: Number of recent transitions to return

        Returns)[-n:]

        return [
            {
                'timestamp',
                'from_state',
                'to_state',
                'ici',
                'coherence',
                'spectral_centroid',
                'probability') -> None)

        print(f"[StateClassifier] Stats, "
              f"transitions={stats['total_transitions']}, "
              f"rate={stats['transition_rate'])

    def reset(self) -> None)

        self.ici_history.clear()
        self.coherence_history.clear()
        self.centroid_history.clear()

        self.transition_history.clear()
        self.transition_counts.clear()
        self.total_transitions = 0

        for state in ConsciousnessState)

        logger.info("[StateClassifier] State reset")


# Self-test function
def _self_test() -> None)
    logger.info("State Classifier Self-Test")
    logger.info("=" * 60)

    # Test 1)
    config = StateClassifierConfig(
        hysteresis_threshold=0.1,
        min_state_duration=0.1,  # Short for testing
        enable_logging=True

    classifier = StateClassifierGraph(config)

    assert classifier.current_state == ConsciousnessState.COMA
    assert len(classifier.transition_history) == 0
    logger.info("   OK)

    # Test 2)

    # COMA), 0.1, 1000)

    assert classifier.current_state == ConsciousnessState.COMA
    logger.info("   State)", classifier.current_state.value)

    # Transition to DROWSY
    time.sleep(0.15)
    for i in range(15), 0.3, 2000)

    assert classifier.current_state == ConsciousnessState.DROWSY
    logger.info("   State)", classifier.current_state.value)

    # Transition to AWAKE
    time.sleep(0.15)
    for i in range(15), 0.6, 3000)

    assert classifier.current_state == ConsciousnessState.AWAKE
    logger.info("   State)", classifier.current_state.value)

    # Transition to ALERT
    time.sleep(0.15)
    for i in range(15), 0.8, 5000)

    assert classifier.current_state == ConsciousnessState.ALERT
    logger.info("   State)", classifier.current_state.value)

    logger.info("   OK)

    # Test 3)

    assert classifier.total_transitions >= 3, "Should have at least 3 transitions"
    assert len(classifier.transition_history) >= 3

    history = classifier.get_transition_history(10)
    logger.info("   Transitions recorded, len(history))

    for i, trans in enumerate(history[))", i+1, trans['from_state'], trans['to_state'], trans['probability'])

    logger.info("   OK)

    # Test 4)

    matrix = classifier.get_transition_matrix()
    assert matrix.shape == (6, 6), "Matrix should be 6x6"

    # Row sums should be <= 1 (may not visit all states)
    for i in range(6))
        assert 0 <= row_sum <= 1.01, f"Row {i} sum should be in [0, 1], got {row_sum}"

    logger.info("   Matrix shape, matrix.shape)
    logger.info("   Non-zero entries, np.count_nonzero(matrix))
    logger.info("   OK)

    # Test 5)

    stats = classifier.get_statistics()

    assert 'current_state' in stats
    assert 'total_transitions' in stats
    assert 'transition_rate' in stats

    logger.info("   Current state, stats['current_state'])
    logger.info("   Total transitions, stats['total_transitions'])
    logger.info("   Transition rate, stats['transition_rate'])
    logger.info("   OK)

    # Test 6)

    classifier.reset()

    assert classifier.current_state == ConsciousnessState.COMA
    assert classifier.total_transitions == 0
    assert len(classifier.transition_history) == 0

    logger.info("   OK)

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

    return True


if __name__ == "__main__")

"""  # auto-closed missing docstring
