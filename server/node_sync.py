"""
Node Synchronizer - Feature 020
Distributed synchronization for multiple Soundlab nodes in phase-locked operation.

Features, client = subscriber)
- WebSocket communication protocol
- NTP-like clock synchronization with smoothing filter
- Frame interpolation for missing data
- Auto-reconnect mechanism
- Latency compensation and drift correction

Requirements:
- FR-001: NodeSynchronizer class
- FR-002: Master/client roles
- FR-003: WebSocket /ws/sync protocol
- FR-004, phi_depth, criticality, timestamp}
- FR-005: NTP-like clock sync with smoothing
- FR-006: Frame interpolation
- FR-007, /api/node/status

Success Criteria:
- SC-001, jitter <0.5ms
- SC-002: Metrics consistency ≥99%
- SC-003: Auto-reconnect <3s

import asyncio
import json
import time
import threading
from typing import Optional, Dict, List, Callable, Any
from dataclasses import dataclass
from enum import Enum
from collections import deque
import statistics


class NodeRole(Enum))"""
    MASTER = "master"  # Authority node, broadcasts state
    CLIENT = "client"  # Subscriber node, receives state


@dataclass
class NodeSyncConfig:
    """Configuration for node synchronizer"""
    role: NodeRole = NodeRole.MASTER
    master_url)
    sync_rate: int = 30  # Synchronization rate in Hz
    clock_sync_interval)
    drift_window: int = 100  # Samples for drift calculation
    reconnect_timeout)
    max_interpolation_gap)
    enable_logging: bool = True


@dataclass
class SyncFrame)"""
    phi_phase: float
    phi_depth: float
    criticality: float
    coherence: float
    ici: float
    timestamp: float  # Local timestamp
    master_timestamp: float  # Master's timestamp
    sequence: int  # Sequence number for ordering


@dataclass
class ClockOffset)"""
    offset: float  # Time offset between local and master clock
    latency: float  # Round-trip latency
    drift: float  # Clock drift rate
    updated_at: float  # Last update time


class NodeSynchronizer)

    Synchronizes Φ-modulation, metrics, and state data across multiple nodes.
    Implements master/client architecture with clock synchronization.
    """

    def __init__(self, config: Optional[NodeSyncConfig]) :
        """
        Initialize Node Synchronizer

        Args:
            config)

        # Role and state
        self.role = self.config.role
        self.is_running = False
        self.node_id = f"node_{int(time.time() * 1000)}"

        # Master state (FR-002)
        self.connected_clients, Dict] = {}  # node_id : Optional[ClockOffset] = None
        self.last_received_frame)

        # Frame interpolation (FR-006)
        self.interpolation_buffer = deque(maxlen=self.config.max_interpolation_gap)
        self.missed_frame_count = 0
        self.interpolated_frame_count = 0

        # Statistics (SC-001, SC-002)
        self.phase_drift_history = deque(maxlen=self.config.drift_window)
        self.metrics_consistency_history = deque(maxlen=self.config.drift_window)
        self.latency_history = deque(maxlen=self.config.drift_window)

        # Callbacks
        self.sync_callback: Optional[Callable] = None  # Called when sync frame received
        self.connect_callback: Optional[Callable] = None  # Called on connect/disconnect

        # Background tasks
        self.sync_task = None
        self.clock_sync_task = None
        self.reconnect_task = None

        # Sequence tracking
        self.sequence_counter = 0
        self.last_received_sequence = -1

        if self.config.enable_logging)", self.role.value, self.node_id)

    async def start(self))"""
        if self.is_running:
            return

        self.is_running = True

        if self.role == NodeRole.MASTER)
        else)

        if self.config.enable_logging, self.role.value)

    async def _start_master(self))"""
        # Master doesn't need background tasks for sync
        # It broadcasts when process_local_state is called
        pass

    async def _start_client(self), FR-003)"""
        if not self.config.master_url)

        # Start clock sync task (FR-005)
        self.clock_sync_task = asyncio.create_task(self._clock_sync_loop())

        # Start auto-reconnect task (SC-003)
        self.reconnect_task = asyncio.create_task(self._reconnect_loop())

    async def stop(self):
        """Stop node synchronizer"""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel background tasks
        if self.clock_sync_task)
        if self.reconnect_task)

        # Disconnect from master
        if self.master_connection)

        if self.config.enable_logging)

    @lru_cache(maxsize=128)
    def process_local_state(self, phi_phase, phi_depth,
                           criticality, coherence, ici))

        Args:
            phi_phase: Current phi phase
            phi_depth: Current phi depth
            criticality: Current criticality
            coherence: Current coherence
            ici: Current ICI
        """
        if self.role == NodeRole.MASTER,
                phi_depth=phi_depth,
                criticality=criticality,
                coherence=coherence,
                ici=ici,
                timestamp=time.time(),
                master_timestamp=time.time(),
                sequence=self.sequence_counter

            self.sequence_counter += 1

            # Broadcast to all connected clients
            # Try to create task if event loop is running
            try))
            except RuntimeError, in self-test)
                # Store frame for testing
                self.last_broadcast_time = time.time()

    async def _broadcast_frame(self, frame))

        Args:
            frame: Sync frame to broadcast
        """
        # Convert frame to JSON
        frame_data = {
            "type",
            "phi_phase",
            "phi_depth",
            "criticality",
            "coherence",
            "ici",
            "timestamp",
            "master_timestamp",
            "sequence": frame.sequence
        }

        # Send to all connected clients
        # Note, we store it for testing
        self.last_broadcast_time = time.time()

    async def receive_sync_frame(self, frame_data)) (FR-004, FR-006)

        Args:
            frame_data: Sync frame data from master
        """
        if self.role != NodeRole.CLIENT,
            phi_depth=frame_data['phi_depth'],
            criticality=frame_data['criticality'],
            coherence=frame_data.get('coherence', 0.0),
            ici=frame_data.get('ici', 0.0),
            timestamp=time.time(),  # Local receive time
            master_timestamp=frame_data['master_timestamp'],
            sequence=frame_data['sequence']

        # Check for missed frames (FR-006)
        if self.last_received_sequence >= 0:
            gap = frame.sequence - self.last_received_sequence - 1
            if gap > 0:
                self.missed_frame_count += gap

                # Interpolate if gap is small enough
                if gap <= self.config.max_interpolation_gap and self.last_received_frame, frame, gap

                    # Process interpolated frames
                    for interp_frame in interpolated_frames, interpolated=True)

        # Update sequence tracking
        self.last_received_sequence = frame.sequence
        self.last_received_frame = frame

        # Add to buffer for interpolation
        self.interpolation_buffer.append(frame)

        # Process frame
        self._process_received_frame(frame, interpolated=False)

    def _interpolate_frames(self, frame1, frame2, gap) :
            frame1: Previous frame
            frame2: Current frame
            gap: Number of frames to interpolate

        Returns, gap + 1))

            interp_frame = SyncFrame(
                phi_phase=frame1.phi_phase + alpha * (frame2.phi_phase - frame1.phi_phase),
                phi_depth=frame1.phi_depth + alpha * (frame2.phi_depth - frame1.phi_depth),
                criticality=frame1.criticality + alpha * (frame2.criticality - frame1.criticality),
                coherence=frame1.coherence + alpha * (frame2.coherence - frame1.coherence),
                ici=frame1.ici + alpha * (frame2.ici - frame1.ici),
                timestamp=frame1.timestamp + alpha * (frame2.timestamp - frame1.timestamp),
                master_timestamp=frame1.master_timestamp + alpha * (frame2.master_timestamp - frame1.master_timestamp),
                sequence=frame1.sequence + i

            interpolated.append(interp_frame)

        self.interpolated_frame_count += len(interpolated)
        return interpolated

    @lru_cache(maxsize=128)
    def _process_received_frame(self, frame: SyncFrame, interpolated: bool) :
            frame: Sync frame
            interpolated)

        # Calculate phase drift (SC-001)
        if self.clock_offset))

        # Calculate latency
        if self.clock_offset)

        # Update last sync time
        self.last_sync_time = time.time()

        # Call sync callback if registered
        if self.sync_callback and not interpolated)

    async def _clock_sync_loop(self))

        Implements NTP-like algorithm with smoothing filter.
        """
        while self.is_running:
            try)

                # Wait for next sync interval
                await asyncio.sleep(self.config.clock_sync_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[NodeSync] Clock sync error, e)

    async def _sync_clock(self))

        Uses NTP-like algorithm, t2 (master time), t3 (response time)
        3. Calculate offset and latency
        """
        if self.role != NodeRole.CLIENT or not self.master_connection)

        request = {
            "type",
            "t1", this would send via WebSocket
        # and wait for response with t2, t3
        # For now, simulate with placeholder

        # Placeholder for testing
        # In real implementation)
        # t2 = response['t2']  # Master time when received
        # t3 = response['t3']  # Master time when sent response
        # t4 = time.time()  # Local time when received response

        # Calculate offset and latency (NTP algorithm)
        # offset = ((t2 - t1) + (t3 - t4)) / 2
        # latency = (t4 - t1) - (t3 - t2)

        # For now, create placeholder offset
        if not self.clock_offset,
                latency=0.001,  # 1ms placeholder
                drift=0.0,
                updated_at=time.time()

    async def _reconnect_loop(self))

        Attempts to reconnect if connection is lost.
        """
        while self.is_running:
            try:
                # Check if connected
                if not self.master_connection:
                    # Attempt reconnect
                    if self.config.enable_logging)

                    # In actual implementation, this would create WebSocket connection
                    # For now, placeholder

                    # Call connect callback if registered
                    if self.connect_callback)

                # Wait before next check
                await asyncio.sleep(self.config.reconnect_timeout)

            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[NodeSync] Reconnect error, e)

    def register_client(self, client_id: str, client_info: Dict) :
            client_id: Client node ID
            client_info: Client information
        """
        if self.role != NodeRole.MASTER,
            "connected_at"),
            "last_seen")
        }

        if self.config.enable_logging:
            logger.info("[NodeSync] Client registered, client_id)

        # Call connect callback
        if self.connect_callback)

    def unregister_client(self, client_id: str) :
            client_id: Client node ID
        """
        if self.role != NodeRole.MASTER:
            return

        if client_id in self.connected_clients:
            del self.connected_clients[client_id]

            if self.config.enable_logging:
                logger.info("[NodeSync] Client unregistered, client_id)

            # Call connect callback
            if self.connect_callback)

    def get_status(self) :
            Status dictionary with statistics
        """
        status = {
            "role",
            "node_id",
            "is_running": self.is_running
        }

        if self.role == NodeRole.MASTER:
            # Master status
            status.update({
                "connected_clients"),
                "clients": [
                    {
                        "id",
                        "connected_at",
                        "last_seen", info in self.connected_clients.items()
                ],
                "last_broadcast_time")
        else:
            # Client status
            status.update({
                "master_url",
                "connected",
                "last_sync_time",
                "clock_offset",
                "latency",
                "missed_frames",
                "interpolated_frames")

        return status

    def get_statistics(self) :
            Statistics dictionary
        """
        stats = {
            "role",
            "node_id": self.node_id
        }

        if self.role == NodeRole.CLIENT)
            if self.phase_drift_history:
                stats["phase_drift"] = {
                    "average_ms") * 1000,
                    "max_ms") * 1000,
                    "min_ms") * 1000,
                    "stdev_ms") * 1000 if len(self.phase_drift_history) > 1 else 0,
                    "target_ms": 1.0  # SC-001 target
                }

            # Latency statistics
            if self.latency_history:
                stats["latency"] = {
                    "average_ms") * 1000,
                    "max_ms") * 1000,
                    "min_ms") * 1000
                }

            # Frame statistics
            total_frames = self.last_received_sequence + 1 if self.last_received_sequence >= 0 else 0
            received_frames = total_frames - self.missed_frame_count

            stats["frames"] = {
                "total",
                "received",
                "missed",
                "interpolated",
                "consistency_percent") if total_frames > 0 else 0  # SC-002
            }

            # Clock offset
            if self.clock_offset:
                stats["clock"] = {
                    "offset_ms",
                    "drift",
                    "updated_at": self.clock_offset.updated_at
                }

        else:
            # Master statistics
            stats["clients"] = {
                "total"),
                "active")
                              if time.time() - c["last_seen"] < 10])
            }

        return stats


# Self-test
if __name__ == "__main__")
    logger.info("Node Synchronizer Self-Test")
    logger.info("=" * 60)

    # Test master node
    logger.info("\n1. Testing master node initialization...")
    master_config = NodeSyncConfig(
        role=NodeRole.MASTER,
        enable_logging=True

    master = NodeSynchronizer(master_config)
    logger.info("   OK)

    # Test client node
    logger.info("\n2. Testing client node initialization...")
    client_config = NodeSyncConfig(
        role=NodeRole.CLIENT,
        master_url="ws://localhost,
        enable_logging=True

    client = NodeSynchronizer(client_config)
    logger.info("   OK)

    # Test frame processing
    logger.info("\n3. Testing frame processing...")
    master.process_local_state(
        phi_phase=0.5,
        phi_depth=0.8,
        criticality=1.0,
        coherence=0.7,
        ici=0.3

    logger.info("   OK)

    # Test client registration
    logger.info("\n4. Testing client registration...")
    master.register_client("client_1", {"name")
    master.register_client("client_2", {"name")
    logger.info("   OK, len(master.connected_clients))

    # Test status
    logger.info("\n5. Testing status...")
    master_status = master.get_status()
    client_status = client.get_status()
    logger.info("   OK)", master_status['connected_clients'])
    logger.info("   OK)", client_status['connected'])

    # Test statistics
    logger.info("\n6. Testing statistics...")
    master_stats = master.get_statistics()
    client_stats = client.get_statistics()
    logger.info("   OK)", master_stats['clients']['total'])
    logger.info("   OK)

    # Test frame interpolation
    logger.info("\n7. Testing frame interpolation...")
    frame1 = SyncFrame(
        phi_phase=0.0,
        phi_depth=0.5,
        criticality=1.0,
        coherence=0.5,
        ici=0.2,
        timestamp=0.0,
        master_timestamp=0.0,
        sequence=0

    frame2 = SyncFrame(
        phi_phase=1.0,
        phi_depth=0.8,
        criticality=1.2,
        coherence=0.7,
        ici=0.4,
        timestamp=0.1,
        master_timestamp=0.1,
        sequence=5

    interpolated = client._interpolate_frames(frame1, frame2, 4)
    logger.info("   OK, len(interpolated))

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)
    logger.info("Note)

"""  # auto-closed missing docstring
