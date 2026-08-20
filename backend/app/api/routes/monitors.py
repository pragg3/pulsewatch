from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.monitor import Monitor
from backend.app.schemas.monitor import MonitorCreate, MonitorResponse

router = APIRouter(
    prefix="/monitors",
    tags=["monitors"],
)


@router.post(
    "",
    response_model=MonitorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_monitor(
    monitor_data: MonitorCreate,
    db: Annotated[Session, Depends(get_db)],
):
    url = str(monitor_data.url)

    existing_monitor = db.scalar(select(Monitor).where(Monitor.url == url))

    if existing_monitor:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A monitor with this URL already exists",
        )

    monitor = Monitor(
        name=monitor_data.name,
        url=url,
    )

    db.add(monitor)
    db.commit()
    db.refresh(monitor)

    return monitor


@router.get("", response_model=list[MonitorResponse])
def list_monitors(
    db: Annotated[Session, Depends(get_db)],
):
    statement = select(Monitor).order_by(Monitor.id)

    return db.scalars(statement).all()
