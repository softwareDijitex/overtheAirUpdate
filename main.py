from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

def frontend(build_dir="./build"):
    """
     FASTAPI ROUTER FOR REACT FRONTEND
    :param build_dir: the path to your build folder for react
            we are assuming the "static" folder lives within your build folder
            if not, change it some lines below
    :return: fastapi.FastAPI
    """

    import pathlib
    import fastapi.exceptions
    from fastapi import FastAPI, Request, Response
    from fastapi.staticfiles import StaticFiles

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
    "https://battery-monitor-webapp-endhfdbxavdqhtef.centralindia-01.azurewebsites.net/",
]

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

# Initialize Flask components for FastAPI compatibility
from app import init_fastapi_components
init_fastapi_components()

# Import and include API routes
from app.routes.customer_routes import customer_bp
from app.routes.machine_routes import machine_bp
from app.routes.file_routes import file_bp

# Include API routes
app.include_router(customer_bp, prefix="/api/customers", tags=["customers"])
app.include_router(machine_bp, prefix="/api/machines", tags=["machines"])
app.include_router(file_bp, prefix="/api/files", tags=["files"])

# Health check endpoint
@app.get('/health')
def health_check():
    return Response(status_code=204)

# CORS preflight handler
@app.options("/{full_path:path}")
async def options_handler():
    return Response(status_code=200)

# Debug endpoint to test CORS
@app.get('/api/test-cors')
def test_cors():
    return {"message": "CORS is working!", "timestamp": "2024-01-01T00:00:00Z"}

static_folder = os.path.join(os.path.dirname(__file__), 'frontendapp', 'build')
static_dir = os.path.join(static_folder, 'static')

app.mount("/", frontend(build_dir="./frontendapp/build"))

# Only mount if static_dir exists
# if os.path.isdir(static_dir):
#     app.mount("/static", StaticFiles(directory=static_dir), name="static")

# # Serve React index.html for all other routes (client-side routing)
# @app.get("/{full_path:path}")
# def serve_react_app(full_path: str):
#     index_path = os.path.join(static_folder, 'index.html')
#     if os.path.exists(index_path):
#         return FileResponse(index_path)
#     return Response(content="index.html not found", status_code=404) 