# repository/image_repository.py
from typing import List, Dict, Any, Optional, Type
from entity import ImageEntity
from repositories.common.base import InterfaceRepository


class ImageRepository(InterfaceRepository[ImageEntity]):

    def get_by_id(self, entity_id: int) -> Optional[ImageEntity]:
        with self.connection.session as session:
            return session.query(ImageEntity).filter(ImageEntity.id == entity_id).first()

    def delete_by_id(self, entity_id: int) -> bool:
        with self.connection.session as session:
            entity = self.get_by_id(entity_id)
            if entity:
                session.delete(entity)
                session.commit()
                return True
            return False

    def create(self, data: Dict[str, Any]) -> ImageEntity:
        with self.connection.session as session:
            session = self.connection.session
            image_entity = ImageEntity(**data)
            session.add(image_entity)
            session.commit()
            session.refresh(image_entity)
        return image_entity

    def update(self, entity: ImageEntity, data: Dict[str, Any]) -> ImageEntity:
        with self.connection.session as session:
            for key, value in data.items():
                setattr(entity, key, value)
            session.add(entity)
            session.commit()
            session.refresh(entity)
        return entity

    def list(self, filters: Dict[str, Any] = None) -> List[Type[ImageEntity]]:
        with self.connection.session as session:
            query = session.query(ImageEntity)
            if filters:
                for key, value in filters.items():
                    operator, val = value
                    attr = getattr(ImageEntity, key)
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