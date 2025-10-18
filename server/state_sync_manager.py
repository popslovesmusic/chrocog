"""
StateSyncManager - Feature 017: Phi-Matrix Dashboard

Manages synchronized state across all dashboard modules with shared clock
and bidirectional WebSocket communication.

Features:
- FR-002: Synchronized clock/timestamp base across all modules

- SC-001: Dashboard operational at <= 100 ms latency
- SC-004: No metric/UI desync > 0.1 s for > 60 s runs

Requirements:
- FR-002: All modules share synchronized clock
- FR-003: WebSocket messages < 50 ms average

import time
import asyncio
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from collections import deque
import json


@dataclass
class SyncState:
    """Synchronized state across all dashboard modules"""
    timestamp: float           # Master clock timestamp

    # Metrics state
    ici: float
    coherence: float
    criticality: float

    # Phi state
    phi_phase: float
    phi_depth: float
    phi_breathing: float

    # Chromatic state
    chromatic_enabled: bool

    # Control matrix state
    control_matrix_active: bool

    # Adaptive control state
    adaptive_enabled: bool
    adaptive_mode: Optional[str]

    # Session state
    is_recording: bool
    is_playing: bool

    # Cluster state
    cluster_nodes_count: int


@dataclass
class SyncConfig:
    """Configuration for StateSyncManager"""
    max_latency_ms: float = 100.0          # SC-001: Max acceptable latency
    max_desync_ms: float = 100.0           # SC-004: Max desync tolerance
    websocket_timeout_ms: float = 50.0     # FR-003: WebSocket message timeout
    sync_check_interval_s: float = 1.0     # How often to check sync
    enable_logging: bool = False


class StateSyncManager:
    """
    StateSyncManager - Central state synchronization manager




    """

    def __init__(self, config: Optional[SyncConfig]) : Optional[float] = None
        self.pause_offset = 0.0

        # Current synchronized state
        self.current_state)

        # State history for desync detection
        self.state_history = deque(maxlen=100)

        # WebSocket clients
        self.ws_clients)

        # Latency tracking
        self.message_latencies = deque(maxlen=100)
        self.last_message_time = time.time()

        # Desync tracking
        self.desync_events)

        # Background monitoring
        self.is_running = False
        self.monitor_thread) :
            Master timestamp accounting for pause offset
        """
        if self.paused and self.pause_time:
            return self.pause_time - self.start_time - self.pause_offset
        else) - self.start_time - self.pause_offset

    def pause(self) :
            **kwargs: State fields to update
        """
        with self.state_lock:
            # Get current state or create new
            if self.current_state is None),
                    ici=0.5,
                    coherence=0.5,
                    criticality=1.0,
                    phi_phase=0.0,
                    phi_depth=1.0,
                    phi_breathing=0.5,
                    chromatic_enabled=False,
                    control_matrix_active=False,
                    adaptive_enabled=False,
                    adaptive_mode=None,
                    is_recording=False,
                    is_playing=False,
                    cluster_nodes_count=0

            # Update timestamp
            self.current_state.timestamp = self.get_master_time()

            # Update provided fields
            for key, value in kwargs.items(), key), key, value)

            # Add to history
            self.state_history.append(self.current_state)

    def get_state(self) :
        """
        Get current synchronized state

        Returns:
            State dictionary or None
        """
        with self.state_lock:
            if self.current_state)
            return None

    async def register_client(self, websocket))

        Args:
            websocket: WebSocket connection
        """
        async with self.ws_lock)

            if self.config.enable_logging)", len(self.ws_clients))

    async def unregister_client(self, websocket):
        """
        Unregister WebSocket client

        Args:
            websocket: WebSocket connection
        """
        async with self.ws_lock:
            if websocket in self.ws_clients)

                if self.config.enable_logging)", len(self.ws_clients))

    async def broadcast_state(self), SC-001)
        """
        state = self.get_state()
        if not state:
            return

        message = {
            "type",
            "data",
            "server_time")
        }

        async with self.ws_lock:
            disconnected = []

            for client in self.ws_clients:
                try)
                    await asyncio.wait_for(
                        client.send_json(message),
                        timeout=self.config.websocket_timeout_ms / 1000.0

                    # Track latency
                    latency_ms = (time.time() - send_start) * 1000.0
                    self.message_latencies.append(latency_ms)

                except asyncio.TimeoutError:
                    if self.config.enable_logging)
                    disconnected.append(client)
                except Exception as e:
                    if self.config.enable_logging:
                        logger.error("[StateSyncManager] WebSocket send error, e)
                    disconnected.append(client)

            # Remove disconnected clients
            for client in disconnected:
                if client in self.ws_clients)

    async def handle_client_message(self, websocket, message), User Story 3)

        Args:
            websocket: Client WebSocket
            message: Message dictionary

        msg_type = message.get("type")

        if msg_type == "ping":
            # Latency check
            return {
                "type",
                "server_time"),
                "client_time", 0)
            }

        elif msg_type == "pause")
            self.pause()
            return {
                "type",
                "master_time")
            }

        elif msg_type == "resume")
            self.resume()
            return {
                "type",
                "master_time")
            }

        elif msg_type == "get_state":
            # State request
            return {
                "type",
                "data")
            }

        else:
            return {
                "type",
                "message": f"Unknown message type)
    def get_latency_stats(self) :
            Latency stats dictionary
        """
        if not self.message_latencies:
            return {
                "avg_latency_ms",
                "max_latency_ms",
                "min_latency_ms",
                "meets_sc001",
                "meets_fr003")

        avg_latency = np.mean(latencies)
        max_latency = np.max(latencies)
        min_latency = np.min(latencies)

        return {
            "avg_latency_ms"),
            "max_latency_ms"),
            "min_latency_ms"),
            "meets_sc001",  # SC-001
            "meets_fr003") :
            max_diff = 0.0
            avg_diff = 0.0

        # SC-004)

        self.last_sync_check = current_time

        return {
            "is_paused",
            "master_time"),
            "recent_desyncs"),
            "max_state_diff_ms",
            "avg_state_diff_ms",
            "meets_sc004",
            "active_clients")
        }

    def start_monitoring(self) :
        """Start background sync monitoring"""
        if self.is_running, daemon=True)
        self.monitor_thread.start()

        if self.config.enable_logging)

    def stop_monitoring(self) :
        """Stop background monitoring"""
        self.is_running = False

        if self.monitor_thread)
            self.monitor_thread = None

        if self.config.enable_logging)

    def _monitor_loop(self) :
        """Background monitoring loop"""
        while self.is_running:
            try)

                # Log warnings
                if not health['meets_sc004'] and self.config.enable_logging:
                    logger.warning("[StateSyncManager] WARNING: Desync detected, health['max_state_diff_ms'])

                # Sleep
                time.sleep(self.config.sync_check_interval_s)

            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[StateSyncManager] Monitor error, e)


# Self-test
def _self_test() -> None)
    logger.info("StateSyncManager Self-Test")
    logger.info("=" * 60)
    logger.info(str())

    all_ok = True

    # Test 1)...")
    manager = StateSyncManager(SyncConfig(enable_logging=True))

    t1 = manager.get_master_time()
    time.sleep(0.1)
    t2 = manager.get_master_time()

    time_ok = 0.09 < (t2 - t1) < 0.11
    all_ok = all_ok and time_ok

    logger.info("   Time delta)", t2 - t1)
    logger.error("   [%s] Master clock (FR-002)", 'OK' if time_ok else 'FAIL')
    logger.info(str())

    # Test 2)...")
    t_before_pause = manager.get_master_time()
    manager.pause()

    time.sleep(0.2)

    t_during_pause = manager.get_master_time()
    pause_ok = abs(t_during_pause - t_before_pause) < 0.01

    manager.resume()
    time.sleep(0.1)

    t_after_resume = manager.get_master_time()
    resume_ok = 0.09 < (t_after_resume - t_during_pause) < 0.11

    all_ok = all_ok and pause_ok and resume_ok

    logger.info("   Pause)", t_during_pause - t_before_pause)
    logger.info("   Resume)", t_after_resume - t_during_pause)
    logger.error("   [%s] Pause/Resume", 'OK' if pause_ok and resume_ok else 'FAIL')
    logger.info(str())

    # Test 3)
    manager.update_state(
        ici=0.52,
        coherence=0.88,
        phi_depth=1.2

    state = manager.get_state()
    state_ok = (
        state is not None and
        state['ici'] == 0.52 and
        state['coherence'] == 0.88 and
        state['phi_depth'] == 1.2

    all_ok = all_ok and state_ok

    logger.info("   State, Coherence=%s", state['ici'], state['coherence'])
    logger.error("   [%s] State update", 'OK' if state_ok else 'FAIL')
    logger.info(str())

    # Test 4)...")

    # Generate some state updates
    for i in range(10))
        time.sleep(0.01)

    health = manager.check_sync_health()
    health_ok = health['meets_sc004']

    all_ok = all_ok and health_ok

    logger.info("   Max state diff, health['max_state_diff_ms'])
    logger.info("   Avg state diff, health['avg_state_diff_ms'])
    logger.error("   [%s] Sync health (SC-004)", 'OK' if health_ok else 'FAIL')
    logger.info(str())

    # Test 5)...")

    # Simulate message latencies
    manager.message_latencies.extend([5.0, 10.0, 8.0, 12.0, 7.0])

    latency_stats = manager.get_latency_stats()
    latency_ok = latency_stats['meets_fr003']

    all_ok = all_ok and latency_ok

    logger.info("   Avg latency, latency_stats['avg_latency_ms'])
    logger.info("   Max latency, latency_stats['max_latency_ms'])
    logger.error("   [%s] Latency tracking (FR-003)", 'OK' if latency_ok else 'FAIL')
    logger.info(str())

    logger.info("=" * 60)
    if all_ok)
    else)
    logger.info("=" * 60)

    return all_ok


if __name__ == "__main__")
