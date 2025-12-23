import os
import requests
from datetime import datetime
from typing import List, Dict
import time
import re

class NaverBlogCrawler:
    """네이버 블로그 검색 API를 사용하여 블로그 URL 수집"""
    
    def __init__(self):
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        self.base_url = "https://openapi.naver.com/v1/search/blog.json"
        
        if not self.client_id or not self.client_secret:
            raise ValueError("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 .env 파일에 설정해주세요.")
        
    def search(self, keyword: str, display: int = 100, start: int = 1) -> Dict:
        """
        네이버 블로그 검색
        
        Args:
            keyword: 검색 키워드
            display: 한 번에 가져올 결과 수 (최대 100)
            start: 검색 시작 위치 (1~1000)
        
        Returns:
            API 응답 결과
        """
        headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
        params = {
            'query': keyword,
            'display': display,
            'start': start,
            'sort': 'date'  # 날짜순 정렬 (최신순)
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 에러: {e}")
            return None
    
    def collect_by_keyword(self, keyword: str, max_results: int = 1000) -> List[Dict]:
        """
        키워드로 블로그 포스트 URL 수집
        
        Args:
            keyword: 검색 키워드
            max_results: 최대 수집 개수 (API 제한: 최대 1000)
        
        Returns:
            블로그 포스트 정보 리스트
        """
        all_posts = []
        display = 100  # 한 번에 100개씩
        max_results = min(max_results, 1000)  # API 제한
        
        print(f"\n{'='*60}")
        print(f"📝 네이버 블로그 API 수집 시작: '{keyword}'")
        print(f"{'='*60}")
        
        for start in range(1, max_results + 1, display):
            current_display = min(display, max_results - start + 1)
            print(f"📥 수집 중: {start}~{start + current_display - 1}번째...")
            
            result = self.search(keyword, current_display, start)
            if not result or 'items' not in result:
                print("⚠️ 더 이상 결과가 없습니다.")
                break
            
            items = result['items']
            if not items:
                print("⚠️ 검색 결과가 없습니다.")
                break
            
            for item in items:
                post_data = {
                    'platform': '네이버 블로그',
                    'region': '국내',
                    'keyword': keyword,
                    'title': self._clean_html(item['title']),
                    'description': self._clean_html(item['description']),
                    'blogger_name': item['bloggername'],
                    'blogger_id': item['bloggerlink'].split('/')[-1] if item['bloggerlink'] else '',
                    'post_url': item['link'],
                    'post_date': self._parse_date(item['postdate']),
                    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    # 상세 정보는 나중에 추가될 예정
                    'views': None,
                    'comments': None,
                    'likes': None
                }
                all_posts.append(post_data)
            
            # API 호출 제한 대응 (초당 10회 제한)
            time.sleep(0.15)
            
            # 더 이상 결과가 없으면 중단
            if len(items) < current_display:
                break
        
        print(f"✅ 네이버 블로그 수집 완료: 총 {len(all_posts)}개")
        return all_posts
    
    def _clean_html(self, text: str) -> str:
        """HTML 태그 및 특수문자 제거"""
        if not text:
            return ""
        # HTML 태그 제거
        text = re.sub('<[^<]+?>', '', text)
        # HTML 엔티티 변환
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        return text.strip()
    
    def _parse_date(self, date_str: str) -> str:
        """날짜 포맷 변환 (YYYYMMDD -> YYYY-MM-DD)"""
        try:
            if len(date_str) == 8:
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            return date_str
        except:
            return date_str
