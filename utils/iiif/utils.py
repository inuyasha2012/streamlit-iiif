def gen_iiif3_full_max_0_default_jpg_image_url(base_url: str, image_dir: str, image_uuid: str) -> str:
    return f'{base_url}/{image_dir}/{image_uuid}/full/max/0/default.jpg'

def gen_iiif3_full_size_0_default_jpg_image_url(base_url: str, image_dir: str, size_dir:str, image_uuid: str) -> str:
    return f'{base_url}/{image_dir}/{image_uuid}/full/{size_dir}/0/default.jpg'


def gen_iiif3_image_id(base_url: str, image_dir: str, image_uuid: str) -> str:
    return f'{base_url}/{image_dir}/{image_uuid}'

def gen_iiif3_default_jpg_from_image_id(image_id:str) -> str:
    return f'{image_id}/full/max/0/default.jpg'


def gen_iiif3_image_info(base_url: str, image_dir: str, image_uuid: str) -> str:
    return f'{base_url}/{image_dir}/{image_uuid}/info.json'


def gen_iiif3_manifest_url(base_url: str, manifest_dir: str, manifest_uuid: str) -> str:
    return f'{base_url}/{manifest_dir}/{manifest_uuid}'

def gen_iiif3_manifest_json_url(base_url: str, manifest_dir: str, manifest_uuid: str) -> str:
    return f'{base_url}/{manifest_dir}/{manifest_uuid}/manifest.json'