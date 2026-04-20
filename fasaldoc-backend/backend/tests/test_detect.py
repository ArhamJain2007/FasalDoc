"""
Tests for POST /api/v1/detect endpoint.
Uses a mock ML model to avoid loading TensorFlow in CI.
"""
import io
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import AsyncClient
from PIL import Image

from app.ml.postprocessing import PredictionResult


def make_mock_result() -> PredictionResult:
    return PredictionResult(
        disease_name="Early Blight",
        crop_name="Tomato",
        disease_name_hi="अगेती झुलसा",
        crop_name_hi="टमाटर",
        disease_name_pa="ਅਗੇਤੀ ਝੁਲਸ",
        crop_name_pa="ਟਮਾਟਰ",
        confidence=82.5,
        class_index=32,
        class_label="Tomato___Early_blight",
        disease_id="tomato_early_blight",
        stage="Stage 2",
        all_probs={"Tomato___Early_blight": 82.5},
    )


@pytest.mark.asyncio
async def test_detect_rejects_non_image(client: AsyncClient, auth_headers: dict):
    """Uploading a PDF should return 400 INVALID_FILE_TYPE."""
    response = await client.post(
        "/api/v1/detect",
        files={"file": ("doc.pdf", b"fake pdf content", "application/pdf")},
        headers=auth_headers,
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "INVALID_FILE_TYPE"


@pytest.mark.asyncio
async def test_detect_rejects_oversized_file(client: AsyncClient, auth_headers: dict, large_image_bytes: bytes):
    """Uploading >10MB should return 413 FILE_TOO_LARGE."""
    response = await client.post(
        "/api/v1/detect",
        files={"file": ("big.jpg", large_image_bytes, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 413
    body = response.json()
    assert body["error"] == "FILE_TOO_LARGE"


@pytest.mark.asyncio
async def test_detect_requires_auth(client: AsyncClient, test_image_bytes: bytes):
    """Unauthenticated request should return 401."""
    response = await client.post(
        "/api/v1/detect",
        files={"file": ("leaf.jpg", test_image_bytes, "image/jpeg")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_detect_returns_valid_response(
    client: AsyncClient,
    auth_headers: dict,
    test_image_bytes: bytes,
):
    """Full detection pipeline returns correct schema with mocked ML model."""
    mock_result = make_mock_result()

    with (
        patch("app.api.v1.detect.ModelLoader.is_loaded", return_value=True),
        patch("app.api.v1.detect.DetectionService.detect", new=AsyncMock(return_value=mock_result)),
        patch("app.api.v1.detect.StorageService.upload", new=AsyncMock(return_value="https://s3.example.com/test.jpg")),
        patch("app.api.v1.detect.DetectionService.enrich", new=AsyncMock()) as mock_enrich,
        patch("app.api.v1.detect.DetectionService.save_scan", new=AsyncMock()) as mock_save,
    ):
        from app.services.detection_service import EnrichedResult
        from app.models.scan import Scan
        from datetime import datetime
        from uuid import uuid4

        mock_enrich.return_value = EnrichedResult(
            disease_name="Early Blight",
            crop_name="Tomato",
            treatment_id="some-treatment-uuid",
            description="Early blight fungal disease.",
        )
        mock_scan = MagicMock(spec=Scan)
        mock_scan.id = uuid4()
        mock_scan.created_at = datetime.utcnow()
        mock_save.return_value = mock_scan

        response = await client.post(
            "/api/v1/detect",
            files={"file": ("leaf.jpg", test_image_bytes, "image/jpeg")},
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert "disease_name" in data
    assert "crop_name" in data
    assert 0 <= data["confidence"] <= 100
    assert data["stage"] in ["Stage 1", "Stage 2", "Stage 3"]
    assert "treatment_id" in data
    assert "scan_id" in data
    assert "image_url" in data


@pytest.mark.asyncio
async def test_detect_language_param_valid(
    client: AsyncClient,
    auth_headers: dict,
    test_image_bytes: bytes,
):
    """Language param accepts en, hi, pa."""
    for lang in ["en", "hi", "pa"]:
        response = await client.post(
            f"/api/v1/detect?language={lang}",
            files={"file": ("leaf.jpg", test_image_bytes, "image/jpeg")},
            headers=auth_headers,
        )
        # May be 200 or non-400/422 (model not loaded in test env)
        assert response.status_code != 422 or "language" not in str(response.json())


@pytest.mark.asyncio
async def test_detect_language_param_invalid(
    client: AsyncClient,
    auth_headers: dict,
    test_image_bytes: bytes,
):
    """Invalid language param should return 422."""
    response = await client.post(
        "/api/v1/detect?language=fr",
        files={"file": ("leaf.jpg", test_image_bytes, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_detect_model_not_loaded(
    client: AsyncClient,
    auth_headers: dict,
    test_image_bytes: bytes,
):
    """When model is not loaded, should return 503."""
    with patch("app.api.v1.detect.ModelLoader.is_loaded", return_value=False):
        response = await client.post(
            "/api/v1/detect",
            files={"file": ("leaf.jpg", test_image_bytes, "image/jpeg")},
            headers=auth_headers,
        )
    assert response.status_code == 503
    assert response.json()["error"] == "MODEL_NOT_LOADED"
