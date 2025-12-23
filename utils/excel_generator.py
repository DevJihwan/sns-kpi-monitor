import pandas as pd
from datetime import datetime
from typing import List, Dict
import os

class ExcelGenerator:
    """SNS KPI 데이터를 Excel 파일로 생성"""
    
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, naver_data: List[Dict], twitter_data: List[Dict], 
                       keywords: List[str]) -> str:
        """
        통합 KPI 리포트 생성
        
        Args:
            naver_data: 네이버 블로그 데이터
            twitter_data: 트위터 데이터
            keywords: 수집한 키워드 리스트
        
        Returns:
            생성된 Excel 파일 경로
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'SNS_KPI_Report_{timestamp}.xlsx'
        filepath = os.path.join(self.output_dir, filename)
        
        print(f"\n{'='*60}")
        print(f"📊 Excel 리포트 생성 중...")
        print(f"{'='*60}")
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # 1. 전체 요약 시트
            print("📄 '전체 요약' 시트 생성 중...")
            self._create_summary_sheet(writer, naver_data, twitter_data, keywords)
            
            # 2. 통합 데이터 시트 (모든 SNS 합침)
            print("📄 '통합 데이터' 시트 생성 중...")
            self._create_integrated_sheet(writer, naver_data, twitter_data)
            
            # 3. 네이버 블로그 시트
            if naver_data:
                print("📄 '네이버 블로그' 시트 생성 중...")
                self._create_naver_sheet(writer, naver_data)
            
            # 4. 트위터 시트
            if twitter_data:
                print("📄 'Twitter' 시트 생성 중...")
                self._create_twitter_sheet(writer, twitter_data)
            
            # 5. 해시태그 분석 시트
            print("📄 '해시태그 분석' 시트 생성 중...")
            self._create_hashtag_analysis_sheet(writer, naver_data, twitter_data, keywords)
            
            # 6. 일별 트렌드 시트
            print("📄 '일별 트렌드' 시트 생성 중...")
            self._create_daily_trends_sheet(writer, naver_data, twitter_data)
        
        print(f"{'='*60}")
        print(f"✅ Excel 리포트 생성 완료!")
        print(f"📁 파일 위치: {filepath}")
        print(f"{'='*60}\n")
        
        return filepath
    
    def _create_summary_sheet(self, writer, naver_data, twitter_data, keywords):
        """전체 요약 시트"""
        # 플랫폼별 요약
        summary_data = {
            '플랫폼': ['네이버 블로그', 'Twitter(X)', '전체'],
            '총 게시물 수': [
                len(naver_data),
                len(twitter_data),
                len(naver_data) + len(twitter_data)
            ],
            '국내 게시물': [
                sum(1 for d in naver_data if d.get('region') == '국내'),
                sum(1 for d in twitter_data if d.get('region') == '국내'),
                sum(1 for d in naver_data if d.get('region') == '국내') + 
                sum(1 for d in twitter_data if d.get('region') == '국내')
            ],
            '해외 게시물': [
                sum(1 for d in naver_data if d.get('region') == '해외'),
                sum(1 for d in twitter_data if d.get('region') == '해외'),
                sum(1 for d in naver_data if d.get('region') == '해외') + 
                sum(1 for d in twitter_data if d.get('region') == '해외')
            ],
            '수집 키워드 수': [len(keywords)] * 3,
            '수집 완료 시간': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 3
        }
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='전체 요약', index=False)
        
        # 키워드별 게시물 수
        keyword_summary = []
        for keyword in keywords:
            naver_count = len([d for d in naver_data if d.get('keyword') == keyword])
            twitter_count = len([d for d in twitter_data if d.get('keyword') == keyword])
            
            keyword_summary.append({
                '키워드': keyword,
                '네이버 블로그': naver_count,
                'Twitter': twitter_count,
                '합계': naver_count + twitter_count
            })
        
        df_keywords = pd.DataFrame(keyword_summary)
        
        # 기존 시트에 추가 (빈 줄 2개 후)
        startrow = len(df_summary) + 3
        df_keywords.to_excel(writer, sheet_name='전체 요약', 
                            startrow=startrow, index=False)
    
    def _create_integrated_sheet(self, writer, naver_data, twitter_data):
        """통합 데이터 시트 - 고객 요구사항에 맞춘 포맷"""
        integrated = []
        
        # 네이버 블로그 데이터 추가
        for item in naver_data:
            integrated.append({
                '국내/해외': item.get('region', '국내'),
                '플랫폼': '네이버 블로그',
                '채널명(ID)': item.get('blogger_name', ''),
                '원문 링크': item.get('post_url', ''),
                '조회수': item.get('views', 0) if item.get('views') is not None else '수집불가',
                '좋아요 수': item.get('likes', 0) if item.get('likes') is not None else '수집불가',
                '댓글 수': item.get('comments', 0) if item.get('comments') is not None else '수집불가',
                '키워드': item.get('keyword', ''),
                '제목': item.get('title', ''),
                '작성일': item.get('post_date', ''),
                '수집일시': item.get('collected_at', '')
            })
        
        # 트위터 데이터 추가
        for item in twitter_data:
            integrated.append({
                '국내/해외': item.get('region', '미분류'),
                '플랫폼': 'Twitter(X)',
                '채널명(ID)': f"@{item.get('channel_id', '')}",
                '원문 링크': item.get('post_url', ''),
                '조회수': item.get('views', 0),
                '좋아요 수': item.get('likes', 0),
                '댓글 수': item.get('comments', 0),
                '키워드': item.get('keyword', ''),
                '제목': item.get('text', '')[:100] + '...' if len(item.get('text', '')) > 100 else item.get('text', ''),
                '작성일': item.get('post_date', ''),
                '수집일시': item.get('collected_at', '')
            })
        
        df = pd.DataFrame(integrated)
        
        # 날짜순 정렬 (최신순)
        if not df.empty and '작성일' in df.columns:
            df = df.sort_values('작성일', ascending=False)
        
        df.to_excel(writer, sheet_name='통합 데이터', index=False)
    
    def _create_naver_sheet(self, writer, naver_data):
        """네이버 블로그 상세 시트"""
        naver_formatted = []
        
        for item in naver_data:
            naver_formatted.append({
                '국내/해외': item.get('region', '국내'),
                '블로거명': item.get('blogger_name', ''),
                '블로그 ID': item.get('blogger_id', ''),
                '원문 링크': item.get('post_url', ''),
                '제목': item.get('title', ''),
                '내용 미리보기': item.get('description', ''),
                '조회수': item.get('views', 0) if item.get('views') is not None else '수집불가',
                '좋아요 수': item.get('likes', 0) if item.get('likes') is not None else '수집불가',
                '댓글 수': item.get('comments', 0) if item.get('comments') is not None else '수집불가',
                '키워드': item.get('keyword', ''),
                '작성일': item.get('post_date', ''),
                '수집일시': item.get('collected_at', ''),
                '상세크롤링': '성공' if item.get('detail_crawled') else '실패'
            })
        
        df = pd.DataFrame(naver_formatted)
        
        # 날짜순 정렬
        if not df.empty and '작성일' in df.columns:
            df = df.sort_values('작성일', ascending=False)
        
        df.to_excel(writer, sheet_name='네이버 블로그', index=False)
    
    def _create_twitter_sheet(self, writer, twitter_data):
        """트위터 상세 시트"""
        twitter_formatted = []
        
        for item in twitter_data:
            twitter_formatted.append({
                '국내/해외': item.get('region', '미분류'),
                '사용자명': item.get('channel_name', ''),
                '사용자 ID': f"@{item.get('channel_id', '')}",
                '원문 링크': item.get('post_url', ''),
                '트윗 내용': item.get('text', ''),
                '조회수': item.get('views', 0),
                '좋아요 수': item.get('likes', 0),
                '댓글 수': item.get('comments', 0),
                '리트윗 수': item.get('retweets', 0),
                '키워드': item.get('keyword', ''),
                '작성일': item.get('post_date', ''),
                '수집일시': item.get('collected_at', '')
            })
        
        df = pd.DataFrame(twitter_formatted)
        
        # 날짜순 정렬
        if not df.empty and '작성일' in df.columns:
            df = df.sort_values('작성일', ascending=False)
        
        df.to_excel(writer, sheet_name='Twitter', index=False)
    
    def _create_hashtag_analysis_sheet(self, writer, naver_data, twitter_data, keywords):
        """해시태그별 분석 시트"""
        analysis = []
        
        for keyword in keywords:
            naver_posts = [d for d in naver_data if d.get('keyword') == keyword]
            twitter_posts = [d for d in twitter_data if d.get('keyword') == keyword]
            
            # 트위터 참여 지표
            total_views = sum([t.get('views', 0) for t in twitter_posts])
            total_likes = sum([t.get('likes', 0) for t in twitter_posts])
            total_comments = sum([t.get('comments', 0) for t in twitter_posts])
            total_retweets = sum([t.get('retweets', 0) for t in twitter_posts])
            
            # 네이버 참여 지표 (수집된 것만)
            naver_views = [n.get('views', 0) for n in naver_posts if n.get('views') is not None and n.get('views') > 0]
            naver_likes = [n.get('likes', 0) for n in naver_posts if n.get('likes') is not None and n.get('likes') > 0]
            naver_comments = [n.get('comments', 0) for n in naver_posts if n.get('comments') is not None and n.get('comments') > 0]
            
            analysis.append({
                '키워드': keyword,
                '네이버 게시물 수': len(naver_posts),
                '트위터 게시물 수': len(twitter_posts),
                '총 게시물 수': len(naver_posts) + len(twitter_posts),
                '트위터 총 조회수': total_views,
                '트위터 총 좋아요': total_likes,
                '트위터 총 댓글': total_comments,
                '트위터 총 리트윗': total_retweets,
                '트위터 평균 조회수': round(total_views / len(twitter_posts), 1) if twitter_posts else 0,
                '네이버 조회수 수집': f"{len(naver_views)}/{len(naver_posts)}",
                '네이버 평균 조회수': round(sum(naver_views) / len(naver_views), 1) if naver_views else 0
            })
        
        df = pd.DataFrame(analysis)
        df.to_excel(writer, sheet_name='해시태그 분석', index=False)
    
    def _create_daily_trends_sheet(self, writer, naver_data, twitter_data):
        """일별 트렌드 시트"""
        all_data = []
        
        # 네이버 데이터
        for item in naver_data:
            all_data.append({
                '날짜': item.get('post_date', ''),
                '플랫폼': '네이버 블로그',
                '키워드': item.get('keyword', ''),
                '국내/해외': item.get('region', '국내')
            })
        
        # 트위터 데이터
        for item in twitter_data:
            all_data.append({
                '날짜': item.get('post_date', ''),
                '플랫폼': 'Twitter',
                '키워드': item.get('keyword', ''),
                '국내/해외': item.get('region', '미분류')
            })
        
        if not all_data:
            return
        
        df = pd.DataFrame(all_data)
        
        # 날짜별, 플랫폼별, 키워드별 집계
        daily_counts = df.groupby(['날짜', '플랫폼', '키워드', '국내/해외']).size().reset_index(name='게시물 수')
        daily_counts = daily_counts.sort_values(['날짜', '플랫폼'], ascending=[False, True])
        
        daily_counts.to_excel(writer, sheet_name='일별 트렌드', index=False)
