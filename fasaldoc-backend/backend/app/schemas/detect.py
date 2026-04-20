from pydantic import BaseModel, Field
from typing import Literal


class DetectionResponse(BaseModel):
    scan_id: str
    disease_name: str
    crop_name: str
    confidence: float = Field(ge=0.0, le=100.0)
    stage: Literal["Stage 1", "Stage 2", "Stage 3"]
    treatment_id: str
    description: str        # translated disease description
    image_url: str
    scan_date: str
    # severity is derived from stage by the frontend api.ts,
    # but also returned here for convenience
    severity: Literal["low", "medium", "high"] = "medium"


class DetectionErrorResponse(BaseModel):
    error: str
    message: str
    detail: dict = Field(default_factory=dict)
