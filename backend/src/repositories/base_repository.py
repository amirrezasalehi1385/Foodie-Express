from sqlalchemy import select
from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model

    def get_by_id(self, id: int):
        return self.db.get(self.model, id)

    def get_all(self):
        stmt = select(self.model)
        return self.db.scalars(stmt).all()

    def create(self, entity):
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)

        return entity

    def update(self, entity, data: dict):
        for field, value in data.items():
            setattr(entity, field, value)

        self.db.flush()
        self.db.refresh(entity)

        return entity

    def delete(self, entity) -> None:
        self.db.delete(entity)
        self.db.flush()