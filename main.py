"""Main application entry point."""
import uvicorn
from src.api.routes import app
from src.core.config import settings


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        log_level="info"
    )
