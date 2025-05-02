from functools import cached_property
from typing import Dict, Any, List

import requests


class ManifestParser:

    def __init__(self, manifest_url: str):
        self.manifest_url = manifest_url

    @cached_property
    def manifest_dict(self) -> Dict[str, Any]:
        """Parse a IIIF manifest from a URL and return its contents"""
        manifest_url = self.manifest_url
        response = requests.get(manifest_url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def format_manifest_for_llm(manifest_info: Dict[str, Any]) -> str:
        """Format manifest information for LLM consumption"""
        manifest_text = f"Manifest ID: {manifest_info.get('id', '')}\n"
        manifest_text += f"Type: {manifest_info.get('type', '')}\n"

        # Add labels
        manifest_text += "Labels:\n"
        for lang, text in manifest_info.get("label", {}).items():
            manifest_text += f"  - {lang}: {text}\n"

        # Add summary if available
        if manifest_info.get("summary"):
            manifest_text += "Summary:\n"
            for lang, text in manifest_info.get("summary", {}).items():
                manifest_text += f"  - {lang}: {text}\n"

        # Add metadata
        manifest_text += "Metadata:\n"
        for key, value_dict in manifest_info.get("metadata", {}).items():
            manifest_text += f"  - {key}:\n"
            for lang, text in value_dict.items():
                manifest_text += f"    - {lang}: {text}\n"

        # Add items summary (limited to first 5 for brevity)
        manifest_text += f"Items (Canvases): {len(manifest_info.get('items', []))}\n"
        for i, item in enumerate(manifest_info.get("items", [])):
            manifest_text += f"  Item {i + 1}:\n"
            manifest_text += f"    ID: {item.get('id', '')}\n"
            manifest_text += f"    Type: {item.get('type', '')}\n"
            for lang, text in item.get('label', {}).items():
                manifest_text += f"    Label - {lang}: {text}\n"
            manifest_text += f"    Images: 1\n"

        return manifest_text

    def extract_manifest_info(self) -> Dict[str, Any]:
        """Extract key information from the manifest entities"""
        manifest_data = self.manifest_dict
        info = {
            "id": manifest_data.get("id", ""),
            "type": manifest_data.get("type", ""),
            "label": self._extract_language_map(manifest_data.get("label", {})),
            "summary": self._extract_language_map(manifest_data.get("summary", {})),
            "metadata": self._extract_metadata(manifest_data.get("metadata", [])),
            "items": self._extract_items(manifest_data.get("items", [])),
            "images": self._extract_images_(manifest_data.get("items", [])),
        }
        return info

    @staticmethod
    def _extract_language_map(language_map: Dict[str, List[str]]) -> Dict[str, str]:
        """Extract text from IIIF language maps"""
        result = {}
        for lang, values in language_map.items():
            if values and isinstance(values, list):
                result[lang] = " ".join(values)
        return result

    def _extract_metadata(self, metadata_list: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
        """Extract metadata from IIIF manifest"""
        result = {}
        for item in metadata_list:
            if "label" in item and "value" in item:
                label = self._extract_language_map(item["label"])
                value = self._extract_language_map(item["value"])
                key = label.get("en", next(iter(label.values())) if label else "Unknown")
                result[key] = value
        return result

    def _extract_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract information about items (canvases) in the manifest"""
        result = []
        for item in items:
            item_info = {
                "id": item.get("id", ""),
                "type": item.get("type", ""),
                "label": self._extract_language_map(item.get("label", {})),
                "images": self._extract_images(items),
            }
            result.append(item_info)
        return result

    @staticmethod
    def _extract_images(items: List[Dict[str, Any]]) -> List[str]:
        """Extract image URLs from annotation pages"""
        image_urls = []
        for item in items:
            if item.get("type") == "AnnotationPage":
                for annotation in item.get("items", []):
                    if "body" in annotation and annotation["body"].get("type") == "Image":
                        if "id" in annotation["body"]:
                            image_urls.append(annotation["body"]["id"])
        return image_urls


    @staticmethod
    def _extract_images_(items: List[Dict[str, Any]]) -> List[str]:
        image_urls = []
        for item in items:
            for each_item in item['items']:
                for annotation in each_item.get("items", []):
                    if "body" in annotation and annotation["body"].get("type") == "Image":
                        if "id" in annotation["body"]:
                            image_urls.append(annotation["body"]["id"])
        return image_urls