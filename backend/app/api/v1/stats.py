from typing import Dict, Any
from fastapi import APIRouter, Depends, Response
from app.api.dependencies import get_metrics_service
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/stats", tags=["Observability"])


@router.get("", response_model=Dict[str, Any])
def get_system_stats(
    service: MetricsService = Depends(get_metrics_service),
):
    """Retrieve search engine health, indexing stats, and cache performance."""
    return service.get_system_stats()


@router.get("/prometheus")
def get_prometheus_metrics(
    service: MetricsService = Depends(get_metrics_service),
):
    """Expose Prometheus formatted metrics for scrapers."""
    content = service.get_prometheus_metrics()
    return Response(content=content, media_type="text/plain; version=0.0.4")
