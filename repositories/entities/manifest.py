from typing import List, Dict, Any, Optional, Type
from entity import ManifestEntity
from repositories.common.base import InterfaceRepository


class ManifestRepository(InterfaceRepository[ManifestEntity]):
    """
    Repository for managing IIIF 3.0 manifests.
    """

    def get_by_id(self, entity_id: int) -> Optional[ManifestEntity]:
        with self.connection.session as session:
            return session.query(ManifestEntity).filter(ManifestEntity.id == entity_id).first()

    def delete_by_id(self, entity_id: int) -> bool:
        with self.connection.session as session:
            entity = self.get_by_id(entity_id)
            if entity:
                session.delete(entity)
                session.commit()
                return True
            return False

    def create(self, data: Dict[str, Any]) -> ManifestEntity:
        with self.connection.session as session:
            manifest_entity = ManifestEntity(**data)
            session.add(manifest_entity)
            session.commit()
            session.refresh(manifest_entity)
            return manifest_entity

    def update(self, entity: ManifestEntity, data: Dict[str, Any]) -> ManifestEntity:
        with self.connection.session as session:
            for key, value in data.items():
                setattr(entity, key, value)
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity

    def list(self, filters: Dict[str, Any] = None) -> List[Type[ManifestEntity]]:
        with self.connection.session as session:
            query = session.query(ManifestEntity)
            if filters:
                for key, value in filters.items():
                    operator, val = value
                    attr = getattr(ManifestEntity, key)
                    if operator == "==":
                        query = query.filter(attr == val)
                    elif operator == ">=":
                        query = query.filter(attr >= val)
                    elif operator == "<=":
                        query = query.filter(attr <= val)
                    elif operator == ">":
                        query = query.filter(attr > val)
                    elif operator == "<":
                        query = query.filter(attr < val)
                    elif operator == "!=":
                        query = query.filter(attr != val)
                    elif operator == "like":
                        query = query.filter(attr.like(val))
                    elif operator == "ilike":
                        query = query.filter(attr.ilike(val))
                    elif operator == "in":
                        query = query.filter(attr.in_(val))
            return query.all()