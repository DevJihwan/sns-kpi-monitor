# SNS KPI 모니터링 시스템

네이버 블로그와 Twitter(X)에서 특정 해시태그의 KPI를 측정하는 시스템입니다.

## 📋 기능

- ✅ 네이버 블로그 검색 및 상세 정보 수집
- ✅ Twitter(X) 트윗 검색 및 통계 수집
- ✅ 조회수, 좋아요, 댓글 수 자동 수집
- ✅ 국내/해외 자동 분류
- ✅ Excel 리포트 자동 생성
- ✅ JSON 백업 저장

## 🎯 수집 데이터 항목

1. **국내/해외 구분**
2. **채널명 (ID)**
3. **원문 링크**
4. **조회수**
5. **좋아요 수**
6. **댓글 수**

## 📦 설치 방법

### 1. 프로젝트 클론

```bash
git clone https://github.com/DevJihwan/sns-kpi-monitor.git
cd sns-kpi-monitor
```

### 2. 필요한 패키지 설치

```bash
pip3 install -r requirements.txt
```

### 3. 네이버 API 키 발급

1. [네이버 개발자 센터](https://developers.naver.com/apps/#/register) 접속
2. 애플리케이션 등록
   - 애플리케이션 이름: SNS KPI Monitor
   - 사용 API: 검색 → 블로그 검색
3. Client ID와 Client Secret 복사

### 4. 환경 변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집
nano .env  # 또는 원하는 에디터 사용
```

`.env` 파일에 API 키 입력:
```
NAVER_CLIENT_ID=발급받은_클라이언트_ID
NAVER_CLIENT_SECRET=발급받은_클라이언트_시크릿
```

## 🚀 실행 방법

### 기본 실행

```bash
python3 main.py
```

### 키워드 변경 방법

`main.py` 파일을 열고 아래 부분을 수정:

```python
# 수집할 키워드 설정 (여기를 수정하세요!)
keywords = [
    "원하는키워드1",
    "원하는키워드2",
    "원하는키워드3",
    "원하는키워드4"
]
```

### 수집 개수 조정

```python
MAX_NAVER_PER_KEYWORD = 100   # 네이버: 키워드당 최대 100개
MAX_TWITTER_PER_KEYWORD = 100  # 트위터: 키워드당 최대 100개
```

## 📊 결과물

### Excel 파일 구조

생성되는 Excel 파일(`output/SNS_KPI_Report_YYYYMMDD_HHMMSS.xlsx`)에는 다음 시트가 포함됩니다:

1. **전체 요약**: 플랫폼별 게시물 수, 키워드별 통계
2. **통합 데이터**: 모든 SNS 데이터 통합 (핵심!)
   - 국내/해외, 채널명(ID), 원문링크, 조회수, 좋아요, 댓글
3. **네이버 블로그**: 네이버 블로그 상세 데이터
4. **Twitter**: 트위터 상세 데이터
5. **해시태그 분석**: 키워드별 참여 지표
6. **일별 트렌드**: 날짜별 게시물 추세

### JSON 백업

`data/` 폴더에 JSON 형식으로도 저장됩니다:
- `naver_data_YYYYMMDD_HHMMSS.json`
- `twitter_data_YYYYMMDD_HHMMSS.json`

## ⏱️ 예상 소요 시간

| 작업 | 소요 시간 (100개 기준) |
|------|----------------------|
| 네이버 API 수집 | 1-2분 |
| 네이버 상세 크롤링 | 5-8분 |
| 트위터 수집 | 2-3분 |
| Excel 생성 | 10초 |
| **총합** | **약 10분** |

## 📁 프로젝트 구조

```
sns_kpi_monitor/
├── crawlers/
│   ├── __init__.py
│   ├── naver_blog.py          # 네이버 API 크롤러
│   ├── naver_blog_detail.py   # 네이버 상세 크롤러 (Selenium)
│   └── twitter.py              # 트위터 크롤러
├── utils/
│   ├── __init__.py
│   └── excel_generator.py      # Excel 생성기
├── data/                        # JSON 백업 저장
├── output/                      # Excel 결과물
├── .env                         # API 키 (직접 생성)
├── .env.example                 # API 키 템플릿
├── requirements.txt             # 필요 패키지
├── main.py                      # 메인 실행 파일
└── README.md                    # 이 파일
```

## ⚠️ 주의사항

### 네이버 블로그
- **API 제한**: 일 25,000건 호출 제한
- **상세 크롤링**: 시간이 오래 걸립니다 (1개당 3-5초)
- **성공률**: 약 90-95%
- **일부 블로그**: 비공개 설정 시 조회수/댓글 수집 불가

### 트위터
- **ntscraper 사용**: 무료이지만 불안정할 수 있음
- **대안**: X API 유료 플랜 ($100/월) 사용 권장
- **국내/해외 구분**: 한글 포함 여부로 자동 판단

### 일반
- **속도 제한**: 과도한 요청은 IP 차단 위험
- **에러율**: 약 5-10% 예상 (삭제된 게시물, 타임아웃 등)
- **Chrome**: Selenium 사용을 위해 Chrome 브라우저 필요

## 🔧 문제 해결

### 1. "NAVER_CLIENT_ID를 설정해주세요" 에러
```bash
# .env 파일이 있는지 확인
ls -la .env

# 없다면 생성
cp .env.example .env
# 그리고 API 키 입력
```

### 2. "Chrome WebDriver 초기화 실패" 에러
```bash
# Chrome 브라우저 설치 확인
google-chrome --version  # Linux
# 또는
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version  # Mac

# Chrome이 없다면 설치 필요
```

### 3. "ntscraper 초기화 실패" 에러
```bash
# 패키지 재설치
pip3 uninstall ntscraper
pip3 install ntscraper
```

### 4. 트위터 수집이 안 됨
```python
# X API 유료 플랜 사용 권장
# 또는 다른 트위터 스크래핑 라이브러리 시도
```

## 💡 팁

### 1. 테스트 실행
처음에는 적은 개수로 테스트:
```python
MAX_NAVER_PER_KEYWORD = 10
MAX_TWITTER_PER_KEYWORD = 10
```

### 2. 헤드리스 모드 끄기
브라우저 화면을 보고 싶다면 `main.py`에서:
```python
detail_crawler = NaverBlogDetailCrawler(headless=False)
```

### 3. 수집 속도 조정
`naver_blog_detail.py`에서 delay 값 변경:
```python
all_naver_data = detail_crawler.batch_extract(all_naver_data, delay=3.0)  # 기본 2.0초
```

## 📧 문의

- 개발자: DevJihwan
- GitHub: https://github.com/DevJihwan

## 📜 라이선스

이 프로젝트는 SNS KPI 측정을 위한 도구입니다.
