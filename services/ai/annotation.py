from typing import List, Dict, Any
import requests
from utils.tools import ImageAnnoTool


class AnnotationService:
    def __init__(self, anno_tool: ImageAnnoTool):
        self.image_anno_tool = anno_tool

    def get_manifest_images(self, manifest_url: str) -> List[str]:
        """Get list of image URLs from a manifest"""
        self.image_anno_tool.set_manifest(manifest_url)
        return self.image_anno_tool.get_manifest_images()

    def process_manifest_annotations(self, manifest_url: str) -> Dict[str, Any]:
        """Process annotations for a manifest and save results"""
        self.image_anno_tool.set_manifest(manifest_url)
        images_urls = self.image_anno_tool.get_manifest_images()

        results = []
        for idx, image_url in enumerate(images_urls):
            anno_data = self.image_anno_tool.generate_anno_data_from_image(image_url)
            self.image_anno_tool.set_anno4manifest(anno_data, idx)
            results.append({
                "image_url": image_url,
                "annotation_data": anno_data
            })

        # Get updated manifest
        manifest_json = self.image_anno_tool.manifest.model_dump_json(by_alias=True, exclude_none=True)
        uuid = self.image_anno_tool.manifest.id.split('/')[-2]

        return {
            "results": results,
            "manifest_json": manifest_json,
            "uuid": uuid
        }