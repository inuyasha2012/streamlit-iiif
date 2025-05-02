import pytest
from unittest.mock import patch, MagicMock
from storage.github import GithubIIIF3Storage, GithubStorageConfig

@pytest.fixture
def mock_github():
    with patch('storage.github.Github') as MockGithub:
        yield MockGithub

def test_create_image_file(mock_github):
    # Mock the Github instance and its methods
    mock_repo = MagicMock()
    mock_github.return_value.get_user.return_value.get_repo.return_value = mock_repo

    # Create a GithubIIIF3Storage instance with mock config
    config = GithubStorageConfig(
        access_token='fake_token',
        repo_name='fake_repo',
        image_dir='images',
        manifest_dir='manifests',
        base_url='https://example.com'
    )
    storage = GithubIIIF3Storage(config)

    # Mock the create_file method
    mock_repo.create_file.return_value = {'content': 'fake_content', 'commit': 'fake_commit'}

    # Call the method to test
    result = storage.create_image_file('uuid_dir', b'fake_content')

    # Assertions
    mock_repo.create_file.assert_called_once_with(
        path='images/uuid_dir/full/max/0/default.jpg',
        message='Add image file',
        content=b'fake_content'
    )
    assert result == {'content': 'fake_content', 'commit': 'fake_commit'}

def test_update_manifest_info_file(mock_github):
    # Mock the Github instance and its methods
    mock_repo = MagicMock()
    mock_github.return_value.get_user.return_value.get_repo.return_value = mock_repo

    # Create a GithubIIIF3Storage instance with mock config
    config = GithubStorageConfig(
        access_token='fake_token',
        repo_name='fake_repo',
        image_dir='images',
        manifest_dir='manifests',
        base_url='https://example.com'
    )
    storage = GithubIIIF3Storage(config)

    # Mock the get_contents and update_file methods
    mock_contents = MagicMock()
    mock_contents.sha = 'fake_sha'
    mock_repo.get_contents.return_value = mock_contents
    mock_repo.update_file.return_value = {'content': 'fake_content', 'commit': 'fake_commit'}

    result = storage.update_manifest_info_file('uuid_dir', b'fake_content')

    mock_repo.get_contents.assert_called_once_with('manifests/uuid_dir/manifest.json')
    mock_repo.update_file.assert_called_once_with(
        path='manifests/uuid_dir/manifest.json',
        message='Update manifest info file',
        content=b'fake_content',
        sha='fake_sha'
    )
    assert result == {'content': 'fake_content', 'commit': 'fake_commit'}