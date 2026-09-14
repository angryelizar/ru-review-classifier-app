from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["api"])


class PredictRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


class PredictResponse(BaseModel):
    label: str
    raw_label: str
    score: float
    scores: dict[str, float]


class SampleResponse(BaseModel):
    text: str
    label: str
    src: str


@router.post("/predict", response_model=PredictResponse)
def predict(body: PredictRequest, request: Request) -> dict:
    holder = request.app.state.holder
    try:
        return holder.predict(body.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/sample", response_model=SampleResponse)
def sample(request: Request) -> dict:
    holder = request.app.state.holder
    try:
        return holder.random_sample()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
