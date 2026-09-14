from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.config import get_settings

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def index(request: Request):
    settings = get_settings()
    holder = request.app.state.holder
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "app_title": settings.app_title,
            "model_repo_id": settings.model_repo_id,
            "dataset_repo_id": settings.dataset_repo_id,
            "model_ready": holder.model_ready,
            "dataset_ready": holder.dataset_ready,
            "model_error": holder.model_error,
            "dataset_error": holder.dataset_error,
        },
    )
