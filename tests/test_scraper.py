import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from scraper import scrape_profile_page, ProfileNotFoundException, ProfileIsPrivateException

@pytest.mark.asyncio
@patch('scraper.get_authenticated_page')
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
@patch('scraper.get_authenticated_page')
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