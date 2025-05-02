from functools import cached_property
from typing import Union, TypedDict
from github import Github
from github.Commit import Commit
from github.ContentFile import ContentFile
from storage.base import InterfaceIIIF3Storage


class GithubIIIF3Storage(InterfaceIIIF3Storage):

    def __init__(self, access_token: str, repo_name: str, image_dir: str, manifest_dir: str):
        super().__init__()
        self.access_token = access_token
        self.repo_name = repo_name
        self.base_dir = repo_name
        self.image_dir = image_dir
        self.manifest_dir = manifest_dir

    @cached_property
    def repo(self):
        g = Github(self.access_token)
        return g.get_user().get_repo(self.repo_name)

    def create_image_file(self, uuid_dir: str, content: Union[str, bytes], scale_dir='max', *args, **kwargs) -> dict[str, ContentFile | Commit]:
        path = f'{self.image_dir}/{uuid_dir}/full/{scale_dir}/0/default.jpg'
        message = kwargs.get('message', 'Add image file')
        return self._create_file(content, message, path)

    def _create_file(self, content: Union[str, bytes], message: str, path: str) -> dict[str, ContentFile | Commit]:
        return self.repo.create_file(
            path=path,
            message=message,
            content=content
        )


    def _update_file(self, content: Union[str, bytes], message: str, path: str) -> dict[str, ContentFile | Commit]:
        contents = self.repo.get_contents(path)
        return self.repo.update_file(
            path=path,
            message=message,
            content=content,
            sha=contents.sha
        )

    def create_image_info_file(self, uuid_dir: str, content: Union[str, bytes], *args, **kwargs) -> None:
        path = f'{self.image_dir}/{uuid_dir}/info.json'
        message = kwargs.get('message', 'Add image info file')
        self._create_file(content, message, path)


    def create_manifest_info_file(self, uuid_dir: str, content: Union[str, bytes], *args, **kwargs) -> dict[str, ContentFile | Commit]:
        path = f'{self.manifest_dir}/{uuid_dir}/manifest.json'
        message = kwargs.get('message', 'Add manifest info file')
        return self._create_file(content, message, path)


    def update_manifest_info_file(self, uuid_dir: str, content: Union[str, bytes], *args, **kwargs) -> dict[str, ContentFile | Commit]:
        path = f'{self.manifest_dir}/{uuid_dir}/manifest.json'
        print(path)
        message = kwargs.get('message', 'Update manifest info file')
        return self._update_file(content, message, path)