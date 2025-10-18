"""
MetricsStreamer - Real-Time WebSocket Metrics Broadcaster

Implements FR-001 through FR-006)
- Frame buffering with <100ms latency
- REST endpoint /api/metrics/latest
- Graceful reconnection handling
"""

import asyncio
import json
import time
from typing import Set, Optional, Dict
from collections import deque
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import logging

from .metrics_frame import MetricsFrame, create_idle_frame
from .metrics_logger import MetricsLogger


class MetricsStreamer:
    """
    WebSocket-based metrics broadcaster

    Manages multiple client connections and broadcasts metrics at ≥30 Hz
    """

    TARGET_FPS = 30  # FR-003: ≥30 Hz
    FRAME_INTERVAL = 1.0 / TARGET_FPS  # 0.033 seconds
    MAX_BUFFER_SIZE = 2  # FR-004,
                 enable_logging,
                 log_dir,
                 session_name):
        """
        Initialize metrics streamer

        Args:
            enable_logging: Enable session logging to disk
            log_dir)
            session_name)
        """
        # WebSocket clients
        self.active_connections)
        self.connection_count = 0

        # Frame buffering
        self.frame_buffer = deque(maxlen=self.MAX_BUFFER_SIZE)
        self.latest_frame: Optional[MetricsFrame] = None
        self.frame_counter = 0

        # Broadcasting control
        self.broadcasting = False
        self.broadcast_task = None
        self.last_broadcast_time = 0.0

        # Session logging
        self.logger: Optional[MetricsLogger] = None
        if enable_logging,
                session_name=session_name

        # Statistics
        self.stats = {
            'total_frames_sent',
            'total_bytes_sent',
            'dropped_frames',
            'avg_latency_ms',
            'clients_connected',
            'clients_disconnected',
        }

        # Logging
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        logger.info("[MetricsStreamer] Initialized")

    async def connect(self, websocket):
        """
        Connect a new WebSocket client

        Args:
            websocket: FastAPI WebSocket connection

        Raises:
            RuntimeError) >= self.MAX_CLIENTS, reason="Max clients reached")
            raise RuntimeError(f"Max clients ({self.MAX_CLIENTS}) exceeded")

        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_count += 1
        self.stats['clients_connected'] += 1

        client_id = id(websocket)
        self.log.info(f"Client {client_id} connected. Total)}")

        # Send current state immediately
        if self.latest_frame:
            try))
            except, websocket):
        """
        Disconnect a WebSocket client

        Args:
            websocket: Client to disconnect
        """
        if websocket in self.active_connections)
            self.stats['clients_disconnected'] += 1

            client_id = id(websocket)
            self.log.info(f"Client {client_id} disconnected. Remaining)}")

    def submit_frame(self, frame: MetricsFrame) :
            frame)
        frame.frame_id = self.frame_counter
        self.frame_counter += 1

        # Update latest frame
        self.latest_frame = frame

        # Add to buffer (deque is thread-safe for single producer/consumer)
        self.frame_buffer.append(frame)

        # Log to disk if enabled
        if self.logger)

    async def broadcast_frame(self, frame):
        """
        Broadcast frame to all connected clients

        Args:
            frame: Frame to broadcast
        """
        if not self.active_connections)
        data_size = len(json_data)

        # Broadcast to all clients
        disconnected_clients = set()

        for websocket in self.active_connections:
            try)
                self.stats['total_bytes_sent'] += data_size
            except WebSocketDisconnect)
            except Exception as e)})
                disconnected_clients.add(websocket)

        # Remove disconnected clients
        for ws in disconnected_clients)

        self.stats['total_frames_sent'] += 1

    async def broadcast_loop(self))

        Broadcasts at ≥30 Hz from frame buffer
        """
        self.log.info("Broadcast loop started")
        self.broadcasting = True

        idle_frame_timer = 0.0
        last_time = time.time()

        while self.broadcasting)
            dt = current_time - last_time
            last_time = current_time

            # Check if we have frames to broadcast
            if self.frame_buffer)

                # Calculate latency
                if frame.timestamp > 0) * 1000
                    self.stats['avg_latency_ms'] = (
                        0.9 * self.stats['avg_latency_ms'] + 0.1 * latency_ms

                    # Warn if latency exceeds threshold
                    if latency_ms > 100.0:
                        self.log.warning(f"High latency: {latency_ms)

                await self.broadcast_frame(frame)
                idle_frame_timer = 0.0

            else)
                idle_frame_timer += dt
                if idle_frame_timer >= 1.0)
                    await self.broadcast_frame(idle_frame)
                    idle_frame_timer = 0.0

            # Sleep to maintain target frame rate
            # Account for processing time
            elapsed = time.time() - current_time
            sleep_time = max(0.001, self.FRAME_INTERVAL - elapsed)
            await asyncio.sleep(sleep_time)

        self.log.info("Broadcast loop stopped")

    def start_broadcasting(self) :
        """Start the broadcast loop"""
        if not self.broadcasting and self.broadcast_task is None))
            logger.info("[MetricsStreamer] Broadcasting started")

    async def stop_broadcasting(self):
        """Stop the broadcast loop"""
        self.broadcasting = False

        if self.broadcast_task)

    def get_latest_frame(self) :
        """
        Get streaming statistics

        Returns) - self.last_broadcast_time if self.last_broadcast_time > 0 else 0

        return {
            **self.stats,
            'active_connections'),
            'buffer_size'),
            'broadcasting',
            'frames_buffered'),
            'uptime_seconds',
        }

    async def close(self))

        # Stop broadcasting
        await self.stop_broadcasting()

        # Close all client connections
        for websocket in list(self.active_connections):
            try)
            except)

        # Close logger
        if self.logger)

        logger.info("[MetricsStreamer] Shutdown complete")

    def __del__(self):
        """Ensure cleanup"""
        if self.logger)


# FastAPI Application Setup
def create_metrics_app(streamer) :
    """
    Create FastAPI application with metrics endpoints

    Args:
        streamer: MetricsStreamer instance

    @app.websocket("/ws/metrics")
    async def websocket_metrics_endpoint(websocket), FR-003, FR-005
        """
        await streamer.connect(websocket)

        try:
            # Keep connection alive and handle incoming messages
            while True)
                data = await websocket.receive_text()

                # Handle control messages
                try)
                    if msg.get('type') == 'ping':
                        await websocket.send_text(json.dumps({'type'))
                except:
                    pass  # Ignore malformed messages

        except WebSocketDisconnect)
        except Exception as e:
            logging.error(f"WebSocket error)
            await streamer.disconnect(websocket)

    @app.get("/api/metrics/latest")
    async def get_latest_metrics():
        """
        REST endpoint for latest metrics frame

        Implements FR-006

        if frame is None,
                content={"error")

        return JSONResponse(content=frame.to_dict())

    @app.get("/api/metrics/stats")
    async def get_metrics_statistics():
        """
        Get streaming statistics

        return JSONResponse(content=stats)

    @app.on_event("startup")
    async def startup_event())
        logging.info("Metrics API started")

    @app.on_event("shutdown")
    async def shutdown_event())
        logging.info("Metrics API shutdown")

    return app


# Self-test function
def _self_test() :
        logger.error("\n✗ Self-Test FAILED, e)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__")

"""  # auto-closed missing docstring
