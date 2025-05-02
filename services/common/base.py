# services/base.py
from abc import abstractmethod, ABC
from typing import Optional, Any, List, Dict
from storage import InterfaceIIIF3Storage
from repositories.common import InterfaceRepository

class InterfaceService(ABC):
    def __init__(self, repository: InterfaceRepository, storage: InterfaceIIIF3Storage, base_url: str):
        self.repository = repository
        self.storage = storage
        self.base_url = base_url

    @abstractmethod
    def create(self, *args, **kwargs) -> Any:
        """Create entity in database"""
        raise NotImplementedError

    @abstractmethod
    def all(self) -> List[Any]:
        """Get all entities"""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Any]:
        """Get entity by ID"""
        raise NotImplementedError

    @abstractmethod
    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[Any]:
        """Update entity"""
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete entity"""
        raise NotImplementedError

    @abstractmethod
    def filter(self, *args, **kwargs) -> List[Any]:
        raise NotImplementedError