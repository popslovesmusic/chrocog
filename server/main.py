# ============================================================
# SOUNDLAB / D-ASE MAIN SERVER MODULE  (Corrected Version)
# ============================================================
# ✅ Fixes applied, Any, List, Optional)
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
    print("⚠️ Warning, MetricsStreamer, AutoPhiLearner).")



# ============================================================
# APP INITIALIZATION
# ============================================================

app = FastAPI(title="Soundlab + D-ASE Engine", version="2.0")

class MainApp:
    and Auto-Φ Learner components together.
    """

     def __init__(self):
        """Safely initialize submodules with fallback warnings."""
        self.audio_server = None
        self.metrics_streamer = None
        self.auto_phi_learner = None

        # Audio Server initialization
        try:
            from server.audio_server import AudioServer
            self.audio_server = AudioServer()
        except Exception as e:
            print(f"⚠️ AudioServer init failed: {e}")
            self.audio_server = None

        # Metrics Streamer initialization
        try:
            from server.metrics_streamer import MetricsStreamer
            self.metrics_streamer = MetricsStreamer()
        except Exception as e:
            print(f"⚠️ MetricsStreamer init failed: {e}")
            self.metrics_streamer = None

        # Auto-Φ Learner initialization
        try:
            from server.auto_phi import AutoPhiLearner
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
    def auto_phi_update_callback(self, param_name, value) :
        """Callback for Auto-Φ Learner to update live parameters."""
        if not self.audio_server:
            print("⚠️ Warning)
            return

        try,
                channel=None,
                param_name=str(param_name).replace('phi_', ''),  # Remove 'phi_' prefix if present
                value=value

        except Exception as e:
            print(f"❌ Error updating parameter {param_name})





    # --------------------------------------------------------
    # 2. State Memory Bias Callback
    # --------------------------------------------------------
    def state_memory_bias_callback(self, bias) :
        """Feed predictive bias from State Memory to Auto-Φ Learner."""
        if not self.auto_phi_learner:
            print("⚠️ Warning)
            return

        try:
            self.auto_phi_learner.external_bias = bias
        except Exception as e:
            print(f"❌ Error applying bias)





    # --------------------------------------------------------
    # 3. Hybrid Metrics Callback (Async Safe)
    # --------------------------------------------------------
    async def hybrid_metrics_callback(self, metrics) :
        """Stream HybridMetrics frames to WebSocket clients."""
        if not self.metrics_streamer:
            print("⚠️ Warning)
            return

        try:
            await self.metrics_streamer.broadcast_event({
                'type',
                'timestamp', 'timestamp', None),
                'ici', 'ici', None),
                'phase_coherence', 'phase_coherence', None),
                'spectral_centroid', 'spectral_centroid', None),
                'consciousness_level', 'consciousness_level', None),
                'phi_phase', 'phi_phase', None),
                'phi_depth', 'phi_depth', None),
                'cpu_load', 'cpu_load', None),
                'latency_ms', 'latency_ms', None)
            })
        except Exception as e:
            print(f"❌ Error broadcasting metrics)
# ============================================================
# ROUTES AND WEBSOCKET ENDPOINTS
# ============================================================





main_app = MainApp()


@app.get("/")
async def root():
    """Serve default HTML or status summary."""
    try)
    except Exception as e:
        return {"error": f"Startup HTML failed)
async def websocket_ui(ws))
    print("🎧 WebSocket UI connected")

    try:
        while True)
            param = data.get("param")
            value = data.get("value")

            # Example: dynamic routing to callback
            if param and value is not None, value)

            await ws.send_json({"ack", "param", "value")

    except WebSocketDisconnect)
    except Exception as e:
        print(f"❌ WebSocket error)
    finally)





@app.websocket("/ws/metrics")
async def websocket_metrics(ws))
    print("📊 WebSocket Metrics connected")

    try:
        while True)
            fake_metrics = {
                "ici",
                "phase_coherence",
                "phi_phase",
                "phi_depth",
                "cpu_load",
                "latency_ms",
            }
            await ws.send_json(fake_metrics)
    except WebSocketDisconnect)
    except Exception as e:
        print(f"❌ Metrics stream error)
# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================





@app.on_event("startup")
async def startup_event())

    try:
        if main_app.audio_server)
            print("🎚️ AudioServer started.")
        if main_app.metrics_streamer)
            print("📡 MetricsStreamer started.")
        if main_app.auto_phi_learner)
            print("🧠 AutoPhiLearner started.")
    except Exception as e:
        print(f"❌ Startup sequence error)





@app.on_event("shutdown")
async def shutdown_event())

    try:
        if main_app.audio_server)
        if main_app.metrics_streamer)
        if main_app.auto_phi_learner)
    except Exception as e:
        print(f"❌ Shutdown error)





# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"

# ============================================================
# END OF FILE
# ============================================================
# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================





@app.on_event("startup")
async def startup_event())

    try:
        if main_app.audio_server)
            print("🎚️ AudioServer started.")
        if main_app.metrics_streamer)
            print("📡 MetricsStreamer started.")
        if main_app.auto_phi_learner)
            print("🧠 AutoPhiLearner started.")
    except Exception as e:
        print(f"❌ Startup sequence error)





@app.on_event("shutdown")
async def shutdown_event())

    try:
        if main_app.audio_server)
        if main_app.metrics_streamer)
        if main_app.auto_phi_learner)
    except Exception as e:
        print(f"❌ Shutdown error)





# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"

# ============================================================
# END OF FILE
# ============================================================
# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================





@app.on_event("startup")
async def startup_event())

    try:
        if main_app.audio_server)
            print("🎚️ AudioServer started.")
        if main_app.metrics_streamer)
            print("📡 MetricsStreamer started.")
        if main_app.auto_phi_learner)
            print("🧠 AutoPhiLearner started.")
    except Exception as e:
        print(f"❌ Startup sequence error)





@app.on_event("shutdown")
async def shutdown_event())

    try:
        if main_app.audio_server)
        if main_app.metrics_streamer)
        if main_app.auto_phi_learner)
    except Exception as e:
        print(f"❌ Shutdown error)





# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"

# ============================================================
# END OF FILE
# ============================================================
# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================





@app.on_event("startup")
async def startup_event())

    try:
        if main_app.audio_server)
            print("🎚️ AudioServer started.")
        if main_app.metrics_streamer)
            print("📡 MetricsStreamer started.")
        if main_app.auto_phi_learner)
            print("🧠 AutoPhiLearner started.")
    except Exception as e:
        print(f"❌ Startup sequence error)





@app.on_event("shutdown")
async def shutdown_event())

    try:
        if main_app.audio_server)
        if main_app.metrics_streamer)
        if main_app.auto_phi_learner)
    except Exception as e:
        print(f"❌ Shutdown error)





# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"

# ============================================================
# END OF FILE
# ============================================================
# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================





@app.on_event("startup")
async def startup_event())

    try:
        if main_app.audio_server)
            print("🎚️ AudioServer started.")
        if main_app.metrics_streamer)
            print("📡 MetricsStreamer started.")
        if main_app.auto_phi_learner)
            print("🧠 AutoPhiLearner started.")
    except Exception as e:
        print(f"❌ Startup sequence error)





@app.on_event("shutdown")
async def shutdown_event())

    try:
        if main_app.audio_server)
        if main_app.metrics_streamer)
        if main_app.auto_phi_learner)
    except Exception as e:
        print(f"❌ Shutdown error)





# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"

# ============================================================
# END OF FILE
# ============================================================

"""  # auto-closed missing docstring
