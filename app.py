from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import pathlib
import fastapi.exceptions
from app import get_mongo_client, get_database, init_fastapi_components
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError


def frontend(build_dir="./build"):
    """
     FASTAPI ROUTER FOR REACT FRONTEND
    :param build_dir: the path to your build folder for react
            we are assuming the "static" folder lives within your build folder
            if not, change it some lines below
    :return: fastapi.FastAPI
    """

    build_dir = pathlib.Path(build_dir)

    react = FastAPI(openapi_url="")
    react.mount('/static', StaticFiles(directory=build_dir / "static"))
    
    @react.get('/{path:path}')
    async def handle_catch_all(request: Request, path):

        if path and path != "/":
            disk_path = build_dir / path
            if disk_path.exists():
                return Response(disk_path.read_bytes(), 200)
            else:
                if disk_path.is_file():
                    raise fastapi.exceptions.HTTPException(404)

        return Response((build_dir / "index.html").read_bytes(), 200)

    return react

# Define CORS origins at module level
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:3000",
    "http://0.0.0.0:8000",
    "https://battery-monitor-webapp-endhfdbxavdqhtef.centralindia-01.azurewebsites.net",
]

# Create FastAPI app
app = FastAPI(
    title="Customer Management System API",
    description="API for managing customers, machines, and files",
    version="1.0.0"
)

# Add CORS middleware BEFORE including routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize DB handles on startup
@app.on_event("startup")
def _init_db_handles():
    app.state.mongo_client = get_mongo_client()
    app.state.db = get_database()

# Simple DB health endpoint
@app.get('/db/health')
def db_health():
    try:
        app.state.mongo_client.admin.command('ping')
        return {"ok": True}
    except Exception:
        return Response(status_code=500)

# Initialize FastAPI components
init_fastapi_components()

# Import and include API routes FIRST
from app.routes.customer_routes import customer_bp
from app.routes.machine_routes import machine_bp
from app.routes.file_routes import file_bp
from app.routes.machineHardware_routes import hardware_bp

# Include API routes BEFORE mounting frontend
app.include_router(customer_bp, prefix="/api/customers", tags=["customers"])
app.include_router(machine_bp, prefix="/api/machines", tags=["machines"])
app.include_router(file_bp, prefix="/api/files", tags=["files"])
app.include_router(hardware_bp, prefix="/api/hardware", tags=["hardware"])

# Add specific API endpoints
@app.get('/health')
def health_check():
    return Response(status_code=204)


@app.get('/api/test-cors')
def test_cors():
    return {"message": "CORS is working!", "timestamp": "2024-01-01T00:00:00Z"}

# Add debug endpoint to see all routes
@app.get("/debug/routes")
def list_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unknown')
            })
    return {"routes": routes}

# CORS preflight handler
@app.options("/{full_path:path}")
async def options_handler():
    return Response(status_code=200)

# Mount the React frontend LAST (this catches all remaining routes)
static_folder = os.path.join(os.path.dirname(__file__), 'frontendapp', 'build')
app.mount("/", frontend(build_dir="./frontendapp/build"))

