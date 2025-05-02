from typing import Dict, List, Any, Union
from abc import ABC, abstractmethod

class IIIFAdapterInterface(ABC):

    @abstractmethod
    def generate_image_id(self, **kwargs: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_image_info_url(self, **kwargs: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_full_size_image_url(self, **kwargs: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_manifest_json_url(self, base_url: str, manifest_dir: str, manifest_uuid: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_image_info(self, tiles: List[Dict], id: str, width: int, height: int) -> Union[Dict, str]:
        raise NotImplementedError

    @abstractmethod
    def create_image_tile(self, width: int, scale_factors: List[int]) -> Dict:
        raise NotImplementedError

    @abstractmethod
    def create_manifest_builder(self, manifest_base_url: str, manifest_uuid: str,
                               manifest_label: Dict, images: List[Any], manifest_dir: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_manifest_thumbnail(self, id: str) -> Dict:
        raise NotImplementedError