from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from typing import Dict, List

class NaverBlogDetailCrawler:
    """Selenium을 사용하여 네이버 블로그 상세 정보 수집"""
    
    def __init__(self, headless: bool = True):
        """
        Args:
            headless: True면 브라우저 창 안 띄움 (서버/백그라운드 실행용)
        """
        self.headless = headless
        self.driver = None
        
    def init_driver(self):
        """Chrome WebDriver 초기화"""
        if self.driver is not None:
            return
        
        print("🌐 Chrome WebDriver 초기화 중...")
        
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # User-Agent 설정 (봇 감지 회피)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 로그 레벨 설정
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("✅ Chrome WebDriver 초기화 완료")
        except Exception as e:
            print(f"❌ WebDriver 초기화 실패: {e}")
            raise
    
    def close_driver(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("🔒 Chrome WebDriver 종료")
    
    def extract_blog_stats(self, url: str) -> Dict:
        """
        블로그 URL에서 조회수, 댓글, 좋아요 추출
        
        Args:
            url: 네이버 블로그 포스트 URL
        
        Returns:
            {
                'views': 조회수,
                'comments': 댓글수,
                'likes': 좋아요수,
                'success': 성공 여부,
                'error': 에러 메시지 (실패 시)
            }
        """
        result = {
            'views': 0,
            'comments': 0,
            'likes': 0,
            'success': False,
            'error': None
        }
        
        try:
            self.driver.get(url)
            time.sleep(2)  # 페이지 로딩 대기
            
            # iframe으로 전환 시도 (신규 블로그)
            try:
                iframe = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "mainFrame"))
                )
                self.driver.switch_to.frame(iframe)
                time.sleep(1)
            except:
                # iframe 없는 경우 (구 블로그 또는 다른 형식)
                pass
            
            # 조회수 추출
            result['views'] = self._extract_views()
            
            # 댓글 수 추출
            result['comments'] = self._extract_comments()
            
            # 좋아요 수 추출 (공감)
            result['likes'] = self._extract_likes()
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        finally:
            # iframe에서 나오기
            try:
                self.driver.switch_to.default_content()
            except:
                pass
        
        return result
    
    def _extract_views(self) -> int:
        """조회수 추출 - 다양한 패턴 시도"""
        try:
            # 패턴 1: <span class="se-f">조회 1,234</span>
            patterns = [
                (By.CLASS_NAME, "se_publishDate"),
                (By.CLASS_NAME, "se-f"),
                (By.CLASS_NAME, "se-module-text"),
                (By.CLASS_NAME, "blog2_series"),
            ]
            
            for by, value in patterns:
                try:
                    elements = self.driver.find_elements(by, value)
                    for elem in elements:
                        text = elem.text
                        if '조회' in text:
                            numbers = re.findall(r'[\d,]+', text)
                            if numbers:
                                return int(numbers[0].replace(',', ''))
                except:
                    continue
            
            # 패턴 2: 전체 페이지 텍스트에서 "조회" 패턴 찾기
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            views_match = re.search(r'조회\s*([\d,]+)', page_text)
            if views_match:
                return int(views_match.group(1).replace(',', ''))
            
        except Exception as e:
            pass
        
        return 0
    
    def _extract_comments(self) -> int:
        """댓글 수 추출"""
        try:
            # 패턴 1: 댓글 영역의 카운트 텍스트
            comment_selectors = [
                ".u_cbox_count",
                ".cmt_count",
                ".comment_count",
                ".num",
                ".u_cbox_info_txt"
            ]
            
            for selector in comment_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text
                        if '댓글' in text:
                            numbers = re.findall(r'[\d,]+', text)
                            if numbers:
                                return int(numbers[0].replace(',', ''))
                except:
                    continue
            
            # 패턴 2: 댓글 아이템 직접 카운트
            comment_items = self.driver.find_elements(By.CSS_SELECTOR, ".u_cbox_comment_box, .cmt_item")
            if comment_items:
                return len(comment_items)
            
            # 패턴 3: 전체 텍스트에서 추출
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            comments_match = re.search(r'댓글\s*([\d,]+)', page_text)
            if comments_match:
                return int(comments_match.group(1).replace(',', ''))
            
        except Exception as e:
            pass
        
        return 0
    
    def _extract_likes(self) -> int:
        """좋아요(공감) 수 추출"""
        try:
            # 패턴 1: 공감 버튼의 카운트
            like_selectors = [
                ".u_likeit_text",
                ".btn_sympathy .count",
                ".ico_like",
                ".u_likeit_list_count"
            ]
            
            for selector in like_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text
                        if text:
                            numbers = re.findall(r'[\d,]+', text)
                            if numbers:
                                return int(numbers[0].replace(',', ''))
                except:
                    continue
            
            # 패턴 2: 버튼 텍스트에서 추출
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                text = btn.text
                if '공감' in text or '좋아요' in text:
                    numbers = re.findall(r'[\d,]+', text)
                    if numbers:
                        return int(numbers[0].replace(',', ''))
            
            # 패턴 3: 전체 텍스트에서 추출
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            likes_match = re.search(r'공감\s*([\d,]+)', page_text)
            if likes_match:
                return int(likes_match.group(1).replace(',', ''))
            
        except Exception as e:
            pass
        
        return 0
    
    def batch_extract(self, posts: List[Dict], delay: float = 2.0) -> List[Dict]:
        """
        여러 블로그 포스트 일괄 상세 정보 수집
        
        Args:
            posts: 블로그 포스트 정보 리스트 (post_url 포함)
            delay: 각 요청 사이 대기 시간 (초)
        
        Returns:
            상세 정보가 추가된 포스트 리스트
        """
        total = len(posts)
        success_count = 0
        
        print(f"\n{'='*60}")
        print(f"🔍 네이버 블로그 상세 크롤링 시작")
        print(f"{'='*60}")
        print(f"📊 총 {total}개 포스트 크롤링 예정")
        print(f"⏱️  예상 소요 시간: 약 {int(total * (delay + 2) / 60)}분")
        print(f"{'='*60}\n")
        
        self.init_driver()
        
        for idx, post in enumerate(posts, 1):
            url = post['post_url']
            print(f"[{idx}/{total}] 크롤링 중: {post['title'][:30]}...")
            
            stats = self.extract_blog_stats(url)
            
            # 결과 업데이트
            post['views'] = stats['views']
            post['comments'] = stats['comments']
            post['likes'] = stats['likes']
            post['detail_crawled'] = stats['success']
            
            if stats['success']:
                success_count += 1
                print(f"  ✅ 조회: {stats['views']:,} | 댓글: {stats['comments']} | 좋아요: {stats['likes']}")
            else:
                print(f"  ⚠️  상세 정보 수집 실패: {stats['error']}")
            
            # 진행률 표시
            if idx % 10 == 0:
                progress = (idx / total) * 100
                print(f"\n📈 진행률: {progress:.1f}% ({idx}/{total}) | 성공: {success_count}/{idx}\n")
            
            # 다음 요청 전 대기
            if idx < total:
                time.sleep(delay)
        
        self.close_driver()
        
        print(f"\n{'='*60}")
        print(f"✅ 네이버 블로그 상세 크롤링 완료")
        print(f"{'='*60}")
        print(f"📊 전체: {total}개")
        print(f"✅ 성공: {success_count}개 ({success_count/total*100:.1f}%)")
        print(f"❌ 실패: {total - success_count}개 ({(total-success_count)/total*100:.1f}%)")
        print(f"{'='*60}\n")
        
        return posts
