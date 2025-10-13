import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from playwright.async_api import TimeoutError
from src.scraper import (
    scrape_profile_page,
    ProfileNotFoundException,
    ProfileIsPrivateException,
    ScrapeTimeoutException,
)

@pytest.mark.asyncio
@patch('src.scraper.get_authenticated_page')
async def test_scrape_profile_page_success(mock_get_authenticated_page):
    """
    정상적인 프로필 페이지에서 스크래핑이 성공하는 경우를 테스트합니다.
    """
    # --- Arrange (준비) ---
    username = "test_user"
    # 가짜 HTML 페이지 내용
    mock_html_content = """
    <html><body>
        <a href="/test_user/p/C123"></a>
        <img src="https://scontent.cdn.instagram.com/image1.jpg">
        <img src="https://scontent.cdn.instagram.com/image2.jpg">
        <img src="/some/other/image.png">
    </body></html>
    """

    # Playwright의 page 객체와 그 안의 함수들을 가짜(Mock)로 만듭니다.
    mock_not_found_locator = AsyncMock()
    mock_not_found_locator.is_visible.return_value = False
    mock_post_locator = AsyncMock()
    mock_post_locator.count.return_value = 1

    mock_page = AsyncMock()
    mock_page.locator = MagicMock(side_effect=[mock_not_found_locator, mock_post_locator])
    mock_page.evaluate.side_effect = [1000, None, 1000] # 스크롤이 끝까지 내려간 것처럼 시뮬레이션
    mock_page.content.return_value = mock_html_content

    mock_get_authenticated_page.return_value.__aenter__.return_value = mock_page

    # --- Act (실행) ---
    image_urls = await scrape_profile_page(username)

    # --- Assert (검증) ---
    assert len(image_urls) == 2
    assert "https://scontent.cdn.instagram.com/image1.jpg" in image_urls
    assert "https://scontent.cdn.instagram.com/image2.jpg" in image_urls


@pytest.mark.asyncio
@patch('src.scraper.get_authenticated_page')
async def test_scrape_profile_page_not_found(mock_get_authenticated_page):
    """
    '계정 없음' 페이지를 만났을 때 ProfileNotFoundException을 발생시키는지 테스트합니다.
    """
    # Locator 모의 객체 설정 (is_visible은 비동기 메서드)
    mock_not_found_locator = AsyncMock()
    mock_not_found_locator.is_visible = AsyncMock(return_value=True)

    # Page 모의 객체 설정
    mock_page = AsyncMock()
    # page.locator는 동기 메서드이므로 MagicMock으로 덮어써서 Locator 모의 객체를 반환하게 함
    mock_page.locator = MagicMock(return_value=mock_not_found_locator)
    
    # get_authenticated_page의 컨텍스트 매니저가 Page 모의 객체를 반환하도록 설정
    mock_get_authenticated_page.return_value.__aenter__.return_value = mock_page
    
    with pytest.raises(ProfileNotFoundException, match="'not_a_real_user' 계정을 찾을 수 없습니다."):
        await scrape_profile_page("not_a_real_user")

@pytest.mark.asyncio
@patch('src.scraper.get_authenticated_page')
async def test_scrape_profile_page_is_private(mock_get_authenticated_page):
    """
    비공개 계정 페이지를 만났을 때 ProfileIsPrivateException을 발생시키는지 테스트합니다.
    """
    # Page 모의 객체 설정
    mock_page = AsyncMock()

    # '계정 없음' 로케이터는 보이지 않음
    mock_not_found_locator = AsyncMock()
    mock_not_found_locator.is_visible = AsyncMock(return_value=False)

    # '게시물' 로케이터는 0개의 요소를 가짐
    mock_post_locator = AsyncMock()
    mock_post_locator.count = AsyncMock(return_value=0)

    # page.locator는 동기 메서드이며, 호출 순서에 따라 다른 값을 반환해야 함
    mock_page.locator = MagicMock(side_effect=[mock_not_found_locator, mock_post_locator])

    # get_authenticated_page의 컨텍스트 매니저가 Page 모의 객체를 반환하도록 설정
    mock_get_authenticated_page.return_value.__aenter__.return_value = mock_page

    with pytest.raises(ProfileIsPrivateException, match="'private_user' 계정은 비공개이거나 게시물이 없습니다."):
        await scrape_profile_page("private_user")

@pytest.mark.asyncio
@patch('src.scraper.get_authenticated_page')
async def test_scrape_profile_page_timeout(mock_get_authenticated_page):
    """
    스크래핑 중 TimeoutError가 발생했을 때 ScrapeTimeoutException을 발생시키는지 테스트합니다.
    """
    # --- Arrange (준비) ---
    # page.goto가 TimeoutError를 발생시키도록 설정
    def raise_timeout(*args, **kwargs):
        raise TimeoutError("Page load timed out")
    mock_page = AsyncMock()
    mock_page.goto.side_effect = raise_timeout

    # get_authenticated_page의 컨텍스트 매니저가 이 mock_page를 반환하도록 설정
    mock_get_authenticated_page.return_value.__aenter__.return_value = mock_page

    # --- Act & Assert (실행 및 검증) ---
    # ScrapeTimeoutException이 발생하는지 확인
    with pytest.raises(ScrapeTimeoutException, match="'timeout_user' 계정을 스크래핑하는 중 타임아웃이 발생했습니다."):
        await scrape_profile_page("timeout_user")
    