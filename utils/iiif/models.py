from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Union


class IIIFBaseModel(BaseModel):
    class Config:
        populate_by_name = True
        exclude_none = True


class IIIF3ImageTile(IIIFBaseModel):
    width: int
    scaleFactors: List[int]


class IIIF3Image(IIIFBaseModel):
    width: Optional[int]
    height: Optional[int]
    context: Literal['http://iiif.io/api/image/3/context.json'] = Field(
        default='http://iiif.io/api/image/3/context.json', alias='@context'
    )
    id: str
    type: Literal['ImageService3'] = 'ImageService3'
    protocol: Optional[Literal['http://iiif.io/api/image']] = 'http://iiif.io/api/image'
    profile: Optional[List[Literal['level0', 'level1', 'level2']]]
    tiles: List[IIIF3ImageTile]


class IIIF3ContentResourceService(IIIFBaseModel):
    id: str
    type: Literal['ImageService3'] = 'ImageService3'
    profile: Literal['level0', 'level1', 'level2'] = 'level0'


class IIIF3ContentResource(IIIFBaseModel):
    id: str
    type: str = "Image"
    format: str = "image/jpeg"
    service: List[IIIF3ContentResourceService]
    height: int
    width: int


class IIIF3AnnotationTag(IIIFBaseModel):
    type: str = "TextualBody"
    value: str
    format: str = "text/plain"
    language: str = "en"

class IIIF3Annotation(IIIFBaseModel):
    context: Literal["http://iiif.io/api/presentation/3/context.json"] = Field('http://iiif.io/api/presentation/3/context.json', alias='@context')
    id: str
    type: Literal['Annotation'] = "Annotation"
    motivation: str = "painting"
    body: Union[IIIF3ContentResource, IIIF3AnnotationTag]
    target: str


class IIIF3AnnotationPage(IIIFBaseModel):
    context: Literal["http://iiif.io/api/presentation/3/context.json"] = Field('http://iiif.io/api/presentation/3/context.json', alias='@context')
    id: str
    type: Literal['AnnotationPage'] = "AnnotationPage"
    items: List[IIIF3Annotation]


class IIIF3Canvas(IIIFBaseModel):
    id: str
    type: Literal['Canvas'] = 'Canvas'
    label: Dict[str, List[str]]
    height: Optional[int]
    width: Optional[int]
    items: List[IIIF3AnnotationPage]
    annotations: Optional[List[IIIF3AnnotationPage]] = None


class IIIF3ManifestSummary(IIIFBaseModel):
    pass


class IIIF3ManifestThumbnail(IIIFBaseModel):
    id: str
    type: Literal['Image'] = 'Image'
    format: Literal['image/jpeg'] = 'image/jpeg'


class IIIF3ManifestProvider(IIIFBaseModel):
    id: str
    type: Literal['Agent'] = 'Agent'
    label: Dict[str, List[str]]


class IIIF3ManifestStructure(IIIFBaseModel):
    pass


class IIIF3ManifestAnnotation(IIIFBaseModel):
    pass


class IIIF3ManifestAtom(IIIFBaseModel):
    type: str
    label: Dict[str, List[str]]


class IIIF3Manifest(IIIFBaseModel):
    context: Literal['http://iiif.io/api/presentation/3/context.json'] = Field('http://iiif.io/api/presentation/3/context.json', alias='@context')
    id: str
    type: Literal['Manifest'] = "Manifest"
    label: Dict[str, List[str]]
    items: List[IIIF3Canvas]
    structures: Optional[List[IIIF3ManifestStructure]] = None
    annotations: Optional[List[IIIF3ManifestAnnotation]] =None
    thumbnail: Optional[List[IIIF3ManifestThumbnail]] = None
    provider: Optional[List[IIIF3ManifestProvider]] = None
    metadata: Optional[List[IIIF3ManifestAtom]] = None
    summary: Optional[Dict[str, List[str]]] = None