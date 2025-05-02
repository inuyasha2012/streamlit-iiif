# repository/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic
from sqlalchemy.orm import Session
from streamlit import connections
from entity import Base

T = TypeVar('T', bound=Base)

class InterfaceRepository(ABC, Generic[T]):

    def __init__(self, connection: connections.SQLConnection):
        self.connection = connection
        
    @abstractmethod
    def delete_by_id(self, entity_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def list(self, filters: Dict[str, Any] = None) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: T, data: Dict[str, Any]) -> T:
        raise NotImplementedError