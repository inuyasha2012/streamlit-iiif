from utils.iiif import (IIIF3Image, IIIF3ImageTile, IIIF3ContentResource, IIIF3ContentResourceService, IIIF3Annotation,
                        gen_iiif3_full_max_0_default_jpg_image_url, create_manifest_builder, gen_iiif3_image_id)
import uuid

class TestIIIFModel:

    def setup_method(self):
        self.content_resource_id = "https://example.org/iiif/book1/page1/full/max/0/default.jpg"
        self.content_label = {"en": ["Page 1"]}
        self.content_service_image_id = "https://example.org/iiif/book1/page1"
        self.content_height = 2000
        self.content_width = 1500
        self.annotation_id = "https://example.org/iiif/book1/page1/annotation/p0001-image"

    def test_iiif3_image_info(self):
        image_uuid = uuid.uuid4().hex
        image_id = f'https://{IIIF_HOST}/images/{image_uuid}'
        width = 100
        height = 200

        test_image_info = {
            '@context': 'http://iiif.io/api/image/3/context.json',
            'id': image_id,
            'type': 'ImageService3',
            'protocol': 'http://iiif.io/api/image',
            'width': width,
            'height': height,
            'profile': [
                'level0'
            ],
            'tiles': [
                {"width": 512, "scaleFactors": [1]},
            ],
        }
        image_tiles = [IIIF3ImageTile(width=512, scaleFactors=[1])]
        image = IIIF3Image(
            id=gen_iiif3_image_id(IIIF_HOST, image_uuid),
            width=100,
            height=200,
            tiles=image_tiles,
        )
        assert image.model_dump(by_alias=True) == test_image_info


    def test_iiif3_content_resource(self):

        test_content_resource = {
            "id": self.content_resource_id,
            "type": "Image",
            "label": self.content_label,
            "format": "image/jpeg",
            "services": [
                {
                    "id": self.content_service_image_id,
                    "type": "ImageService3",
                    "profile": "level0",
                }
            ],
            "height": self.content_height,
            "width": self.content_width
        }
        content_resource_service = IIIF3ContentResourceService(
            id=self.content_service_image_id,
        )
        content_resource = IIIF3ContentResource(
            id=self.content_resource_id,
            label=self.content_label,
            service=[content_resource_service],
            height=self.content_height,
            width=self.content_width
        )

        assert content_resource.dict(by_alias=True) == test_content_resource


    def test_iiif3_annotation(self):
        test_annotation = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": "https://example.org/iiif/book1/page1/annotation/p0001-image",
            "type": "Annotation",
            "motivation": "painting",
            "body": {
                "id": "https://example.org/iiif/book1/page1/full/max/0/default.jpg",
                "type": "Image",
                "format": "image/jpeg",
                "services": [
                    {
                        "id": "https://example.org/iiif/book1/page1",
                        "type": "ImageService3",
                        "profile": "level0"
                    }
                ],
                "height": 2000,
                "width": 1500
            },
            "target": "https://example.org/iiif/book1/page1"
        }

        content_resource_service = IIIF3ContentResourceService(
            id=self.content_service_image_id,
        )
        content_resource = IIIF3ContentResource(
            id=self.content_resource_id,
            # label=self.content_label,
            service=[content_resource_service],
            height=self.content_height,
            width=self.content_width
        )



        annotation = IIIF3Annotation(
            id=self.annotation_id,
            body=content_resource,
            target="https://example.org/iiif/book1/page1"
        )

        assert annotation.dict(by_alias=True) == test_annotation


class TestIIIFBuild:

    def setup_method(self):
        self.image_list = []
        for i in range(10):
            uuid_val = uuid.uuid4().hex
            image_id = gen_iiif3_full_max_0_default_jpg_image_url('example.org', uuid_val)
            image_tiles = [IIIF3ImageTile(width=100, scaleFactors=[1])]
            image = IIIF3Image(id=image_id, width=100, height=200, tiles=image_tiles)
            self.image_list.append(image)

    def test_build_manifest(self):
        create_manifest_builder(
            'example.org',
            uuid.uuid4().hex,
            {"en": ["Book 1"]},
            self.image_list
        )