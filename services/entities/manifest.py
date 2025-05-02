import uuid
from typing import Dict, Any, List, Optional, Type
from entity import ManifestEntity
from services.common.base import InterfaceService


class ManifestService(InterfaceService):

    def create(self,
               manifest_url: str,
               public: bool = False,
               thumbnail_url: str | None = None,
               tag: str | None = None,
               meta_data: Dict[str, str] | None = None,
               ) -> ManifestEntity:
        data = {
            "thumbnail_url": thumbnail_url,
            "manifest_url": manifest_url,
            "tag": tag,
            "public": public,
            "meta_data": meta_data
        }
        return self.repository.create(data)

    def all(self) -> List[Type[ManifestEntity]]:
        return self.repository.list()

    def get_by_id(self, entity_id: int) -> Optional[ManifestEntity]:
        return self.repository.get_by_id(entity_id)

    def get_by_manifest_url(self, manifest_url: str) -> Optional[ManifestEntity]:
        try:
            filters = {'manifest_url': ("==", manifest_url)}
            return self.repository.list(filters=filters)[0]
        except IndexError:
            return None

    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[ManifestEntity]:
        entity = self.repository.get_by_id(entity_id)
        return self.repository.update(entity, data)

    def delete(self, entity_id: int) -> bool:
        return self.repository.delete_by_id(entity_id)

    PUBLIC_DT = {"Yes": True, "No": False}

    def filter_by_public(self) -> List[Type[ManifestEntity]]:
        filters = {'public': ("==", True)}
        return self.repository.list(filters)

    def filter(self,
               updated_at_start_date: str | None = None,
               updated_at_end_date: str | None = None,
               tag: str | None = None,
               public: List[str] | None = None
               ) -> List[Type[ManifestEntity]]:
        filters = {}
        if updated_at_start_date is not None:
            filters["updated_at"] = (">=", updated_at_start_date)
        if updated_at_end_date is not None:
            filters["updated_at"] = ("<=", updated_at_end_date)
        if tag:
            filters["tag"] = ("ilike", f"%{tag}%")
        if public:
            convert_public = [self.PUBLIC_DT[_] for _ in public]
            filters["public"] = ("in", convert_public)
        return self.repository.list(filters=filters)


    def update_manifest_info_file(self, uuid_dir: str, manifest_json: str):
        return self.storage.update_manifest_info_file(uuid_dir, manifest_json)
