from abc import abstractmethod, ABC
from typing import Union, Any


class InterfaceIIIF3Storage(ABC):

    base_dir: str
    image_dir: str
    manifest_dir: str

    def __init__(self):
        pass

    @abstractmethod
    def create_image_file(self,
                          uuid_dir: str,
                          content: Union[str, bytes],
                          scale_dir='max',
                          *args,
                          **kwargs
                          ) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_image_info_file(self, uuid_dir: str, content: Union[str, bytes], *args, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_manifest_info_file(self, uuid_dir: str, content: Union[str, bytes], *args, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    def update_manifest_info_file(self, uuid_dir: str, content: Union[str, bytes], *args, **kwargs) -> Any:
        raise NotImplementedError