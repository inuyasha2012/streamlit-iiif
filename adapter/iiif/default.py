from adapter.iiif.base import IIIFAdapterInterface


class DefaultIIIFAdapter(IIIFAdapterInterface):

    def __init__(self, base_url: str, manifest_dir: str, image_dir: str) -> None:
        self.base_url = base_url
        self.manifest_dir = manifest_dir


   