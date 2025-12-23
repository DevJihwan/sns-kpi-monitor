from ntscraper import Nitter
import time
from datetime import datetime
from typing import List, Dict
import re

class TwitterCrawler:
    """ntscraper를 사용하여 트위터(X) 데이터 수집"""
    
    def __init__(self):
        try:
            self.scraper = Nitter(log_level=1, skip_instance_check=False)
        except Exception as e:
            print(f"⚠️ ntscraper 초기화 실패: {e}")
            self.scraper = None
    
    def search(self, keyword: str, max_tweets: int = 100) -> List[Dict]:
        """
        트위터 검색
        
        Args:
            keyword: 검색 키워드 (해시태그는 #포함)
            max_tweets: 최대 트윗 수
        
        Returns:
            트윗 리스트
        """
        if not self.scraper:
            print("❌ ntscraper가 초기화되지 않았습니다.")
            return []
        
        try:
            tweets = self.scraper.get_tweets(keyword, mode='term', number=max_tweets)
            return tweets.get('tweets', [])
        except Exception as e:
            print(f"❌ 트위터 검색 실패: {e}")
            return []
    
    def collect_by_keyword(self, keyword: str, max_results: int = 500) -> List[Dict]:
        """
        키워드로 트윗 수집
        
        Args:
            keyword: 검색 키워드
            max_results: 최대 수집 개수
        
        Returns:
            트윗 정보 리스트
        """
        print(f"\n{'='*60}")
        print(f"🐦 Twitter 수집 시작: '{keyword}'")
        print(f"{'='*60}")
        
        # 해시태그 형식으로 변환
        search_term = keyword if keyword.startswith('#') else f"#{keyword}"
        
        print(f"🔍 검색어: {search_term}")
        raw_tweets = self.search(search_term, max_results)
        
        if not raw_tweets:
            print("⚠️ 트윗을 찾을 수 없습니다.")
            return []
        
        all_tweets = []
        for tweet in raw_tweets:
            # 국내/해외 구분 (한글 포함 여부로 판단)
            text = tweet.get('text', '')
            region = '국내' if self._contains_korean(text) else '해외'
            
            tweet_data = {
                'platform': 'Twitter(X)',
                'region': region,
                'keyword': keyword,
                'channel_name': tweet.get('user', {}).get('name', ''),
                'channel_id': tweet.get('user', {}).get('username', ''),
                'tweet_id': tweet.get('link', '').split('/')[-1] if tweet.get('link') else '',
                'text': text,
                'post_url': tweet.get('link', ''),
                'post_date': self._parse_date(tweet.get('date', '')),
                'views': tweet.get('stats', {}).get('views', 0),
                'likes': tweet.get('stats', {}).get('likes', 0),
                'comments': tweet.get('stats', {}).get('replies', 0),
                'retweets': tweet.get('stats', {}).get('retweets', 0),
                'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            all_tweets.append(tweet_data)
        
        print(f"✅ Twitter 수집 완료: 총 {len(all_tweets)}개")
        print(f"   └ 국내: {sum(1 for t in all_tweets if t['region'] == '국내')}개")
        print(f"   └ 해외: {sum(1 for t in all_tweets if t['region'] == '해외')}개")
        
        return all_tweets
    
    def _contains_korean(self, text: str) -> bool:
        """텍스트에 한글이 포함되어 있는지 확인"""
        if not text:
            return False
        korean_pattern = re.compile('[ㄱ-ㅎㅏ-ㅣ가-힣]')
        return bool(korean_pattern.search(text))
    
    def _parse_date(self, date_str: str) -> str:
        """날짜 포맷 정리"""
        try:
            # ISO 형식에서 날짜만 추출 (2024-12-23T10:30:00+00:00 -> 2024-12-23)
            if 'T' in date_str:
                return date_str.split('T')[0]
            return date_str
        except:
            return datetime.now().strftime('%Y-%m-%d')
    
    def get_user_profile(self, username: str) -> Dict:
        """사용자 프로필 정보 가져오기 (참고용)"""
        if not self.scraper:
            return {}
        
        try:
            profile = self.scraper.get_profile_info(username)
            return profile
        except Exception as e:
            print(f"❌ 프로필 가져오기 실패 ({username}): {e}")
            return {}
