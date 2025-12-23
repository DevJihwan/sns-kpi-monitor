#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNS KPI 모니터링 - 네이버 블로그 + 트위터 샘플
"""

import os
import sys
from dotenv import load_dotenv
from crawlers.naver_blog import NaverBlogCrawler
from crawlers.naver_blog_detail import NaverBlogDetailCrawler
from crawlers.twitter import TwitterCrawler
from utils.excel_generator import ExcelGenerator
import json
from datetime import datetime

# 환경변수 로드
load_dotenv()

def main():
    """메인 실행 함수"""
    
    print("\n")
    print("="*70)
    print("  SNS KPI 모니터링 시스템")
    print("  대상: 네이버 블로그 + Twitter(X)")
    print("="*70)
    print()
    
    # ========================================
    # 1. 설정
    # ========================================
    
    # 수집할 키워드 설정 (여기를 수정하세요!)
    keywords = [
        "테스트해시태그1",
        "테스트해시태그2",
        "테스트해시태그3",
        "테스트해시태그4"
    ]
    
    # 수집 개수 설정
    MAX_NAVER_PER_KEYWORD = 100  # 네이버 블로그: 키워드당 최대 100개
    MAX_TWITTER_PER_KEYWORD = 100  # 트위터: 키워드당 최대 100개
    
    print("📌 수집 설정")
    print(f"   키워드: {', '.join(keywords)}")
    print(f"   네이버 블로그: 키워드당 최대 {MAX_NAVER_PER_KEYWORD}개")
    print(f"   Twitter: 키워드당 최대 {MAX_TWITTER_PER_KEYWORD}개")
    print()
    
    # API 키 확인
    naver_client_id = os.getenv('NAVER_CLIENT_ID')
    naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
    
    if not naver_client_id or not naver_client_secret:
        print("❌ 오류: .env 파일에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 설정해주세요.")
        print("   1. .env.example 파일을 .env로 복사")
        print("   2. https://developers.naver.com/apps/#/register 에서 API 키 발급")
        print("   3. .env 파일에 키 입력")
        sys.exit(1)
    
    print("✅ 네이버 API 키 확인 완료")
    print()
    
    # ========================================
    # 2. 네이버 블로그 수집
    # ========================================
    
    print("\n" + "="*70)
    print("📝 STEP 1: 네이버 블로그 데이터 수집")
    print("="*70)
    
    naver_crawler = NaverBlogCrawler()
    all_naver_data = []
    
    for keyword in keywords:
        try:
            posts = naver_crawler.collect_by_keyword(keyword, MAX_NAVER_PER_KEYWORD)
            all_naver_data.extend(posts)
        except Exception as e:
            print(f"❌ 네이버 블로그 수집 실패 ({keyword}): {e}")
    
    print(f"\n📊 네이버 블로그 1단계 완료: 총 {len(all_naver_data)}개 URL 수집")
    
    # ========================================
    # 3. 네이버 블로그 상세 정보 수집
    # ========================================
    
    if all_naver_data:
        print("\n" + "="*70)
        print("🔍 STEP 2: 네이버 블로그 상세 정보 크롤링")
        print("="*70)
        print("⚠️  주의: 이 단계는 시간이 오래 걸립니다.")
        print(f"   예상 소요 시간: 약 {len(all_naver_data) * 4 / 60:.0f}분")
        print()
        
        # 사용자 확인
        response = input("계속하시겠습니까? (y/n): ").lower()
        if response != 'y':
            print("❌ 사용자가 취소했습니다.")
            sys.exit(0)
        
        detail_crawler = NaverBlogDetailCrawler(headless=True)
        all_naver_data = detail_crawler.batch_extract(all_naver_data, delay=2.0)
    
    # ========================================
    # 4. 트위터 수집
    # ========================================
    
    print("\n" + "="*70)
    print("🐦 STEP 3: Twitter 데이터 수집")
    print("="*70)
    
    twitter_crawler = TwitterCrawler()
    all_twitter_data = []
    
    for keyword in keywords:
        try:
            tweets = twitter_crawler.collect_by_keyword(keyword, MAX_TWITTER_PER_KEYWORD)
            all_twitter_data.extend(tweets)
        except Exception as e:
            print(f"❌ Twitter 수집 실패 ({keyword}): {e}")
    
    # ========================================
    # 5. 결과 요약
    # ========================================
    
    print("\n" + "="*70)
    print("📊 수집 결과 요약")
    print("="*70)
    print(f"네이버 블로그: {len(all_naver_data)}개")
    print(f"   └ 상세 크롤링 성공: {sum(1 for d in all_naver_data if d.get('detail_crawled'))}개")
    print(f"Twitter: {len(all_twitter_data)}개")
    print(f"   └ 국내: {sum(1 for d in all_twitter_data if d.get('region') == '국내')}개")
    print(f"   └ 해외: {sum(1 for d in all_twitter_data if d.get('region') == '해외')}개")
    print(f"총 게시물: {len(all_naver_data) + len(all_twitter_data)}개")
    print()
    
    # ========================================
    # 6. JSON 백업 저장
    # ========================================
    
    print("💾 JSON 백업 저장 중...")
    os.makedirs('data', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 네이버 데이터 저장
    naver_json_path = f'data/naver_data_{timestamp}.json'
    with open(naver_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_naver_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 네이버 데이터 저장: {naver_json_path}")
    
    # 트위터 데이터 저장
    twitter_json_path = f'data/twitter_data_{timestamp}.json'
    with open(twitter_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_twitter_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 트위터 데이터 저장: {twitter_json_path}")
    
    # ========================================
    # 7. Excel 리포트 생성
    # ========================================
    
    print("\n" + "="*70)
    print("📊 STEP 4: Excel 리포트 생성")
    print("="*70)
    
    excel_generator = ExcelGenerator(output_dir='output')
    report_path = excel_generator.generate_report(
        all_naver_data, 
        all_twitter_data, 
        keywords
    )
    
    # ========================================
    # 8. 완료
    # ========================================
    
    print("\n" + "="*70)
    print("✅ 모든 작업 완료!")
    print("="*70)
    print(f"📁 Excel 파일: {report_path}")
    print(f"📁 JSON 백업: data/ 폴더")
    print("="*70)
    print()
    
    # 통계 출력
    print("📈 최종 통계:")
    print(f"   총 수집 게시물: {len(all_naver_data) + len(all_twitter_data)}개")
    print(f"   네이버 블로그: {len(all_naver_data)}개")
    print(f"   Twitter: {len(all_twitter_data)}개")
    print()
    
    print("💡 다음 단계:")
    print("   1. output/ 폴더에서 Excel 파일 확인")
    print("   2. 각 시트별로 데이터 검토")
    print("   3. 필요시 키워드 조정 후 재실행")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 사용자가 프로그램을 중단했습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
