import os
from typing import Union, NamedTuple
from storage.base import InterfaceIIIF3Storage




class LocalIIIF3Storage(InterfaceIIIF3Storage):

    def update_manifest_info_file(self, uuid_dir: str, content: Union[str, bytes], *args, **kwargs) -> None:
        return self.create_manifest_info_file(uuid_dir, content)

    def __init__(self, base_dir: str, image_dir: str, manifest_dir: str):
        super().__init__()
        self.base_dir = base_dir
        self.image_dir = image_dir
        self.manifest_dir = manifest_dir


    def create_image_file(self, uuid_dir: str, content: Union[str, bytes], scale_dir='max', *args, **kwargs) -> None:
        dir_path = os.path.join(
            self.base_dir,
            self.image_dir,
            uuid_dir,
            'full',
            scale_dir,
            '0',
        )
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path, 'default.jpg')
        with open(path, 'wb') as f:
            f.write(content)

    def create_image_info_file(self, uuid_dir: str, content: Union[str, bytes], *args, **kwargs) -> None:
        dir_path = os.path.join(
            self.base_dir,
            self.image_dir,
            uuid_dir,
        )
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path, 'info.json')
        with open(path, 'w') as f:
            f.write(content)

    def create_manifest_info_file(self, uuid_dir: str, content: Union[str, bytes], *args, **kwargs) -> None:
        dir_path = os.path.join(
            self.base_dir,
            self.manifest_dir,
            uuid_dir,
        )
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path, 'manifest.json')
        with open(path, 'w') as f:
            f.write(content)