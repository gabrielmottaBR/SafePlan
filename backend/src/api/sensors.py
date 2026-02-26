"""
SafePlan Backend - Sensor API Routes
REST endpoints for sensor management and monitoring
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.src.data.database import get_db
from backend.src.data.sensor_repository import SensorConfigRepository
from backend.src.data.reading_repository import SensorReadingRepository

router = APIRouter(prefix="/api/v1/sensors", tags=["Sensors"])


# ============ Pydantic Models (Request/Response) ============

class SensorConfigResponse(BaseModel):
    """Sensor configuration response model."""
    id: int
    sensor_id: str
    name: str
    sensor_type: str
    location: str
    unit: str
    grupo: Optional[str] = None
    modulo: Optional[str] = None
    valor_pct: Optional[float] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SensorReadingResponse(BaseModel):
    """Sensor reading response model."""
    id: int
    sensor_id: str
    value: float
    unit: str
    timestamp: datetime
    source: Optional[str] = None
    quality_code: Optional[str] = None
    
    class Config:
        from_attributes = True


class SensorStatsResponse(BaseModel):
    """Sensor statistics response."""
    sensor_id: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None
    reading_count: int
    time_window_hours: int


# ============ Sensor Endpoints ============

@router.get("/", response_model=dict)
async def list_sensors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    List all sensors with pagination.
    
    Query Parameters:
        - skip: Number of sensors to skip (default: 0)
        - limit: Max sensors to return (default: 100, max: 1000)
    """
    repo = SensorConfigRepository(db)
    sensors = repo.get_all(skip=skip, limit=limit)
    total = repo.count()
    
    # Convert SQLAlchemy objects to dicts
    sensors_data = []
    for sensor in sensors:
        sensor_dict = {
            'id': sensor.id,
            'sensor_id': sensor.sensor_id,
            'name': sensor.name,
            'description': sensor.description,
            'sensor_type': sensor.sensor_type,
            'location': sensor.location,
            'unit': sensor.unit,
            'grupo': sensor.grupo,
            'modulo': sensor.modulo,
            'is_active': sensor.is_active,
            'created_at': sensor.created_at.isoformat() if sensor.created_at else None,
        }
        sensors_data.append(sensor_dict)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": sensors_data,
    }


@router.get("/count", response_model=dict)
async def count_sensors(db: Session = Depends(get_db)):
    """Get total count of sensors."""
    repo = SensorConfigRepository(db)
    return {
        "total_sensors": repo.count(),
        "by_type": repo.count_by_type(),
        "by_location": repo.count_by_location(),
    }


@router.get("/{sensor_id}", response_model=SensorConfigResponse)
async def get_sensor(sensor_id: str, db: Session = Depends(get_db)):
    """Get sensor details by sensor_id."""
    repo = SensorConfigRepository(db)
    sensor = repo.get_by_sensor_id(sensor_id)
    
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor {sensor_id} not found")
    
    return sensor


@router.get("/{sensor_id}/readings", response_model=List[SensorReadingResponse])
async def get_sensor_readings(
    sensor_id: str,
    hours: int = Query(24, ge=1, le=24*30),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Get readings for a sensor from last N hours.
    
    Query Parameters:
        - hours: Time window in hours (1-720, default: 24)
        - limit: Max readings to return (default: 100)
    """
    repo_reading = SensorReadingRepository(db)
    readings = repo_reading.get_last_hours(sensor_id, hours=hours)
    
    # Return most recent first, up to limit
    return sorted(readings[-limit:], key=lambda x: x.timestamp, reverse=True)


@router.get("/{sensor_id}/latest", response_model=SensorReadingResponse)
async def get_latest_reading(sensor_id: str, db: Session = Depends(get_db)):
    """Get latest reading for a sensor."""
    repo = SensorReadingRepository(db)
    reading = repo.get_latest_by_sensor(sensor_id)
    
    if not reading:
        raise HTTPException(status_code=404, detail=f"No readings found for {sensor_id}")
    
    return reading


@router.get("/{sensor_id}/stats", response_model=SensorStatsResponse)
async def get_sensor_stats(
    sensor_id: str,
    hours: int = Query(24, ge=1, le=24*30),
    db: Session = Depends(get_db),
):
    """
    Get statistics for sensor readings.
    
    Query Parameters:
        - hours: Time window in hours (default: 24)
    """
    repo = SensorReadingRepository(db)
    stats = repo.get_statistics(sensor_id, hours=hours)
    
    return SensorStatsResponse(
        sensor_id=sensor_id,
        min_value=stats["min"],
        max_value=stats["max"],
        avg_value=stats["avg"],
        reading_count=stats["count"],
        time_window_hours=hours,
    )


@router.get("/by-location/{location}", response_model=List[SensorConfigResponse])
async def get_sensors_by_location(
    location: str,
    db: Session = Depends(get_db),
):
    """Get all sensors at a specific location."""
    repo = SensorConfigRepository(db)
    sensors = repo.get_by_location(location)
    
    if not sensors:
        raise HTTPException(
            status_code=404,
            detail=f"No sensors found at location '{location}'"
        )
    
    return sensors


@router.get("/by-type/{sensor_type}", response_model=List[SensorConfigResponse])
async def get_sensors_by_type(
    sensor_type: str,
    db: Session = Depends(get_db),
):
    """Get all sensors of a specific type."""
    repo = SensorConfigRepository(db)
    sensors = repo.get_by_type(sensor_type)
    
    if not sensors:
        raise HTTPException(
            status_code=404,
            detail=f"No sensors found of type '{sensor_type}'"
        )
    
    return sensors


@router.get("/by-group/{grupo}", response_model=List[SensorConfigResponse])
async def get_sensors_by_group(
    grupo: str,
    db: Session = Depends(get_db),
):
    """Get all sensors in a voting group."""
    repo = SensorConfigRepository(db)
    sensors = repo.get_by_group(grupo)
    
    if not sensors:
        raise HTTPException(
            status_code=404,
            detail=f"No sensors found in group '{grupo}'"
        )
    
    return sensors


@router.get("/by-module/{modulo}", response_model=List[SensorConfigResponse])
async def get_sensors_by_module(
    modulo: str,
    db: Session = Depends(get_db),
):
    """Get all sensors in a module."""
    repo = SensorConfigRepository(db)
    sensors = repo.get_by_module(modulo)
    
    if not sensors:
        raise HTTPException(
            status_code=404,
            detail=f"No sensors found in module '{modulo}'"
        )
    
    return sensors
