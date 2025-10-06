import pytest
import zipfile
import io
from unittest.mock import patch, MagicMock, AsyncMock

from utils import download_images_as_bytes, create_zip_in_memory

@pytest.mark.asyncio
@patch('utils.aiohttp.ClientSession')
async def test_download_images_as_bytes_success(mock_ClientSession):
    """
    이미지 다운로드가 성공하는 경우를 테스트합니다.
    실제 네트워크 요청 대신 aiohttp.ClientSession을 모킹(mocking)합니다.
    """
    # 가짜 이미지 데이터와 URL 설정
    fake_image_bytes = b'fake_image_data'
    image_urls = ["http://fake.com/image1.jpg"]

    # aiohttp.ClientSession()이 반환할 인스턴스 모의 객체
    mock_sesion_instance = mock_ClientSession.return_value
    # 이 인스턴스가 async with 구문을 지원하도록 __aenter__ 설정
    mock_sesion_instance.__aenter__.return_value = mock_sesion_instance

    # session.get()이 반환할 응답 모의 객체
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.read.return_value = fake_image_bytes
    # session.get() 또한 async with 구문을 지원해야 함
    mock_sesion_instance.get.return_value.__aenter__.return_value = mock_response

    # 함수 실행
    results = await download_images_as_bytes(image_urls)

    # 결과 검증
    assert len(results) == 1
    filename, data = results[0]
    assert filename == "image1.jpg"
    assert data == fake_image_bytes

@pytest.mark.asyncio
@patch('utils.aiohttp.ClientSession')
async def test_download_images_as_bytes_error(mock_ClientSession):
    """
    이미지 다운로드 시 서버가 404 오류를 반환하는 경우를 테스트합니다.
    """
    image_urls = ["http://fake.com/not_found.jpg"]

    mock_session_instance = mock_ClientSession.return_value
    mock_session_instance.__aenter__.return_value = mock_session_instance

    mock_response = AsyncMock()
    mock_response.status = 404 # <-- 404 오류 시뮬레이션
    mock_session_instance.get.return_value.__aenter__.return_value = mock_response

    # 함수 실행
    results = await download_images_as_bytes(image_urls)

    # 결과 검증: 오류가 발생한 경우, 결과 리스트는 비어 있어야 함
    assert len(results) == 0

def test_create_zip_in_memory_success():
    """
    메모리 내 ZIP 파일 생성이 성공하는 경우를 테스트합니다.
    """
    # 가짜 이미지 데이터 리스트 생성
    image_data = [
        ("image1.jpg", b"dummy_data_1"),
        ("image2.png", b"dummy_data_2"),
    ]

    # 함수 실행
    zip_bytes = create_zip_in_memory(image_data)

    # 결과 검증
    assert isinstance(zip_bytes, bytes)

    # 생성된 ZIP 파일의 내용을 직접 읽어서 확인
    zip_buffer = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        # 파일 목록 확인
        assert set(zip_file.namelist()) == {"image1.jpg", "image2.png"}
        # 개별 파일 내용 확인
        assert zip_file.read("image1.jpg") == b"dummy_data_1"
        assert zip_file.read("image2.png") == b"dummy_data_2"

def test_create_zip_in_memory_with_empty_list():
    """
    비어있는 이미지 목록으로 ZIP 파일 생성을 시도하는 엣지 케이스를 테스트합니다.
    """
    # 함수 실행
    zip_bytes = create_zip_in_memory([])
    
    # 결과 검증
    assert isinstance(zip_bytes, bytes)

    # 생성된 ZIP 파일이 유효한지, 그리고 비어있는지 확인
    zip_buffer = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        assert zip_file.namelist() == []