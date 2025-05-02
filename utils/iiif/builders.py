from typing import List, Dict

from utils.iiif.models import (IIIF3ContentResourceService, IIIF3Annotation, IIIF3ContentResource, IIIF3Manifest,
                               IIIF3Canvas, IIIF3ManifestThumbnail, IIIF3ManifestProvider, IIIF3AnnotationPage)



class IIIF3ManifestBuilder:

    def __init__(self, id: str, label: Dict[str, List[str]]) -> None:
        self.id = id
        self.label = label
        self.items = []
        self.thumbnail = None
        self.provider = None

    def set_items(self, items: List[IIIF3Canvas]) -> None:
        self.items = items

    def add_item(self, item: IIIF3Canvas):
        self.items.append(item)

    def set_thumbnail(self, thumbnail: IIIF3ManifestThumbnail):
        self.thumbnail = [thumbnail]

    def set_provider(self, provider: IIIF3ManifestProvider):
        self.provider = [provider]

    def build(self) -> IIIF3Manifest:
        return IIIF3Manifest(
            id=self.id,
            label=self.label,
            items=self.items,
            thumbnail=self.thumbnail
        )

    def build_json(self) -> str:
        return self.build().model_dump_json(by_alias=True, exclude_none=True)


class IIIF3CanvasBuilder:
    def __init__(self,
                 id: str,
                 label: Dict[str, List[str]],
                 height: int = None,
                 width: int = None
                 ):
        self.id = id
        self.label = label
        self.height = height
        self.width = width
        self.items = []


    def set_items(self, items: List[IIIF3AnnotationPage]):
        self.items = items

    def add_item(self, item: IIIF3AnnotationPage):
        self.items = [item]

    def build(self) -> IIIF3Canvas:
        return IIIF3Canvas(
            id=self.id,
            label=self.label,
            height=self.height,
            width=self.width,
            items=self.items
        )

    def build_json(self) -> str:
        return self.build().model_dump_json(by_alias=True, exclude_none=True)


class IIIF3AnnotationPageBuilder:

    def __init__(self, id: str):
        self.id = id
        self.items = []

    def set_item(self, item: IIIF3Annotation):
        self.items = [item]

    def build(self) -> IIIF3AnnotationPage:
        return IIIF3AnnotationPage(
            id=self.id,
            items=self.items
        )

    def build_json(self) -> str:
        return self.build().model_dump_json(by_alias=True, exclude_none=True)


class IIIF3AnnotationBuilder:

    def __init__(self, id: str, motivation: str, target: str):
        self.id = id
        self.motivation = motivation
        self.target = target
        self.body = None

    def set_body(self, body: IIIF3ContentResource):
        self.body = body

    def build(self) -> IIIF3Annotation:
        return IIIF3Annotation(
            id=self.id,
            motivation=self.motivation,
            body=self.body,
            target=self.target
        )

    def build_json(self) -> str:
        return self.build().model_dump_json(by_alias=True, exclude_none=True)


class IIIF3ContentResourceBuilder:

    def __init__(self, id: str, height: int=None, width: int=None):
        self.id = id
        self.service = None
        self.height = height
        self.width = width

    def set_service(self, service: IIIF3ContentResourceService) -> None:
        self.service = [service]

    def build(self) -> IIIF3ContentResource:
        return IIIF3ContentResource(
            id=self.id,
            service=self.service,
            height=self.height,
            width=self.width
        )

    def build_json(self) -> str:
        return self.build().model_dump_json(by_alias=True, exclude_none=True)


class IIIF3ContentResourceServiceBuilder:

    def __init__(self, id: str) -> None:
        self.id = id

    def build(self) -> IIIF3ContentResourceService:
        return IIIF3ContentResourceService(
            id=self.id
        )

    def build_json(self) -> str:
        return self.build().model_dump_json(by_alias=True, exclude_none=True)
