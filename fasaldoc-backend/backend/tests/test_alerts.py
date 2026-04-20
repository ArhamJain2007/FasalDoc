"""
Tests for /api/v1/treatment and /api/v1/alerts endpoints.
"""
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.schemas.history import TreatmentResponse, TreatmentItem, AlertResponse, AlertListResponse


@pytest.mark.asyncio
async def test_get_treatment_success(client: AsyncClient, auth_headers: dict):
    """Known disease ID returns treatment plan."""
    mock_treatment = TreatmentResponse(
        disease_id="tomato_early_blight",
        disease_name="Early Blight",
        crop_name="Tomato",
        description="Early blight is caused by Alternaria solani.",
        severity="medium",
        treatments=[
            TreatmentItem(
                treatment_id="uuid-123",
                type="chemical",
                name="Mancozeb 75% WP",
                dosage="2.5 g/L water",
                schedule="Spray every 7-10 days",
            )
        ],
    )
    with patch(
        "app.api.v1.treatment.TreatmentService.get_treatment",
        new=AsyncMock(return_value=mock_treatment),
    ):
        response = await client.get(
            "/api/v1/treatment/tomato_early_blight",
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["disease_id"] == "tomato_early_blight"
    assert data["disease_name"] == "Early Blight"
    assert len(data["treatments"]) == 1
    assert data["treatments"][0]["type"] == "chemical"


@pytest.mark.asyncio
async def test_get_treatment_not_found(client: AsyncClient, auth_headers: dict):
    """Unknown disease ID returns 404."""
    with patch(
        "app.api.v1.treatment.TreatmentService.get_treatment",
        new=AsyncMock(return_value=None),
    ):
        response = await client.get(
            "/api/v1/treatment/nonexistent_disease",
            headers=auth_headers,
        )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_get_treatment_hindi(client: AsyncClient, auth_headers: dict):
    """Language=hi returns Hindi treatment names."""
    mock_treatment = TreatmentResponse(
        disease_id="tomato_early_blight",
        disease_name="अगेती झुलसा",
        crop_name="टमाटर",
        description="अगेती झुलसा एक फफूंद रोग है।",
        severity="medium",
        treatments=[
            TreatmentItem(
                treatment_id="uuid-456",
                type="chemical",
                name="मैन्कोज़ेब 75% WP",
                dosage="2.5 g/L पानी",
                schedule="हर 7-10 दिन छिड़काव करें",
            )
        ],
    )
    with patch(
        "app.api.v1.treatment.TreatmentService.get_treatment",
        new=AsyncMock(return_value=mock_treatment),
    ):
        response = await client.get(
            "/api/v1/treatment/tomato_early_blight?language=hi",
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["disease_name"] == "अगेती झुलसा"


@pytest.mark.asyncio
async def test_get_treatment_requires_auth(client: AsyncClient):
    """Unauthenticated request returns 401."""
    response = await client.get("/api/v1/treatment/tomato_early_blight")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_alerts_success(client: AsyncClient, auth_headers: dict):
    """Alerts endpoint returns list of alerts for region."""
    mock_alerts = [
        AlertResponse(
            alert_id="alert-uuid-1",
            region="Punjab",
            alert_type="warning",
            title="⚠️ Wheat Brown Rust Risk",
            body="Humidity above 80%. Apply Propiconazole.",
            related_disease_id="wheat_brown_rust",
            expires_at="2024-12-31T23:59:59",
        )
    ]
    with patch(
        "app.api.v1.alerts.AlertService.get_active_alerts",
        new=AsyncMock(return_value=mock_alerts),
    ):
        response = await client.get(
            "/api/v1/alerts?region=Punjab",
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["region"] == "Punjab"
    assert len(data["alerts"]) == 1
    assert data["alerts"][0]["alert_type"] == "warning"


@pytest.mark.asyncio
async def test_get_alerts_empty_region(client: AsyncClient, auth_headers: dict):
    """Region with no active alerts returns empty list."""
    with patch(
        "app.api.v1.alerts.AlertService.get_active_alerts",
        new=AsyncMock(return_value=[]),
    ):
        response = await client.get(
            "/api/v1/alerts?region=Meghalaya",
            headers=auth_headers,
        )
    assert response.status_code == 200
    assert response.json()["alerts"] == []


@pytest.mark.asyncio
async def test_get_alerts_requires_region(client: AsyncClient, auth_headers: dict):
    """Missing region param returns 422."""
    response = await client.get("/api/v1/alerts", headers=auth_headers)
    assert response.status_code == 422
