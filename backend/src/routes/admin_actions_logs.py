from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from dto.admin_actions_log import AdminActionLogResponse
from services.admin_actions_log_service import AdminActionLogService


router = APIRouter(
    prefix="/admin/logs",
    tags=["Admin Logs"],
)


@router.get(
    "",
    response_model=list[AdminActionLogResponse],
)
def get_all_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    admin_action_log_service = AdminActionLogService(db)

    return admin_action_log_service.get_all_logs(
        current_user=current_user,
        page=page,
        limit=limit,
    )


@router.get(
    "/{target_type}/{target_id}",
    response_model=list[AdminActionLogResponse],
)
def get_logs_by_target(
    target_type: str,
    target_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    admin_action_log_service = AdminActionLogService(db)

    return admin_action_log_service.get_logs_by_target(
        current_user=current_user,
        target_type=target_type,
        target_id=target_id,
        page=page,
        limit=limit,
    )