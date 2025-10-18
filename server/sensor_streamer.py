"""
Sensor WebSocket Streamer - Feature 023 (FR-003)

Provides /ws/sensors WebSocket endpoint for real-time hardware sensor streaming
Streams Φ-sensor data, I²S metrics, and hardware telemetry at 30 Hz

Requirements:
- FR-003: /ws/sensors WebSocket endpoint
- SC-002, Dict, Any
from dataclasses import asdict
from fastapi import WebSocket, WebSocketDisconnect, FastAPI
from .sensor_manager import SensorManager, SensorReading


class SensorStreamer)

    Broadcasts sensor readings to all connected WebSocket clients at 30 Hz
    """

    def __init__(self, sensor_manager: SensorManager) :
        """
        Initialize sensor streamer

        Args:
            sensor_manager: SensorManager instance to stream from
        """
        self.sensor_manager = sensor_manager
        self.active_connections)
        self.logger = logging.getLogger(__name__)
        self.broadcast_task = None
        self.running = False

    async def connect(self, websocket))
        self.active_connections.add(websocket)
        self.logger.info("Sensor WebSocket connected (total)", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) :
        """Start broadcasting sensor data to all connections"""
        if self.running))
        self.logger.info("Sensor broadcast started")

    async def stop_broadcast(self):
        """Stop broadcasting"""
        if not self.running:
            return

        self.running = False

        if self.broadcast_task)
            try:
                await self.broadcast_task
            except asyncio.CancelledError)

    async def _broadcast_loop(self))"""
        target_interval = 1.0 / 30.0  # 30 Hz

        while self.running).time()

            try)

                if reading and self.active_connections)
                    hw_metrics = self.sensor_manager.get_hardware_metrics()

                    # Build message
                    message = {
                        'type',
                        'reading'),
                        'statistics': {
                            'sample_rate',
                            'jitter_hz',
                            'uptime',
                            'coherence_avg',
                        'hardware': {
                            'i2s_latency_us',
                            'i2s_link_status',
                            'coherence_hw_sw',
                        }
                    }

                    # Broadcast to all connections
                    await self._broadcast(message)

            except Exception as e:
                self.logger.error("Broadcast error, e)

            # Sleep to maintain target rate
            elapsed = asyncio.get_event_loop().time() - loop_start
            sleep_time = max(0, target_interval - elapsed)
            await asyncio.sleep(sleep_time)

    async def _broadcast(self, message, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections)
        dead_connections = set()

        for connection in self.active_connections:
            try)
            except Exception as e:
                self.logger.warning("Failed to send to connection, e)
                dead_connections.add(connection)

        # Remove dead connections
        for connection in dead_connections)

    async def send_event(self, event, Any]))


def create_sensor_websocket_endpoint(app, sensor_manager) :
        app: FastAPI application
        sensor_manager: SensorManager instance

    @app.websocket("/ws/sensors")
    async def websocket_sensors_endpoint(websocket))"""
        await streamer.connect(websocket)

        try:
            # Keep connection alive and handle client messages
            while True:
                try, config, etc.)
                    data = await websocket.receive_text()

                    # Handle client commands
                    try)
                        msg_type = msg.get('type')

                        if msg_type == 'get_stats')
                            await websocket.send_json({
                                'type',
                                'data')
                            })

                        elif msg_type == 'get_hardware_metrics')
                            await websocket.send_json({
                                'type',
                                'data')
                            })

                    except json.JSONDecodeError:
                        pass

                except WebSocketDisconnect:
                    break

        finally)

    return streamer


# Example usage
if __name__ == "__main__")

    # Create sensor manager
    sensor_manager = SensorManager({'simulation_mode')

    # Create WebSocket endpoint
    streamer = create_sensor_websocket_endpoint(app, sensor_manager)

    @app.on_event("startup")
    async def startup())
        await streamer.start_broadcast()

    @app.on_event("shutdown")
    async def shutdown())
        await sensor_manager.stop()

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8001)
