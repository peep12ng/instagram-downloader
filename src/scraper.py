# 인스타그램 스크래핑을 위한 핵심 로직을 포함할 파일
import asyncio
import logging
from playwright.async_api import async_playwright, TimeoutError
from bs4 import BeautifulSoup
from typing import List
from .browser_manager import get_authenticated_page, CookieFileNotFoundException

logger = logging.getLogger(__name__)

# 사용자 정의 예외
class ProfileNotFoundException(Exception):
    """요청한 프로필을 찾을 수 없을 때 발생하는 예외"""
    pass

class ProfileIsPrivateException(Exception):
    """프로필이 비공개일 때 발생하는 예외"""
    pass

class ScrapeTimeoutException(Exception):
    """스크래핑 중 타임아웃이 발생했을 때의 예외"""
    pass

async def scrape_profile_page(username: str) -> List[str]:
    """
    주어진 인스타그램 계정 페이지로 이동하여 모든 게시물이 로드될 때까지 스크롤하고,
    모든 게시물 이미지의 URL을 추출하여 리스트로 반환합니다.
    """
    logger.info(f"'{username}' 계정 스크래핑 시작...")

    async with async_playwright() as p:
        async with get_authenticated_page(p) as page:
            # 인스타그램 프로필 페이지로 이동
            try:
                await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            
                # 계정 없음 오류 확인(더 안정적인 text selector 사용)
                not_found_locator = page.locator("text=/Sorry, this page isn't available/i")

                if await not_found_locator.is_visible():
                    raise ProfileNotFoundException(f"'{username}' 계정을 찾을 수 없습니다.")
                
                # 게시물 링크가 하나도 없는지 확인하여 비공개/게시물 없는 계정 감지
                # 공개 프로필에는 항상 '/p/'로 시작하는 게시물 링크(a 태그)가 존재
                # 잠시 기다려 페이지가 로드될 시간을 제공
                await page.wait_for_timeout(2000)
                post_locator = page.locator(f"a[href^='/{username}/p/']")

                # 게시물 요소가 하나도 없다면 비공개 계정으로 간주.
                if await post_locator.count() == 0:
                    raise ProfileIsPrivateException(f"'{username}' 계정은 비공개이거나 게시물이 없습니다.")
                
                logger.info("페이지 스크롤 시작...")
                # 페이지의 모든 게시물을 로드하기 위해 아래로 스크롤
                last_height = await page.evaluate("document.body.scrollHeight")
                while True:
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                    await page.wait_for_timeout(2000) # 새 콘텐츠가 로드될 때까지 대기
                    new_height = await page.evaluate("document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

                logger.info("페이지 스크롤 완료.")

                # 스크롤 후 최종 페이지 콘텐츠 다시 가져오기
                final_page_content = await page.content()

            except TimeoutError:
                raise ScrapeTimeoutException(f"'{username}' 계정을 스크래핑하는 중 타임아웃이 발생했습니다.")

            # BeautifulSoup을 사용하여 이미지 URL 파싱
            logger.info("이미지 URL 파싱 시작...")
            soup = BeautifulSoup(final_page_content, "lxml")
            img_tags = soup.find_all('img')

            image_urls = set()
            for img in img_tags:
                # 'src' 속성이 있고, CDN 주소 형식을 포함하는 경우만 추출(인스타그램 게시물-CDN 주소 형식 포함)
                if 'src' in img.attrs and 'scontent' in img['src']:
                    image_urls.add(img['src'])

            logger.info(f"총 {len(image_urls)}개의 고유한 이미지 URL을 찾았습니다.")
            return list(image_urls)

# 직접 실행하여 테스트 python scraper.py
if __name__ == '__main__':
    # 로깅 기본 설정(테스트 실행 시에만)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 테스트할 계정명(존재하지 않는 계정, 비공개 계정 등으로 변경하며 테스트)
    test_username = "xyzcuxvic"
    try:
        image_urls = asyncio.run(scrape_profile_page(test_username))
        logger.info(f"총 {len(image_urls)}개의 이미지를 성공적으로 스크랩했습니다.")
    except (ProfileNotFoundException, ProfileIsPrivateException, CookieFileNotFoundException) as e:
        logger.error(f"오류: {e}")