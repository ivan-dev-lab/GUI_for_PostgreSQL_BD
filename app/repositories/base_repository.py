from __future__ import annotations

from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, session: Session, model):
        self.session = session
        self.model = model

    def get(self, entity_id: int):
        return self.session.get(self.model, entity_id)

    def add(self, entity):
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, entity) -> None:
        self.session.delete(entity)
