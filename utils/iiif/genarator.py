from typing import Dict, List

from utils.iiif.builders import (IIIF3ManifestBuilder, IIIF3CanvasBuilder, IIIF3AnnotationBuilder, IIIF3AnnotationPageBuilder,
                                 IIIF3ContentResourceBuilder,
                                 IIIF3ContentResourceServiceBuilder)
from utils.iiif.models import IIIF3Image
from utils.iiif.utils import gen_iiif3_manifest_url, gen_iiif3_default_jpg_from_image_id

def create_manifest_builder(
        manifest_base_url: str,
        manifest_dir: str,
        manifest_uuid: str,
        manifest_label: Dict[str, List[str]],
        images: List[IIIF3Image]
) -> IIIF3ManifestBuilder:

    manifest_url = gen_iiif3_manifest_url(manifest_base_url, manifest_dir, manifest_uuid)
    manifest_builder = IIIF3ManifestBuilder(
        id=f'{manifest_url}/manifest.json',
        label=manifest_label
    )

    canvases = []
    for idx, img in enumerate(images):

        service_builder = IIIF3ContentResourceServiceBuilder(
            id=img.id,
        )

        content_builder = IIIF3ContentResourceBuilder(
            id=gen_iiif3_default_jpg_from_image_id(img.id),
            height=img.height,
            width=img.width,
        )
        content_builder.set_service(service_builder.build())

        annotation_builder = IIIF3AnnotationBuilder(
            id=f"{manifest_url}/annotation/{idx + 1}",
            motivation="painting",
            target=f"{manifest_url}/canvas/{idx + 1}"
        )
        annotation_builder.set_body(content_builder.build())

        # 创建标注页
        annotation_page_builder = IIIF3AnnotationPageBuilder(
            id=f"{manifest_url}/page/{idx + 1}"
        )
        annotation_page_builder.set_item(
            annotation_builder.build()
        )

        # 创建画布
        canvas_builder = IIIF3CanvasBuilder(
            id=f"{manifest_url}/canvas/{idx + 1}",
            label={'en': [f"Canvas {idx + 1}"]},
            height=img.height,
            width=img.width
        )

        canvas_builder.add_item(annotation_page_builder.build())
        canvases.append(canvas_builder.build())

    # 添加画布到manifest
    manifest_builder.set_items(canvases)
    # 生成JSON
    return manifest_builder
