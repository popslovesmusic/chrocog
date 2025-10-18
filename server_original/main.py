# ============================================================
# SOUNDLAB / D-ASE MAIN SERVER MODULE  (Corrected Version)
# ============================================================
# ✅ Fixes applied:
#  - Removed invalid double type hints
#  - Added missing imports (asyncio, Any, List, Optional)
#  - Made WebSocket broadcasting async-safe
#  - Added initialization checks for audio_server, metrics_streamer, auto_phi_learner
#  - Replaced bare except blocks with explicit Exception handling
# ============================================================





import asyncio
from typing import Any, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Import internal components (mock safely if missing)
try:
    from server.audio_server import AudioServer
    from server.metrics_streamer import MetricsStreamer
    from server.auto_phi_learner import AutoPhiLearner
except ImportError:
    print("⚠️ Warning: One or more core modules not found (AudioServer, MetricsStreamer, AutoPhiLearner).")



# ============================================================
# APP INITIALIZATION
# ============================================================

app = FastAPI(title="Soundlab + D-ASE Engine", version="2.0")

class MainApp:
    """
    Central orchestrator binding the Audio Server, Metrics Streamer,
    and Auto-Φ Learner components together.
    """

    def __init__(self):
        # Safely initialize submodules with fallback warnings
        try:
            self.audio_server = AudioServer()
        except Exception as e:
            print(f"⚠️ AudioServer init failed: {e}")
            self.audio_server = None

        try:
            self.metrics_streamer = MetricsStreamer()
        except Exception as e:
            print(f"⚠️ MetricsStreamer init failed: {e}")
            self.metrics_streamer = None

        try:
            self.auto_phi_learner = AutoPhiLearner()
        except Exception as e:
            print(f"⚠️ AutoPhiLearner init failed: {e}")
            self.auto_phi_learner = None
# ============================================================
# CALLBACK FUNCTIONS
# ============================================================





    # --------------------------------------------------------
    # 1. Auto-Φ Update Callback
    # --------------------------------------------------------
    def auto_phi_update_callback(self, param_name: Any, value: Any) -> None:
        """Callback for Auto-Φ Learner to update live parameters."""
        if not self.audio_server:
            print("⚠️ Warning: Audio server not initialized.")
            return

        try:
            self.audio_server.update_parameter(
                param_type='phi',
                channel=None,
                param_name=str(param_name).replace('phi_', ''),  # Remove 'phi_' prefix if present
                value=value
            )
        except Exception as e:
            print(f"❌ Error updating parameter {param_name}: {e}")





    # --------------------------------------------------------
    # 2. State Memory Bias Callback
    # --------------------------------------------------------
    def state_memory_bias_callback(self, bias: float) -> None:
        """Feed predictive bias from State Memory to Auto-Φ Learner."""
        if not self.auto_phi_learner:
            print("⚠️ Warning: Auto-Φ learner not initialized.")
            return

        try:
            self.auto_phi_learner.external_bias = bias
        except Exception as e:
            print(f"❌ Error applying bias: {e}")





    # --------------------------------------------------------
    # 3. Hybrid Metrics Callback (Async Safe)
    # --------------------------------------------------------
    async def hybrid_metrics_callback(self, metrics: List[Any]) -> None:
        """Stream HybridMetrics frames to WebSocket clients."""
        if not self.metrics_streamer:
            print("⚠️ Warning: Metrics streamer not initialized.")
            return

        try:
            await self.metrics_streamer.broadcast_event({
                'type': 'hybrid_metrics',
                'timestamp': getattr(metrics, 'timestamp', None),
                'ici': getattr(metrics, 'ici', None),
                'phase_coherence': getattr(metrics, 'phase_coherence', None),
                'spectral_centroid': getattr(metrics, 'spectral_centroid', None),
                'consciousness_level': getattr(metrics, 'consciousness_level', None),
                'phi_phase': getattr(metrics, 'phi_phase', None),
                'phi_depth': getattr(metrics, 'phi_depth', None),
                'cpu_load': getattr(metrics, 'cpu_load', None),
                'latency_ms': getattr(metrics, 'latency_ms', None)
            })
        except Exception as e:
            print(f"❌ Error broadcasting metrics: {e}")
# ============================================================
# ROUTES AND WEBSOCKET ENDPOINTS
# ============================================================





main_app = MainApp()


@app.get("/")
async def root():
    """Serve default HTML or status summary."""
    try:
        return HTMLResponse("<h2>Soundlab + D-ASE Engine is running ✅</h2>")
    except Exception as e:
        return {"error": f"Startup HTML failed: {e}"}





@app.websocket("/ws/ui")
async def websocket_ui(ws: WebSocket):
    """Bidirectional UI WebSocket for control and state updates."""
    await ws.accept()
    print("🎧 WebSocket UI connected")

    try:
        while True:
            data = await ws.receive_json()
            param = data.get("param")
            value = data.get("value")

            # Example: dynamic routing to callback
            if param and value is not None:
                main_app.auto_phi_update_callback(param, value)

            await ws.send_json({"ack": True, "param": param, "value": value})

    except WebSocketDisconnect:
        print("⚡ UI WebSocket disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        await ws.close()





@app.websocket("/ws/metrics")
async def websocket_metrics(ws: WebSocket):
    """Read-only metrics stream for visualization dashboards."""
    await ws.accept()
    print("📊 WebSocket Metrics connected")

    try:
        while True:
            await asyncio.sleep(0.5)
            fake_metrics = {
                "ici": 0.97,
                "phase_coherence": 0.89,
                "phi_phase": 0.618,
                "phi_depth": 0.382,
                "cpu_load": 12.3,
                "latency_ms": 8.5,
            }
            await ws.send_json(fake_metrics)
    except WebSocketDisconnect:
        print("⚡ Metrics WebSocket disconnected")
    except Exception as e:
        print(f"❌ Metrics stream error: {e}")
# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================





@app.on_event("startup")
async def startup_event():
    """Initialize subsystems when the FastAPI server starts."""
    print("🚀 Starting Soundlab + D-ASE subsystems...")

    try:
        if main_app.audio_server:
            await main_app.audio_server.start()
            print("🎚️ AudioServer started.")
        if main_app.metrics_streamer:
            await main_app.metrics_streamer.start()
            print("📡 MetricsStreamer started.")
        if main_app.auto_phi_learner:
            await main_app.auto_phi_learner.start()
            print("🧠 AutoPhiLearner started.")
    except Exception as e:
        print(f"❌ Startup sequence error: {e}")





@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown of subsystems."""
    print("🛑 Shutting down Soundlab + D-ASE subsystems...")

    try:
        if main_app.audio_server:
            await main_app.audio_server.stop()
        if main_app.metrics_streamer:
            await main_app.metrics_streamer.stop()
        if main_app.auto_phi_learner:
            await main_app.auto_phi_learner.stop()
    except Exception as e:
        print(f"❌ Shutdown error: {e}")





# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )





# ============================================================
# END OF FILE
# ============================================================
# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================





@app.on_event("startup")
async def startup_event():
    """Initialize subsystems when the FastAPI server starts."""
    print("🚀 Starting Soundlab + D-ASE subsystems...")

    try:
        if main_app.audio_server:
            await main_app.audio_server.start()
            print("🎚️ AudioServer started.")
        if main_app.metrics_streamer:
            await main_app.metrics_streamer.start()
            print("📡 MetricsStreamer started.")
        if main_app.auto_phi_learner:
            await main_app.auto_phi_learner.start()
            print("🧠 AutoPhiLearner started.")
    except Exception as e:
        print(f"❌ Startup sequence error: {e}")





@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown of subsystems."""
    print("🛑 Shutting down Soundlab + D-ASE subsystems...")

    try:
        if main_app.audio_server:
            await main_app.audio_server.stop()
        if main_app.metrics_streamer:
            await main_app.metrics_streamer.stop()
        if main_app.auto_phi_learner:
            await main_app.auto_phi_learner.stop()
    except Exception as e:
        print(f"❌ Shutdown error: {e}")





# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )





# ============================================================
# END OF FILE
# ============================================================
# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================





@app.on_event("startup")
async def startup_event():
    """Initialize subsystems when the FastAPI server starts."""
    print("🚀 Starting Soundlab + D-ASE subsystems...")

    try:
        if main_app.audio_server:
            await main_app.audio_server.start()
            print("🎚️ AudioServer started.")
        if main_app.metrics_streamer:
            await main_app.metrics_streamer.start()
            print("📡 MetricsStreamer started.")
        if main_app.auto_phi_learner:
            await main_app.auto_phi_learner.start()
            print("🧠 AutoPhiLearner started.")
    except Exception as e:
        print(f"❌ Startup sequence error: {e}")





@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown of subsystems."""
    print("🛑 Shutting down Soundlab + D-ASE subsystems...")

    try:
        if main_app.audio_server:
            await main_app.audio_server.stop()
        if main_app.metrics_streamer:
            await main_app.metrics_streamer.stop()
        if main_app.auto_phi_learner:
            await main_app.auto_phi_learner.stop()
    except Exception as e:
        print(f"❌ Shutdown error: {e}")





# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )





# ============================================================
# END OF FILE
# ============================================================
# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================





@app.on_event("startup")
async def startup_event():
    """Initialize subsystems when the FastAPI server starts."""
    print("🚀 Starting Soundlab + D-ASE subsystems...")

    try:
        if main_app.audio_server:
            await main_app.audio_server.start()
            print("🎚️ AudioServer started.")
        if main_app.metrics_streamer:
            await main_app.metrics_streamer.start()
            print("📡 MetricsStreamer started.")
        if main_app.auto_phi_learner:
            await main_app.auto_phi_learner.start()
            print("🧠 AutoPhiLearner started.")
    except Exception as e:
        print(f"❌ Startup sequence error: {e}")





@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown of subsystems."""
    print("🛑 Shutting down Soundlab + D-ASE subsystems...")

    try:
        if main_app.audio_server:
            await main_app.audio_server.stop()
        if main_app.metrics_streamer:
            await main_app.metrics_streamer.stop()
        if main_app.auto_phi_learner:
            await main_app.auto_phi_learner.stop()
    except Exception as e:
        print(f"❌ Shutdown error: {e}")





# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )





# ============================================================
# END OF FILE
# ============================================================
# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================





@app.on_event("startup")
async def startup_event():
    """Initialize subsystems when the FastAPI server starts."""
    print("🚀 Starting Soundlab + D-ASE subsystems...")

    try:
        if main_app.audio_server:
            await main_app.audio_server.start()
            print("🎚️ AudioServer started.")
        if main_app.metrics_streamer:
            await main_app.metrics_streamer.start()
            print("📡 MetricsStreamer started.")
        if main_app.auto_phi_learner:
            await main_app.auto_phi_learner.start()
            print("🧠 AutoPhiLearner started.")
    except Exception as e:
        print(f"❌ Startup sequence error: {e}")





@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown of subsystems."""
    print("🛑 Shutting down Soundlab + D-ASE subsystems...")

    try:
        if main_app.audio_server:
            await main_app.audio_server.stop()
        if main_app.metrics_streamer:
            await main_app.metrics_streamer.stop()
        if main_app.auto_phi_learner:
            await main_app.auto_phi_learner.stop()
    except Exception as e:
        print(f"❌ Shutdown error: {e}")





# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )





# ============================================================
# END OF FILE
# ============================================================
