from sqlalchemy.orm import Session

from models.admin_actinos_log import AdminActionLog


class AdminActionLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        admin_id: int,
        action: str,
        target_type: str,
        target_id: int | None = None,
        description: str | None = None,
    ):
        log = AdminActionLog(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description,
        )

        self.db.add(log)
        self.db.flush()

        return log

    def get_all(
        self,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(AdminActionLog)
            .order_by(AdminActionLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_admin_id(
        self,
        admin_id: int,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(AdminActionLog)
            .filter(
                AdminActionLog.admin_id == admin_id
            )
            .order_by(AdminActionLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_target(
        self,
        target_type: str,
        target_id: int,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(AdminActionLog)
            .filter(
                AdminActionLog.target_type == target_type,
                AdminActionLog.target_id == target_id,
            )
            .order_by(AdminActionLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )