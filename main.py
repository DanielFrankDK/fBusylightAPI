from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from api.routes import router

_html = (Path(__file__).parent / "static/index.html").read_text()

app = FastAPI(
    title="Luxafor FLAG API",
    description="Local REST API to control the Luxafor FLAG Busylight over USB HID.",
    version="1.0.0",
)

app.include_router(router)

@app.get("/", response_class=HTMLResponse)
def index():
    return _html

if __name__ == "__main__":
    import preflight
    preflight.run()

    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
