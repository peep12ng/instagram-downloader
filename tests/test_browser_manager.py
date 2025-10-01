import pytest
from playwright.async_api import async_playwright
from browser_manager import get_authenticated_page, CookieFileNotFoundException

@pytest.mark.asyncio
async def test_get_authenticated_page_raises_error_if_cookie_file_not_found(tmp_path):
    """
    쿠키 파일이 존재하지 않을 때 CookieFileNotFoundException을 발생시키는지 테스트합니다.
    """
    # 존재하지 않는 파일 경로 생성
    non_existent_cookie_file = tmp_path / "non_existent_cookie.json"

    async with async_playwright() as p:
        # pytest.raises 블록은 지정된 예외가 발생했는지 확인합니다.
        # 이 블록이 성공적으로 통과하면, 올바른 타입의 예외가 발생한 것입니다.
        with pytest.raises(CookieFileNotFoundException):
            async with get_authenticated_page(p, cookie_file_path=str(non_existent_cookie_file)):
                pass # 이 코드는 실행되지 않아야 함

@pytest.mark.asyncio
async def test_get_authenticated_page_with_valid_cookie_succeeds(tmp_path):
    """
    유효한 (더미) 쿠키 파일이 있을 때 정상적으로 페이지 객체를 생성하는지 테스트합니다.
    """
    dummy_cookie_file = tmp_path / "dummy_cookie.json"
    dummy_cookie_file.write_text("[]") # Playwright가 인식할 수 있는 빈 JSON 배열

    async with async_playwright() as p:
        async with get_authenticated_page(p, cookie_file_path=str(dummy_cookie_file)) as page:
            assert page is not None
            assert "chromium" in page.context.browser.browser_type.name