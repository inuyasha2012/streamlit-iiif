import uuid
from typing import Tuple, Dict, Any, List, Optional, Type
from helper import convert_image
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.iiif import (IIIF3Image, IIIF3ImageTile, gen_iiif3_image_id,
                        gen_iiif3_image_info, create_manifest_builder, IIIF3ManifestThumbnail)
from entity import ImageEntity, ManifestEntity
from utils.iiif import gen_iiif3_full_size_0_default_jpg_image_url, gen_iiif3_manifest_json_url
from services.common.base import InterfaceService



class ImageService(InterfaceService):

    def upload(self, image: UploadedFile, scale_factors: List[int] = None) -> Tuple[str, str]:
        """Upload an image and return thumbnail and info URLs"""
        image_uuid = uuid.uuid4().hex
        convert_images, height, width = convert_image(image, scale_factors)
        min_scale_dir = None
        for idx, (scale_dir, image) in enumerate(convert_images.items()):
            self.storage.create_image_file(
                uuid_dir=f'{image_uuid}',
                scale_dir=scale_dir,
                content=image.getvalue()
            )
            if idx == len(convert_images) - 1:
                min_scale_dir = scale_dir

        self.storage.create_image_info_file(
            uuid_dir=image_uuid,
            content=IIIF3Image(
                tiles=[IIIF3ImageTile(width=width, scaleFactors=scale_factors)],
                id=gen_iiif3_image_id(self.base_url, self.storage.image_dir, image_uuid),
                width=width,
                height=height,
                profile=['level0']
            ).model_dump_json(by_alias=True, exclude_none=True)
        )

        return (
            gen_iiif3_full_size_0_default_jpg_image_url(self.base_url, self.storage.image_dir, min_scale_dir, image_uuid),
            gen_iiif3_image_info(self.base_url, self.storage.image_dir, image_uuid),
        )

    def create(self, uploaded_image: UploadedFile, scale_factors: List[int] = None) -> ImageEntity:
        thumbnail_url, info_url = self.upload(uploaded_image, scale_factors=scale_factors)
        image_entity = self.repository.create({'thumbnail_url': thumbnail_url, 'info_url': info_url})
        return image_entity

    def all(self) -> List[Type[ImageEntity]]:
        return self.repository.list()

    def get_by_id(self, entity_id: int) -> Optional[ImageEntity]:
        return self.repository.get_by_id(entity_id)

    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[ImageEntity]:
        entity = self.repository.get_by_id(entity_id)
        return self.repository.update(entity, data)

    def delete(self, entity_id: int) -> bool:
        return self.repository.delete_by_id(entity_id)

    USED_DT = {"Yes": True, "No": False}

    def filter(self,
               updated_at_start_date: str | None = None,
               updated_at_end_date: str | None = None,
               used: List[str] | None = None,
               tag: str | None = None
               ) -> List[Type[ImageEntity]]:

        filters = {}

        if updated_at_start_date is not None:
            filters["updated_at"] = (">=", updated_at_start_date)
        if updated_at_end_date is not None:
            filters["updated_at"] = ("<=", updated_at_end_date)

        if used:
            convert_used = [self.USED_DT[_] for _ in used]
            filters["used"] = ("in", convert_used)

        if tag:
            filters["tag"] = ("ilike", f"%{tag}%")

        return self.repository.list(filters)


    def create_manifest_by_image_info_list(self,
                                           iiif_image_list: List[IIIF3Image],
                                           tag: Optional[str] = None,
                                           thumbnail_url: Optional[str] = None
                                           ) -> ManifestEntity:
        manifest_uuid = uuid.uuid4().hex
        label = tag
        manifest_builder = create_manifest_builder(
            manifest_base_url=self.base_url,
            manifest_uuid=manifest_uuid,
            manifest_label={'en': [label]},
            images=iiif_image_list,
            manifest_dir=self.storage.manifest_dir
        )
        thumbnail = IIIF3ManifestThumbnail(
            id=thumbnail_url
        )
        manifest_builder.set_thumbnail(thumbnail)
        self.storage.create_manifest_info_file(
            uuid_dir=manifest_uuid,
            content=manifest_builder.build_json()
        )
        with self.repository.connection.session as session:
            manifest_url = gen_iiif3_manifest_json_url(self.base_url, self.storage.manifest_dir, manifest_uuid)
            manifest_obj = ManifestEntity(
                thumbnail_url=thumbnail_url,
                manifest_url=manifest_url,
                tag=tag,
            )
            session.add(manifest_obj)
            session.commit()
            session.refresh(manifest_obj)
        return manifest_obj