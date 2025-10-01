import os
from contextlib import asynccontextmanager
from playwright.async_api import Playwright, Page, Browser
from typing import AsyncIterator

class CookieFileNotFoundException(Exception):
    """로그인 쿠키 파일을 찾을 수 없을 때 발생하는 예외"""
    pass

@asynccontextmanager
async def get_authenticated_page(playwright: Playwright, cookie_file_path: str = 'instagram_cookies.json') -> AsyncIterator[Page]:
    """
    쿠키를 사용하여 인증된 Playwright 페이지 객체를 생성하는 컨텍스트 매니저.
    
    사용 예:
    async with async_playwright() as p:
        async with get_authenticated_page(p) as page:
            await page.goto(...)
            
    Args:
        playwright (Playwright): Playwright 인스턴스.
        cookie_file_path (str): 사용할 쿠키 파일의 경로.
        
    Yields
        Page: 인증된 페이지 객체.
        
    Raises:
        CookieFileNotFoundException: 쿠키 파일을 찾을 수 없을 때.
    """
    if not os.path.exists(cookie_file_path):
        raise CookieFileNotFoundException(
            f"로그인 쿠키 파일({cookie_file_path})을 찾을 수 없습니다. "
            "스크래퍼를 실행하기 전에 쿠키를 추출하여 프로젝트 루트에 저장해주세요."
        )
    
    browser: Browser = await playwright.chromium.launch(headless=True)
    try:
        context = await browser.new_context(storage_state=cookie_file_path)
        yield await context.new_page()
    finally:
        await browser.close()