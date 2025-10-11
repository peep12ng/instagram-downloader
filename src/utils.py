import asyncio
import aiohttp
from typing import List, Tuple
import zipfile
import io

async def download_images_as_bytes(image_urls: List[str]) -> List[Tuple[str, bytes]]:
    """
    주어진 이미지 URL 목록에서 이미지들을 비동기적으로 다운로드하여,
    (파일명, 이미지 바이트) 형태의 튜플 리스트로 반환합니다.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [_fetch_image(session, url) for url in image_urls]
        results = await asyncio.gather(*tasks)
        # 다운로드에 실패한 경우(None)를 제외하고 반환
        return [res for res in results if res is not None]

async def _fetch_image(session: aiohttp.ClientSession, url: str) -> Tuple[str, bytes] | None:
    """
    단일 이미지 URL에서 이미지를 다운로드하고 (파일명, 바이트) 튜플로 반환합니다.
    실패 시 None을 반환합니다.
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                # URL의 마지막 부분을 파일명으로 사용
                filename = url.split('/')[-1].split('?')[0]
                image_bytes = await response.read()
                print(f"다운로드 성공: {filename}")
                return (filename, image_bytes)
            else:
                print(f"다운로드 실패 (상태 코드: {response.status}): {url}")
                return None
        
    except Exception as e:
        print(f"다운로드 중 오류 발생: {url}, 오류: {e}")
        return None
    
def create_zip_in_memory(image_data: List[Tuple[str, bytes]]) -> bytes:
    """
    (파일명, 이미지 바이트) 튜플 리스트를 받아 메모리 상에서 ZIP 파일을 생성하고,
    해당 ZIP 파일의 바이트를 반환합니다.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, data in image_data:
            zip_file.writestr(filename, data)
    
    # 버퍼의 시작으로 포인터를 이동
    zip_buffer.seek(0)
    return zip_buffer.getvalue()