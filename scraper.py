# 인스타그램 스크래핑을 위한 핵심 로직을 포함할 파일
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List

# 사용자 정의 예외
class ProfileNotFoundException(Exception):
    """요청한 프로필을 찾을 수 없을 때 발생하는 예외"""
    pass

class ProfileIsPrivateException(Exception):
    """프로필이 비공개일 때 발생하는 예외"""
    pass

async def scrape_profile_page(username: str) -> List[str]:
    """
    주어진 인스타그램 계정 페이지로 이동하여 모든 게시물이 로드될 때까지 스크롤하고,
    모든 게시물 이미지의 URL을 추출하여 리스트로 반환합니다.
    """
    print(f"'{username}' 계정 스크래핑 시작...")

    async with async_playwright() as p:
        # 1. headless=False로 변경하여 실제 브라우저 창을 띄웁니다.
        browser = await p.chromium.launch(headless=True) 
        try:
            page = await browser.new_page()

            # 인스타그램 프로필 페이지로 이동
            await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

            # 2. 여기서 코드를 일시정지하고 Playwright Inspector를 엽니다.
            print("\n>>> 디버깅 모드: Playwright Inspector가 실행됩니다. 브라우저와 Inspector 창을 확인하세요.")
            print(">>> Inspector에서 'Explore' 버튼으로 요소를 탐색하거나, 콘솔에서 locator를 테스트할 수 있습니다.")
            print(">>> 계속 진행하려면 Inspector에서 'Resume' 버튼(▶)을 누르세요.\n")
            # await page.pause()

            # 계정 없음 오류 확인 (더 안정적인 text selector 사용)
            not_found_locator = page.locator("text=/Sorry, this page isn't available/i")
            if await not_found_locator.is_visible():
                raise ProfileNotFoundException(f"'{username}' 계정을 찾을 수 없습니다.")
            
            # 비공개 계정 오류 확인 (태그에 의존하지 않고 텍스트 내용으로만 확인하여 안정성 향상)
            private_locator = page.locator("text=/This Account is Private|비공개 계정입니다/i")
            if await private_locator.is_visible():
                raise ProfileIsPrivateException(f"'{username}' 계정은 비공개입니다.")
    
            print("페이지 스크롤 시작...")
            # 페이지의 모든 게시물을 로드하기 위해 아래로 스크롤
            last_height = await page.evaluate("document.body.scrollHeight")
            while True:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                await page.wait_for_timeout(2000) # 새 콘텐츠가 로드될 때까지 대기
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            print("페이지 스크롤 완료.")

            # 스크롤 후 최종 페이지 콘텐츠 다시 가져오기
            final_page_content = await page.content()

            # BeautifulSoup을 사용하여 이미지 URL 파싱
            print("이미지 URL 파싱 시작...")
            soup = BeautifulSoup(final_page_content, "lxml")
            img_tags = soup.find_all('img')

            image_urls = set()
            for img in img_tags:
                # 'src' 속성이 있고, CDN 주소 형식을 포함하는 경우만 추출(인스타그램 게시물-CDN 주소 형식 포함)
                if 'src' in img.attrs and 'scontent' in img['src']:
                    image_urls.add(img['src'])
            
            print(f"총 {len(image_urls)}개의 고유한 이미지 URL을 찾았습니다.")
            return list(image_urls)
        finally:
            await browser.close() # 성공하든 실패하던 항상 브라우저를 닫습니다.

# 직접 실행하여 테스트 python scraper.py
if __name__ == '__main__':
    # 테스트할 계정명(존재하지 않는 계정, 비공개 계정 등으로 변경하며 테스트)
    test_username = "xyzcuxvic"
    try:
        image_urls = asyncio.run(scrape_profile_page(test_username))
        print(f"총 {len(image_urls)}개의 이미지를 성공적으로 스크랩했습니다.")
    except (ProfileNotFoundException, ProfileIsPrivateException) as e:
        print(f"오류: {e}")