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
    "http://localhost",
    "http://localhost:8080",
    "http://0.0.0.0:8000",
    "https://battery-monitor-webapp-endhfdbxavdqhtef.centralindia-01.azurewebsites.net/",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get('/health')
def health_check():
    return Response(status_code=204)

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