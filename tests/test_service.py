import pytest
from unittest.mock import MagicMock
from services.entities.image import ImageService
from entity import ImageEntity

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_storage():
    return MagicMock()

@pytest.fixture
def image_service(mock_session, mock_storage):
    service = ImageService(db_session=mock_session, storage=mock_storage, base_url="http://example.com")
    return service

def test_create_image(image_service, mock_session):
    # Mock the uploaded image
    mock_uploaded_image = MagicMock()
    mock_uploaded_image.getvalue.return_value = b'fake_image_content'

    # Mock the storage
    image_service.storage.create_image_file.return_value = None
    image_service.storage.create_image_info_file.return_value = None

    # Call the method to test
    result = image_service.create(mock_uploaded_image, scale_factors=[1])

    # Assertions
    assert isinstance(result, ImageEntity)
    mock_session.add.assert_called_once_with(result)
    mock_session.commit.assert_called_once()

def test_get_all_images(image_service, mock_session):
    # Mock the query result
    mock_query = mock_session.query.return_value
    mock_query.all.return_value = [ImageEntity(), ImageEntity()]

    # Call the method to test
    result = image_service.all()

    # Assertions
    assert len(result) == 2
    mock_session.query.assert_called_once_with(ImageEntity)
    mock_query.all.assert_called_once()