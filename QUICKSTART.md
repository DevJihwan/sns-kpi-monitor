# 🚀 빠른 시작 가이드

## 5분 안에 시작하기

### 1단계: 패키지 설치 (1분)

```bash
cd sns_kpi_monitor
pip3 install -r requirements.txt
```

### 2단계: 네이버 API 키 발급 (2분)

1. https://developers.naver.com/apps/#/register 접속
2. 로그인 후 **"애플리케이션 등록"** 클릭
3. 정보 입력:
   - 애플리케이션 이름: `SNS KPI Monitor`
   - 사용 API: **검색** 선택 → **블로그 검색** 체크
4. 등록 완료 후 **Client ID**와 **Client Secret** 복사

### 3단계: 환경 변수 설정 (1분)

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (원하는 에디터 사용)
nano .env
```

`.env` 파일에 붙여넣기:
```
NAVER_CLIENT_ID=복사한_클라이언트_ID
NAVER_CLIENT_SECRET=복사한_클라이언트_시크릿
```

저장하고 나가기 (nano: Ctrl+X → Y → Enter)

### 4단계: 실행! (1분)

```bash
python3 main.py
```

완료! 🎉

---

## 📝 키워드 변경하기

`main.py` 파일 편집:

```bash
nano main.py
```

아래 부분 찾아서 수정:
```python
keywords = [
    "원하는키워드1",
    "원하는키워드2",
    "원하는키워드3",
    "원하는키워드4"
]
```

---

## 📊 결과 확인

실행이 끝나면:

```bash
# Excel 파일 확인
ls -lh output/

# 예시:
# SNS_KPI_Report_20241223_153045.xlsx
```

---

## ⚠️ 문제 발생 시

### Chrome이 없다는 에러

**Mac:**
```bash
# Homebrew로 설치
brew install --cask google-chrome
```

**Ubuntu/Debian:**
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

### API 키 에러

```bash
# .env 파일 확인
cat .env

# 올바른 형식:
# NAVER_CLIENT_ID=abc123...
# NAVER_CLIENT_SECRET=def456...
```

### 패키지 에러

```bash
# 모든 패키지 재설치
pip3 install --upgrade -r requirements.txt
```

---

## 💡 테스트 실행

처음에는 적은 양으로 테스트하세요:

`main.py`에서:
```python
MAX_NAVER_PER_KEYWORD = 10   # 원래: 100
MAX_TWITTER_PER_KEYWORD = 10  # 원래: 100
```

이렇게 하면 약 2-3분 안에 끝납니다!

---

## 📞 도움이 필요하신가요?

상세한 내용은 `README.md` 파일을 참고하세요.
