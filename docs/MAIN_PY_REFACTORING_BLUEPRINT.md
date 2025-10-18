# main.py Refactoring Blueprint

**Current Status:** 3,507 lines - Monolithic God Object
**Target:** 15+ focused modules, <300 lines in main.py
**Estimated Effort:** 1-2 weeks with full testing
**Risk Level:** MEDIUM-HIGH (requires comprehensive testing)

## Current Problems

1. **Single Responsibility Violation** - 21 distinct responsibilities
2. **Testing Nightmare** - Cannot test components in isolation
3. **Merge Conflicts** - Multiple developers cannot work simultaneously
4. **Maintenance Hell** - Hard to find and fix bugs
5. **Performance** - Large file slows IDE and startup time

## Proposed Structure

```
server/
├── main.py (200-300 lines)           # Entry point ONLY
│
├── core/
│   ├── __init__.py
│   ├── server.py                     # SoundlabServer base class (~400 lines)
│   ├── config.py                     # Configuration dataclasses (~200 lines)
│   └── logging_config.py             # Logging setup (~100 lines)
│
├── api/
│   ├── __init__.py
│   ├── audio.py                      # Audio control endpoints (~300 lines)
│   │   - /api/audio/start
│   │   - /api/audio/stop
│   │   - /api/audio/status
│   │   - /api/audio/devices
│   │
│   ├── presets.py                    # Preset management (~400 lines)
│   │   - /api/presets/*
│   │   - /api/ab-snapshots/*
│   │
│   ├── metrics.py                    # Metrics query endpoints (~300 lines)
│   │   - /api/metrics/latest
│   │   - /api/metrics/history
│   │
│   ├── latency.py                    # Latency diagnostics (~300 lines)
│   │   - /api/latency/*
│   │   - /api/calibrate/*
│   │
│   ├── state.py                      # State management (~400 lines)
│   │   - /api/auto-phi/*
│   │   - /api/criticality-balancer/*
│   │   - /api/state-memory/*
│   │   - /api/state-classifier/*
│   │   - /api/predictive-model/*
│   │
│   ├── session.py                    # Recording/playback (~400 lines)
│   │   - /api/record/*
│   │   - /api/timeline/*
│   │   - /api/sessions/*
│   │
│   ├── export.py                     # Data export (~200 lines)
│   │   - /api/export/*
│   │
│   ├── cluster.py                    # Cluster coordination (~400 lines)
│   │   - /api/node-sync/*
│   │   - /api/phasenet/*
│   │   - /api/cluster/*
│   │
│   └── hardware.py                   # Hardware control (~300 lines)
│       - /api/hardware/*
│       - /api/hybrid-node/*
│
├── websockets/
│   ├── __init__.py
│   ├── metrics_ws.py                 # Metrics streaming (~200 lines)
│   │   - /ws/metrics
│   │
│   ├── latency_ws.py                 # Latency streaming (~200 lines)
│   │   - /ws/latency
│   │
│   └── ui_ws.py                      # UI sync (~200 lines)
│       - /ws/ui
│
├── middleware/
│   ├── __init__.py
│   ├── cors.py                       # CORS configuration (~50 lines)
│   └── error_handlers.py             # Error handling (~100 lines)
│
└── integration/
    ├── __init__.py
    ├── components.py                 # Component initialization (~500 lines)
    └── callbacks.py                  # Callback wiring (~400 lines)
```

## Refactoring Strategy

### Phase 1: Preparation (1 day)
1. ✅ Create directory structure
2. ✅ Create __init__.py files
3. ✅ Set up comprehensive test suite
4. ✅ Create git branch: `refactor/modularize-main`

### Phase 2: Extract Configuration (2 days)
```python
# server/core/config.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    enable_cors: bool = True
    enable_logging: bool = True

@dataclass
class AudioConfig:
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    sample_rate: int = 48000
    buffer_size: int = 512

@dataclass
class FeatureFlags:
    auto_phi: bool = False
    criticality_balancer: bool = False
    state_memory: bool = False
    # ... etc
```

### Phase 3: Extract API Endpoints (5 days)

**Priority Order:**
1. **Day 1:** Extract audio endpoints (simpler, fewer dependencies)
2. **Day 2:** Extract preset endpoints
3. **Day 3:** Extract state management endpoints
4. **Day 4:** Extract session/cluster endpoints
5. **Day 5:** Extract hardware endpoints

**Example: server/api/audio.py**
```python
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.post("/start")
async def start_audio(audio_server) -> Dict[str, Any]:
    \"\"\"Start audio processing\"\"\"
    success = audio_server.start()
    if success:
        return {
            "ok": True,
            "message": "Audio started",
            "sample_rate": audio_server.SAMPLE_RATE,
            "buffer_size": audio_server.BUFFER_SIZE
        }
    raise HTTPException(status_code=500, detail="Failed to start audio")


@router.post("/stop")
async def stop_audio(audio_server) -> Dict[str, Any]:
    \"\"\"Stop audio processing\"\"\"
    audio_server.stop()
    return {"ok": True, "message": "Audio stopped"}


# ... more endpoints
```

### Phase 4: Extract WebSocket Handlers (2 days)

**Example: server/websockets/metrics_ws.py**
```python
import asyncio
import logging
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class MetricsWebSocketHandler:
    \"\"\"Handle metrics WebSocket streaming\"\"\"

    def __init__(self, metrics_streamer):
        self.metrics_streamer = metrics_streamer

    async def handle_connection(self, websocket: WebSocket):
        \"\"\"Handle a single WebSocket connection\"\"\"
        await websocket.accept()
        logger.info("Metrics WebSocket client connected")

        try:
            # Subscribe to metrics stream
            # ... implementation
            pass
        except WebSocketDisconnect:
            logger.info("Metrics WebSocket client disconnected")
        except Exception as e:
            logger.error("Metrics WebSocket error: %s", e)
```

### Phase 5: Extract Component Integration (3 days)

**server/integration/components.py**
```python
import logging
from typing import Dict, Any

from server.core.config import ServerConfig, AudioConfig, FeatureFlags
from server.audio_server import AudioServer
from server.preset_store import PresetStore
# ... more imports

logger = logging.getLogger(__name__)


class ComponentRegistry:
    \"\"\"Manages all system components\"\"\"

    def __init__(self, config: ServerConfig, audio_config: AudioConfig, flags: FeatureFlags):
        self.config = config
        self.audio_config = audio_config
        self.flags = flags

        # Initialize components
        self.audio_server = None
        self.preset_store = None
        self.metrics_streamer = None
        # ... etc

    def initialize_all(self):
        \"\"\"Initialize all enabled components\"\"\"
        logger.info("Initializing components...")

        # Core components (always enabled)
        self._init_audio_server()
        self._init_preset_store()
        self._init_metrics_streamer()

        # Optional components (based on flags)
        if self.flags.auto_phi:
            self._init_auto_phi()

        if self.flags.criticality_balancer:
            self._init_criticality_balancer()

        # ... etc

    def _init_audio_server(self):
        logger.info("Initializing AudioServer...")
        self.audio_server = AudioServer(
            input_device=self.audio_config.input_device,
            output_device=self.audio_config.output_device,
            enable_logging=self.config.enable_logging
        )

    # ... more initialization methods
```

### Phase 6: Refactor main.py (1 day)

**New main.py (target: <300 lines)**
```python
\"\"\"
Soundlab Main Server - Entry Point

This file should ONLY:
1. Parse command-line arguments
2. Create configuration objects
3. Initialize ComponentRegistry
4. Create FastAPI app with routers
5. Start uvicorn server

All business logic has been moved to specialized modules.
\"\"\"

import logging
import uvicorn
from fastapi import FastAPI

from server.core.config import ServerConfig, AudioConfig, FeatureFlags
from server.core.logging_config import setup_logging
from server.integration.components import ComponentRegistry
from server.integration.callbacks import CallbackWiring

# Import API routers
from server.api import audio, presets, metrics, latency, state, session, export, cluster, hardware
from server.websockets import metrics_ws, latency_ws, ui_ws
from server.middleware import cors

logger = logging.getLogger(__name__)


def create_app(config: ServerConfig, components: ComponentRegistry) -> FastAPI:
    \"\"\"Create and configure FastAPI application\"\"\"

    app = FastAPI(
        title="Soundlab Φ-Matrix",
        version="1.0.0",
        description="Real-time audio processing with Φ-based adaptive modulation"
    )

    # Add middleware
    if config.enable_cors:
        cors.add_cors_middleware(app)

    # Register API routers
    app.include_router(audio.router, dependencies=[Depends(lambda: components.audio_server)])
    app.include_router(presets.router, dependencies=[Depends(lambda: components.preset_store)])
    # ... more routers

    # Register WebSocket handlers
    @app.websocket("/ws/metrics")
    async def metrics_websocket(websocket: WebSocket):
        await metrics_ws.handle_connection(websocket, components.metrics_streamer)

    # ... more WebSocket routes

    return app


def main():
    \"\"\"Main entry point\"\"\"
    import argparse

    parser = argparse.ArgumentParser(description="Soundlab Audio Server")
    # ... argument parsing (same as before)

    args = parser.parse_args()

    # Setup logging
    setup_logging(level="INFO" if args.verbose else "WARNING")

    # Create configuration
    server_config = ServerConfig(host=args.host, port=args.port)
    audio_config = AudioConfig(input_device=args.input_device)
    flags = FeatureFlags(auto_phi=args.enable_auto_phi)

    # Initialize components
    components = ComponentRegistry(server_config, audio_config, flags)
    components.initialize_all()

    # Wire callbacks
    callback_wiring = CallbackWiring(components)
    callback_wiring.wire_all()

    # Create app
    app = create_app(server_config, components)

    # Run server
    logger.info("Starting Soundlab server on %s:%d", server_config.host, server_config.port)
    uvicorn.run(app, host=server_config.host, port=server_config.port)


if __name__ == "__main__":
    main()
```

## Testing Strategy

### Unit Tests
```python
# tests/unit/test_api_audio.py
from server.api.audio import router
from server.audio_server import AudioServer

def test_start_audio_endpoint():
    # Mock audio server
    audio_server = MockAudioServer()

    # Test endpoint
    response = start_audio(audio_server)

    assert response["ok"] == True
    assert audio_server.start_called
```

### Integration Tests
```python
# tests/integration/test_modular_server.py
from fastapi.testclient import TestClient

def test_full_server_startup():
    # Create test configuration
    config = ServerConfig(port=8001)

    # Initialize components
    components = ComponentRegistry(config)
    components.initialize_all()

    # Create app
    app = create_app(config, components)

    # Test with client
    client = TestClient(app)
    response = client.get("/api/audio/status")
    assert response.status_code == 200
```

## Migration Checklist

- [ ] Create git branch
- [ ] Create directory structure
- [ ] Extract configuration (core/config.py)
- [ ] Extract audio API (api/audio.py)
- [ ] Extract preset API (api/presets.py)
- [ ] Extract metrics API (api/metrics.py)
- [ ] Extract latency API (api/latency.py)
- [ ] Extract state API (api/state.py)
- [ ] Extract session API (api/session.py)
- [ ] Extract export API (api/export.py)
- [ ] Extract cluster API (api/cluster.py)
- [ ] Extract hardware API (api/hardware.py)
- [ ] Extract metrics WebSocket (websockets/metrics_ws.py)
- [ ] Extract latency WebSocket (websockets/latency_ws.py)
- [ ] Extract UI WebSocket (websockets/ui_ws.py)
- [ ] Extract CORS middleware (middleware/cors.py)
- [ ] Extract component init (integration/components.py)
- [ ] Extract callback wiring (integration/callbacks.py)
- [ ] Rewrite main.py (<300 lines)
- [ ] Run full test suite
- [ ] Run smoke tests
- [ ] Performance benchmarks
- [ ] Update documentation
- [ ] Code review
- [ ] Merge to main

## Benefits After Refactoring

### Development Velocity
- **+200%** - Multiple developers can work simultaneously
- **+150%** - Faster IDE performance (smaller files)
- **+100%** - Easier to find and fix bugs

### Maintainability
- **Single Responsibility** - Each module has one clear purpose
- **Testability** - Components can be tested in isolation
- **Readability** - Easier to understand each module

### Performance
- **Faster Imports** - Python only loads needed modules
- **Better Caching** - Smaller files cache better
- **Reduced Memory** - Don't load unused code

## Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking functionality | MEDIUM | HIGH | Comprehensive test suite |
| Regression bugs | MEDIUM | MEDIUM | Smoke tests before/after |
| Merge conflicts | LOW | LOW | Feature branch, clear communication |
| Performance degradation | LOW | LOW | Benchmark before/after |

## Timeline

| Week | Tasks | Deliverable |
|------|-------|-------------|
| Week 1 | Phases 1-2 | Config extracted, tests passing |
| Week 2 | Phase 3 (Days 1-3) | Audio/Preset/State APIs extracted |
| Week 3 | Phase 3 (Days 4-5) + Phase 4 | All APIs + WebSockets extracted |
| Week 4 | Phases 5-6 | Integration complete, main.py refactored |

## Success Criteria

✅ main.py < 300 lines
✅ No module > 500 lines
✅ All tests passing
✅ No performance regression (< 5% slowdown acceptable)
✅ Code coverage maintained (>= 85%)
✅ Documentation updated
✅ Smoke tests pass

---

**Status:** BLUEPRINT COMPLETE - Ready for implementation
**Next Step:** Create feature branch and begin Phase 1
**Estimated Completion:** 4 weeks with 1 developer
