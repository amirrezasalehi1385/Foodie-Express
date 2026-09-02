from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model

    def get_by_id(self, id: int):
        return self.db.get(self.model, id)

    def create(self, entity):
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)

        return entity

    def delete(self, entity) -> None:
        self.db.delete(entity)
        self.db.flush()