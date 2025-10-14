import pytest
from unittest.mock import patch
from flask import Flask

from src.app import app
from src.scraper import ProfileNotFoundException, ProfileIsPrivateException, ScrapeTimeoutException

@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_get(client):
    """Test the index route for a successful Get request."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Instagram Feed Photo Downloader' in response.data

@pytest.mark.parametrize("username", [None, '', 'user name', 123])
def test_download_invalid_username(client, username):
    """Test the download route with invalid usernames."""
    response = client.post('/download', json={'username': username})
    assert response.status_code == 400
    assert response.json['error'] == '유효하지 않은 계정명입니다.'

@patch('src.app.scrape_profile_page')
def test_download_no_images_found(mock_scrape, client):
    """Test download when no images are found for a user."""
    mock_scrape.return_value = []

    response = client.post('/download', json={'username': 'testuser'})
    assert response.status_code == 404
    assert response.json['error'] == '다운로드할 이미지를 찾을 수 없습니다.'

@patch('src.app.scrape_profile_page')
def test_download_profile_not_found(mock_scrape, client):
    """Test download when the profile is not found."""
    mock_scrape.side_effect = ProfileNotFoundException()

    response = client.post('/download', json={'username': 'nonexistentuser'})
    assert response.status_code == 404
    assert response.json['error'] == "'nonexistentuser' 계정을 찾을 수 없습니다."

@patch('src.app.scrape_profile_page')
def test_download_profile_is_private(mock_scrape, client):
    """Test download when the profile is private."""
    mock_scrape.side_effect = ProfileIsPrivateException()

    response = client.post('/download', json={'username': 'privateuser'})
    assert response.status_code == 403
    assert response.json['error'] == "'privateuser' 계정은 비공개이거나 게시물이 없습니다."

@patch('src.app.scrape_profile_page')
def test_download_scrape_timeout(mock_scrape, client):
    """Test download when scraping times out."""
    mock_scrape.side_effect = ScrapeTimeoutException()

    response = client.post('/download', json={'username': 'timeoutuser'})
    assert response.status_code == 408
    assert response.json['error'] == '인스타그램에서 응답이 없어 시간 초과되었습니다. 잠시 후 다시 시도해주세요.'

@patch('src.app.create_zip_in_memory')
@patch('src.app.download_images_as_bytes')
@patch('src.app.scrape_profile_page')
def test_download_success(mock_scrape, mock_download, mock_zip, client):
    """Test the successful download and zipping of images."""
    # Setup mocks
    mock_scrape.return_value = ['http://example.com/img1.jpg']
    mock_download.return_value = [('img1.jpg', b'imagedata')]

    mock_zip.return_value = b'zipdata'

    # Make request
    response = client.post('/download', json={'username': 'testuser'})

    # Assertions
    assert response.status_code == 200
    assert response.mimetype == 'application/zip'
    assert response.headers['Content-Disposition'] == 'attachment;filename=testuser_instagram_photos.zip'
    assert response.data == b'zipdata'
    
@patch('src.app.scrape_profile_page')
def test_download_unknown_error(mock_scrape, client):
    """Test download when an unknown error occurs."""
    mock_scrape.side_effect = Exception("Unknown error")

    response = client.post('/download', json={'username': 'erroruser'})
    assert response.status_code == 500
    assert response.json['error'] == '알 수 없는 오류가 발생했습니다. 서버 로그를 확인하세요.'