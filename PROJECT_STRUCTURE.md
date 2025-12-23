# 프로젝트 구조

```
sns_kpi_monitor/
│
├── crawlers/                           # 크롤러 모듈
│   ├── __init__.py                    # 패키지 초기화
│   ├── naver_blog.py                  # 네이버 블로그 API 크롤러 (1단계: URL 수집)
│   ├── naver_blog_detail.py           # 네이버 블로그 Selenium 크롤러 (2단계: 상세 정보)
│   └── twitter.py                      # 트위터 크롤러
│
├── utils/                              # 유틸리티 모듈
│   ├── __init__.py                    # 패키지 초기화
│   └── excel_generator.py             # Excel 리포트 생성기
│
├── data/                               # JSON 백업 저장 폴더 (자동 생성)
│   ├── naver_data_YYYYMMDD_HHMMSS.json
│   └── twitter_data_YYYYMMDD_HHMMSS.json
│
├── output/                             # Excel 결과물 폴더 (자동 생성)
│   └── SNS_KPI_Report_YYYYMMDD_HHMMSS.xlsx
│
├── .env                                # 환경 변수 (직접 생성 필요!)
├── .env.example                        # 환경 변수 템플릿
├── .gitignore                          # Git 제외 파일
├── requirements.txt                    # 필요한 Python 패키지
├── main.py                             # 메인 실행 파일 ⭐
├── README.md                           # 상세 설명서
├── QUICKSTART.md                       # 빠른 시작 가이드
└── PROJECT_STRUCTURE.md               # 이 파일
```

## 주요 파일 설명

### 실행 파일
- **main.py**: 프로그램의 진입점. 이 파일을 실행하세요!

### 크롤러 (crawlers/)
1. **naver_blog.py**: 
   - Naver Search API를 사용
   - 블로그 URL, 제목, 작성자 등 기본 정보 수집
   - 빠름 (1000개 약 2분)

2. **naver_blog_detail.py**:
   - Selenium을 사용하여 각 블로그 페이지 방문
   - 조회수, 댓글 수, 좋아요 수 수집
   - 느림 (100개 약 5-8분)

3. **twitter.py**:
   - ntscraper를 사용하여 트윗 수집
   - 조회수, 좋아요, 댓글, 리트윗 등 모든 정보 수집

### 유틸리티 (utils/)
- **excel_generator.py**:
  - 수집된 데이터를 Excel 파일로 변환
  - 6개 시트 생성 (전체 요약, 통합 데이터, 각 플랫폼 등)

### 설정 파일
- **.env**: API 키를 저장하는 파일 (보안상 Git에 포함 안 됨)
- **.env.example**: .env 파일 생성 시 참고할 템플릿
- **requirements.txt**: 필요한 Python 패키지 목록

### 문서
- **README.md**: 자세한 사용 설명서
- **QUICKSTART.md**: 5분 안에 시작하는 방법

## 작동 순서

```
1. main.py 실행
   ↓
2. 네이버 블로그 API로 URL 수집 (naver_blog.py)
   ↓
3. 각 URL 방문하여 상세 정보 크롤링 (naver_blog_detail.py)
   ↓
4. 트위터 데이터 수집 (twitter.py)
   ↓
5. JSON 백업 저장 (data/)
   ↓
6. Excel 리포트 생성 (excel_generator.py → output/)
   ↓
7. 완료!
```

## 데이터 흐름

```
[ 키워드 입력 ]
       ↓
[ API/크롤링 수집 ]
       ↓
[ Python Dict 형태 ]
       ↓
[ JSON 저장 (백업) ]
       ↓
[ Pandas DataFrame 변환 ]
       ↓
[ Excel 파일 생성 ]
```

## Excel 시트 구조

생성되는 Excel 파일의 6개 시트:

1. **전체 요약**: 플랫폼별 게시물 수, 키워드별 통계
2. **통합 데이터**: 국내/해외, 채널명, URL, 조회수, 좋아요, 댓글 (핵심!)
3. **네이버 블로그**: 네이버만 모아서 상세히
4. **Twitter**: 트위터만 모아서 상세히
5. **해시태그 분석**: 키워드별 참여 지표 분석
6. **일별 트렌드**: 날짜별 게시물 추세

## 커스터마이징 포인트

### 키워드 변경
`main.py` 24-29줄:
```python
keywords = [
    "원하는키워드"
]
```

### 수집 개수 조정
`main.py` 32-33줄:
```python
MAX_NAVER_PER_KEYWORD = 100
MAX_TWITTER_PER_KEYWORD = 100
```

### 크롤링 속도 조정
`main.py` 92줄:
```python
all_naver_data = detail_crawler.batch_extract(all_naver_data, delay=2.0)
# delay 값을 늘리면 느려지지만 안정적
```

### 헤드리스 모드 끄기 (브라우저 보기)
`main.py` 86줄:
```python
detail_crawler = NaverBlogDetailCrawler(headless=False)
```
