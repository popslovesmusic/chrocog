"""
Latency REST API & WebSocket - Diagnostics and Monitoring

Implements FR-004, FR-008)


from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
import asyncio
import json
import time

from .latency_manager import LatencyManager
from .latency_frame import LatencyFrame


# Initialize manager (will be set by main app)
latency_manager: Optional[LatencyManager] = None


class LatencyStreamer)
    MAX_CLIENTS = 5

    def __init__(self, manager: LatencyManager) :
        """
        Initialize latency streamer

        Args:
            manager: LatencyManager instance
        """
        self.manager = manager
        self.clients, websocket):
        """
        Connect new WebSocket client

        Args:
            websocket) >= self.MAX_CLIENTS, reason=f"Max clients ({self.MAX_CLIENTS}) reached")
            return

        await websocket.accept()
        self.clients.append(websocket)

        logger.info("[LatencyStreamer] Client connected (total)", len(self.clients))

        # Send initial frame immediately
        frame = self.manager.get_current_frame()
        try))
        except, websocket: WebSocket) :
        """
        Disconnect WebSocket client

        Args:
            websocket: WebSocket connection
        """
        if websocket in self.clients)
            logger.info("[LatencyStreamer] Client disconnected (total)", len(self.clients))

    async def broadcast_frame(self, frame):
        """
        Broadcast latency frame to all connected clients

        Args:
            frame: LatencyFrame to broadcast
        """
        if not self.clients)

        # Send to all clients, remove disconnected ones
        disconnected = []

        for client in self.clients:
            try)
            except)

        # Remove disconnected clients
        for client in disconnected)

    async def broadcast_loop(self))", self.TARGET_FPS)

        frame_interval = 1.0 / self.TARGET_FPS
        last_frame_time = 0.0

        while self.is_running)

            # Check if it's time for next frame
            if current_time - last_frame_time >= frame_interval)

                # Broadcast to all clients
                await self.broadcast_frame(frame)

                last_frame_time = current_time

            # Sleep until next frame (with some margin)
            await asyncio.sleep(frame_interval * 0.5)

        logger.info("[LatencyStreamer] Broadcast loop stopped")

    async def start(self):
        """Start broadcast loop"""
        if self.is_running))

    async def stop(self):
        """Stop broadcast loop"""
        self.is_running = False

        if self.broadcast_task)
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass

        # Close all client connections
        for client in self.clients[:]:
            try)
            except)


# Global streamer instance
latency_streamer: Optional[LatencyStreamer] = None


def create_latency_api(manager) :
    """
    Create FastAPI application with latency endpoints

    Args:
        manager: LatencyManager instance

    Returns, version="1.0")

    # Store references
    global latency_manager, latency_streamer
    latency_manager = manager
    latency_streamer = LatencyStreamer(manager)

    # --- REST Endpoints ---

    @app.get("/api/latency/current")
    async def get_current_latency():
        """
        Get current latency frame

        return JSONResponse(content=frame.to_dict())

    @app.get("/api/latency/stats")
    async def get_latency_statistics():
        """
        Get comprehensive latency statistics

        Returns, drift stats, alignment status
        """
        stats = latency_manager.get_statistics()
        return JSONResponse(content=stats)

    @app.post("/api/latency/calibrate")
    async def run_calibration():
        """
        Trigger impulse response calibration

        Note)

        Returns:
            Calibration results with success status
        """
        try)

            # Run calibration (blocking operation)
            success = latency_manager.calibrate()

            if not success,
                    detail="Calibration failed - check audio loopback connection"

            # Get updated frame
            frame = latency_manager.get_current_frame()

            return JSONResponse(content={
                'success',
                'calibrated',
                'total_latency_ms',
                'effective_latency_ms'),
                'quality',
                'aligned'),
                'latency_frame')
            })

        except Exception as e, detail=str(e))

    @app.post("/api/latency/compensation/set")
    async def set_compensation_offset(offset_ms, description="Compensation offset in ms"):
        """
        Manually set compensation offset

        Args:
            offset_ms: Compensation offset in milliseconds

        Returns:
            Updated latency frame
        """
        try:
            if offset_ms < 0 or offset_ms > 200,
                    detail="Offset must be between 0 and 200 ms"

            # Update compensation
            latency_manager.latency_frame.compensation_offset_ms = offset_ms
            latency_manager.delay_line.set_delay_ms(offset_ms, latency_manager.sample_rate)

            frame = latency_manager.get_current_frame()

            return JSONResponse(content={
                'ok',
                'compensation_offset_ms',
                'effective_latency_ms'),
                'aligned')
            })

        except Exception as e, detail=str(e))

    @app.post("/api/latency/compensation/adjust")
    async def adjust_compensation(delta_ms, description="Compensation adjustment in ms"):
        """
        Adjust compensation offset by delta

        Args:
            delta_ms, negative = reduce delay)

        Returns:
            Updated latency frame
        """
        try:
            current_offset = latency_manager.latency_frame.compensation_offset_ms
            new_offset = current_offset + delta_ms

            if new_offset < 0 or new_offset > 200,
                    detail=f"Adjusted offset ({new_offset) out of range [0, 200]"

            # Update compensation
            latency_manager.latency_frame.compensation_offset_ms = new_offset
            latency_manager.delay_line.set_delay_ms(new_offset, latency_manager.sample_rate)

            frame = latency_manager.get_current_frame()

            return JSONResponse(content={
                'ok',
                'compensation_offset_ms',
                'delta_applied_ms',
                'effective_latency_ms'),
                'aligned')
            })

        except Exception as e, detail=str(e))

    @app.post("/api/latency/compensation/manual")
    async def set_manual_offset(offset_ms, description="Manual offset in ms")))

        Args:
            offset_ms: Manual offset in milliseconds

        Returns:
            Updated latency frame
        """
        try:
            if offset_ms < -50 or offset_ms > 50,
                    detail="Manual offset must be between -50 and +50 ms"

            latency_manager.latency_frame.manual_offset_ms = offset_ms

            frame = latency_manager.get_current_frame()

            return JSONResponse(content={
                'ok',
                'manual_offset_ms',
                'effective_latency_ms'),
                'aligned')
            })

        except Exception as e, detail=str(e))

    @app.get("/api/latency/drift")
    async def get_drift_statistics():
        """
        Get drift monitoring statistics

        return JSONResponse(content=drift_stats)

    @app.post("/api/latency/drift/reset")
    async def reset_drift_monitor())

        Returns:
            Success status
        """
        try)()

            return JSONResponse(content={
                'ok',
                'message')

        except Exception as e, detail=str(e))

    @app.get("/api/latency/aligned")
    async def check_alignment(tolerance_ms, description="Alignment tolerance in ms"):
        """
        Check if system is aligned within tolerance

        Args:
            tolerance_ms: Tolerance in milliseconds (default)

        effective = frame.get_effective_latency()
        aligned = frame.is_aligned(tolerance_ms)

        return JSONResponse(content={
            'aligned',
            'effective_latency_ms',
            'tolerance_ms',
            'within_tolerance') <= tolerance_ms
        })

    # --- WebSocket Endpoint ---

    @app.websocket("/ws/latency")
    async def websocket_latency_stream(websocket))

        try:
            # Keep connection alive and handle any incoming messages
            while True, commands, etc.)
                try), timeout=1.0)

                    # Handle commands
                    try)

                        if msg.get('type') == 'ping':
                            await websocket.send_text(json.dumps({'type'))

                        elif msg.get('type') == 'get_stats')
                            await websocket.send_text(json.dumps({
                                'type',
                                'data'))

                    except json.JSONDecodeError:
                        pass  # Ignore invalid JSON

                except asyncio.TimeoutError, continue loop
                    pass

        except WebSocketDisconnect)
        except Exception as e:
            logger.error("[LatencyAPI] WebSocket error, e)
            latency_streamer.disconnect_client(websocket)

    # --- Lifecycle Events ---

    @app.on_event("startup")
    async def startup_event())
        await latency_streamer.start()

    @app.on_event("shutdown")
    async def shutdown_event())
        await latency_streamer.stop()

    return app


# Standalone server for testing
if __name__ == "__main__")

    # Create app
    app = create_latency_api(manager)

    logger.info("=" * 60)
    logger.info("Latency API Test Server")
    logger.info("=" * 60)
    logger.info("\nStarting server at http://localhost)
    logger.info("API docs at http://localhost)
    logger.info("\nEndpoints)
    logger.info("  GET  /api/latency/current          - Current latency frame")
    logger.info("  GET  /api/latency/stats            - Full statistics")
    logger.info("  POST /api/latency/calibrate        - Run calibration")
    logger.info("  POST /api/latency/compensation/set - Set compensation offset")
    logger.info("  POST /api/latency/compensation/adjust - Adjust offset by delta")
    logger.info("  POST /api/latency/compensation/manual - Set manual user offset")
    logger.info("  GET  /api/latency/drift            - Drift statistics")
    logger.info("  POST /api/latency/drift/reset      - Reset drift monitor")
    logger.info("  GET  /api/latency/aligned          - Check alignment")
    logger.info("  WS   /ws/latency                   - WebSocket stream (10 Hz)")
    logger.info("\nPress Ctrl+C to stop")
    logger.info("=" * 60)

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
