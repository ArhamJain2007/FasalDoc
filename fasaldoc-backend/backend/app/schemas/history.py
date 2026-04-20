from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


# ── History ────────────────────────────────────────────────────────────────────

class ScanHistoryItem(BaseModel):
    scan_id: str
    disease_name: str
    crop_name: str
    confidence: float
    stage: str
    image_url: str
    status: str
    treatment_id: str | None
    scan_date: str


class ScanHistoryResponse(BaseModel):
    items: list[ScanHistoryItem]
    total: int
    page: int
    page_size: int


class ScanDetailResponse(ScanHistoryItem):
    disease_name_hi: str | None = None
    crop_name_hi: str | None = None
    synced_from_offline: bool = False


class UpdateScanStatusRequest(BaseModel):
    status: Literal["active", "treated", "resolved"]


# ── Alert ───────────────────────────────────────────────────────────────────────

class AlertResponse(BaseModel):
    alert_id: str
    region: str
    alert_type: Literal["danger", "warning", "info"]
    title: str
    body: str
    related_disease_id: str | None = None
    expires_at: str


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
    region: str


# ── Treatment ───────────────────────────────────────────────────────────────────

class TreatmentItem(BaseModel):
    treatment_id: str
    type: Literal["organic", "chemical"]
    name: str
    dosage: str
    schedule: str


class TreatmentResponse(BaseModel):
    disease_id: str
    disease_name: str
    crop_name: str
    description: str
    severity: str
    treatments: list[TreatmentItem]


# ── Sync ────────────────────────────────────────────────────────────────────────

class ScanRecord(BaseModel):
    id: str
    disease_name: str
    crop_name: str
    confidence: float = Field(ge=0.0, le=100.0)
    stage: str
    image_uri: str
    scan_date: str
    status: Literal["active", "treated", "resolved"]
    treatment_id: str
    disease_class_index: int = 0


class SyncRequest(BaseModel):
    records: list[ScanRecord] = Field(..., max_length=200)


class SyncResponse(BaseModel):
    synced: list[str]
    skipped: list[str] = Field(default_factory=list)
    total_received: int
    total_synced: int


# ── Notification ────────────────────────────────────────────────────────────────

class RegisterTokenRequest(BaseModel):
    token: str = Field(..., min_length=10)
    platform: Literal["android", "ios"] = "android"


class RegisterTokenResponse(BaseModel):
    message: str
