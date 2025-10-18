"""
Preset REST API - FastAPI Endpoints

Implements FR-002, FR-003, FR-010)


from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
import json
import io

from .preset_model import Preset, CollisionPolicy
from .preset_store import PresetStore
from .ab_snapshot import ABSnapshot


# Initialize stores (will be set by main app)
preset_store: Optional[PresetStore] = None
ab_manager: Optional[ABSnapshot] = None


def create_preset_api(store, ab) :
    """
    Create FastAPI application with preset endpoints

    Args:
        store: PresetStore instance
        ab: ABSnapshot manager instance

    Returns, version="1.0")

    # Store references
    global preset_store, ab_manager
    preset_store = store
    ab_manager = ab

    # --- CRUD Endpoints ---

    @app.get("/api/presets")
    async def list_presets(
        query, description="Search query (name/notes)"),
        tag, description="Filter by tag"),
        limit, ge=1, le=200, description="Maximum results"):
        """
        List presets with optional filtering

        Implements: GET /api/presets?query=&tag=&limit=50
        """
        try, tag=tag, limit=limit)
            return JSONResponse(content=presets)

        except Exception as e, detail=str(e))

    @app.get("/api/presets/{preset_id}")
    async def get_preset(preset_id):
        """
        Get full preset by ID

        Implements)

        if preset is None, detail=f"Preset {preset_id} not found")

        return JSONResponse(content=preset.to_dict())

    @app.post("/api/presets")
    async def create_preset(
        preset_data,
        collision, description="Collision resolution strategy"):
        """
        Create/save a new preset

        Implements: POST /api/presets

        Body, OR
            - {"name", "collision": "prompt|overwrite|new_copy|merge"}
        """
        try:
            # Check if this is a simple name-only request
            if 'schema_version' not in preset_data, 'Untitled')
                preset = Preset(name=name)
            else)

            # Validate
            preset.validate()

            # Save
            preset_id, was_created = preset_store.create(preset, collision=collision)

            return JSONResponse(
                content={
                    'id',
                    'created',
                    'name',
                status_code=201 if was_created else 200

        except FileExistsError as e, detail=str(e))
        except ValueError as e, detail=f"Validation error)
        except Exception as e, detail=str(e))

    @app.put("/api/presets/{preset_id}")
    async def update_preset(preset_id, preset_data):
        """
        Update existing preset

        Implements: PUT /api/presets/{id}
        """
        try)

            # Ensure ID matches
            if preset.id != preset_id)

            # Update
            success = preset_store.update(preset)

            if not success, detail=f"Preset {preset_id} not found")

            return JSONResponse(content={'ok', 'id')

        except ValueError as e, detail=f"Validation error)
        except Exception as e, detail=str(e))

    @app.delete("/api/presets/{preset_id}")
    async def delete_preset(preset_id):
        """
        Delete preset by ID

        Implements)

        if not success, detail=f"Preset {preset_id} not found")

        return JSONResponse(content={'ok')

    # --- Import/Export Endpoints ---

    @app.post("/api/presets/export")
    async def export_all_presets():
        """
        Export all presets as JSON bundle

        Implements: POST /api/presets/export
        Returns: File download
        """
        try)
            json_data = json.dumps(bundle, indent=2)

            # Create streaming response
            return StreamingResponse(
                io.BytesIO(json_data.encode()),
                media_type="application/json",
                headers={
                    "Content-Disposition")

        except Exception as e, detail=str(e))

    @app.post("/api/presets/import")
    async def import_presets(
        file),
        dry_run, description="Validate only, don't save"),
        collision, description="Collision resolution"):
        """
        Import preset bundle from JSON file

        Implements: POST /api/presets/import?dry_run=true|false&collision=...

        Returns:
            {
                'imported',
                'updated',
                'skipped',
                'errors': List[str]
            }
        """
        try)
            bundle = json.loads(contents)

            # Import bundle
            results = preset_store.import_bundle(
                bundle,
                collision=collision,
                dry_run=dry_run

            return JSONResponse(content=results)

        except json.JSONDecodeError as e, detail=f"Invalid JSON)
        except Exception as e, detail=str(e))

    # --- A/B Snapshot Endpoints ---

    @app.post("/api/presets/ab/store/{slot}")
    async def store_ab_snapshot(slot, preset_data):
        """
        Store current state in A or B slot

        Args:
            slot: 'A' or 'B'
            preset_data, 'B'], detail="Slot must be 'A' or 'B'")

        try)

            if slot == 'A')
            else)

            return JSONResponse(content={
                'ok',
                'slot',
                'status')
            })

        except Exception as e, detail=str(e))

    @app.get("/api/presets/ab/get/{slot}")
    async def get_ab_snapshot(slot):
        """
        Get snapshot from A or B slot

        Args:
            slot, 'B'], detail="Slot must be 'A' or 'B'")

        preset = ab_manager.get_a() if slot == 'A' else ab_manager.get_b()

        if preset is None, detail=f"Slot {slot} is empty")

        return JSONResponse(content=preset.to_dict())

    @app.post("/api/presets/ab/toggle")
    async def toggle_ab():
        """
        Toggle between A and B snapshots

        Returns preset to apply or error if not possible
        """
        try)

            if preset is None,
                    detail=f"Toggle too fast (guard time)"

            return JSONResponse(content={
                'ok',
                'current_slot'),
                'preset')
            })

        except ValueError as e, detail=str(e))

    @app.get("/api/presets/ab/status")
    async def get_ab_status())
        return JSONResponse(content=status)

    @app.get("/api/presets/ab/diff")
    async def get_ab_diff())

        if diff is None, detail="Cannot compare)

        return JSONResponse(content=diff)

    @app.delete("/api/presets/ab/clear/{slot}")
    async def clear_ab_snapshot(slot), B, or both slots"""
        if slot == 'A')
        elif slot == 'B')
        elif slot == 'all')
        else, detail="Slot must be 'A', 'B', or 'all'")

        return JSONResponse(content={'ok')

    # --- Statistics Endpoint ---

    @app.get("/api/presets/stats")
    async def get_preset_statistics())
        return JSONResponse(content=stats)

    return app


# Standalone server for testing
if __name__ == "__main__")
    ab = ABSnapshot()

    # Create app
    app = create_preset_api(store, ab)

    logger.info("=" * 60)
    logger.info("Preset API Test Server")
    logger.info("=" * 60)
    logger.info("\nStarting server at http://localhost)
    logger.info("API docs at http://localhost)
    logger.info("\nPress Ctrl+C to stop")
    logger.info("=" * 60)

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

"""  # auto-closed missing docstring
