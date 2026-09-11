from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User, UserRole
from repositories.admin_actions_log_repository import AdminActionLogRepository


class AdminActionLogService:
    def __init__(self, db: Session):
        self.admin_action_log_repository = AdminActionLogRepository(db)

    def log_action(
        self,
        admin_id: int,
        action: str,
        target_type: str,
        target_id: int | None = None,
        description: str | None = None,
    ):
        return self.admin_action_log_repository.create(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description,
        )

    def get_all_logs(
        self,
        current_user: User,
        page: int = 1,
        limit: int = 10,
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this resource",
            )

        offset = (page - 1) * limit

        return self.admin_action_log_repository.get_all(
            offset=offset,
            limit=limit,
        )

    def get_logs_by_target(
        self,
        current_user: User,
        target_type: str,
        target_id: int,
        page: int = 1,
        limit: int = 10,
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this resource",
            )

        offset = (page - 1) * limit

        return self.admin_action_log_repository.get_by_target(
            target_type=target_type,
            target_id=target_id,
            offset=offset,
            limit=limit,
        )