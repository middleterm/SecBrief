# SecBrief 프로젝트 가이드

> Python 기말 프로젝트: 사용자 맞춤형 사이버 보안 뉴스 수집 및 관리 프로그램

## 1. 프로젝트 목적

SecBrief는 RSS에서 사이버 보안 기사를 수집하고, 기사를 CSV 파일에 저장한 뒤, 사용자가 선택한 관심 분야와 직접 입력한 키워드로 기사를 찾아보는 프로그램이다.

AI API나 데이터베이스를 사용하지 않고 Python 기본 문법과 파일 입출력을 중심으로 구현한다.

## 2. 전체 실행 흐름

```text
RSS 수집
    ↓
기사 딕셔너리 정리
    ↓
data/articles.csv에 저장
    ↓
기본 분야 및 사용자 키워드 선택
    ↓
제목·내용 키워드 검색
    ↓
기사 목록, 검색 결과 수, 키워드별 통계 표시
```

## 3. 파일 구조

```text
SecBrief/
├─ crawler.py                 # RSS 수집 및 HTML 정리
├─ recommender.py             # 키워드 검색과 통계 계산
├─ storage.py                 # CSV/TXT 파일 읽기와 저장
├─ app.py                     # Streamlit 화면
├─ requirements.txt           # 필요한 외부 라이브러리
├─ data/
│  ├─ articles.csv            # 수집된 기사 저장 파일
│  └─ keywords.txt            # 사용자 키워드 저장 파일
└─ tests/
   ├─ test_crawler.py
   ├─ test_recommender.py
   ├─ test_storage.py
   └─ test_integration.py
```

## 4. 공통 기사 데이터 형식

RSS에서 가져온 기사는 아래 딕셔너리 형식을 사용한다.

```python
{
    "title": "기사 제목",
    "link": "https://example.com/article",
    "date": "발행일",
    "content": "기사 요약 또는 설명",
    "source": "KISA 보호나라"
}
```

| 키 | 설명 | 값이 없을 때 |
|---|---|---|
| `title` | 기사 제목 | 제목이 없는 기사는 건너뜀 |
| `link` | 원문 링크 | 링크가 없는 기사는 건너뜀 |
| `date` | 발행일 또는 수정일 | `날짜 없음` |
| `content` | RSS의 `summary` 또는 `description` | `내용 없음` |
| `source` | 기사를 수집한 RSS 출처 | `기존 저장 기사` |

CSV의 열 순서는 `title, link, date, content, source`이다. 기존 4열 CSV를 읽을 때는 기사 데이터를 보존하고 출처만 `기존 저장 기사`로 표시한다.

## 5. 파일별 역할

### crawler.py

- `feedparser`로 RSS를 읽는다.
- KISA 보호나라와 The Hacker News RSS 주소를 보관한다.
- 선택한 RSS 출처 이름을 기사 딕셔너리의 `source`에 저장한다.
- 기사 제목과 내용을 정리하고 HTML 태그를 제거한다.
- 제목이나 링크가 없는 항목은 저장하지 않는다.
- 수집 실패 시 빈 리스트를 반환하고 오류 내용을 출력한다.

```python
articles = fetch_articles(
    RSS_SOURCES["1"]["url"],
    limit=10,
    source=RSS_SOURCES["1"]["name"],
)
```

### storage.py

- `data` 폴더가 없으면 `os.makedirs()`로 만든다.
- `save_articles()`는 링크를 비교해 같은 기사를 한 번만 CSV에 저장한다.
- `load_articles()`는 CSV를 기사 딕셔너리 리스트로 읽는다.
- 기존 4열 CSV도 읽어 기사 데이터 유실을 막고 `source`만 기본값으로 보완한다.
- `save_keywords()`는 사용자 키워드를 TXT 파일에 한 줄씩 쓴다.
- `load_keywords()`는 TXT 파일을 한 줄씩 읽는다.
- 파일이 아직 없으면 빈 리스트를 반환한다.

### recommender.py

기본 관심 분야는 웹 보안, 악성코드, 개인정보, 클라우드 네 가지다.

```python
CATEGORY_KEYWORDS = {
    "웹 보안": [...],
    "악성코드": [...],
    "개인정보": [...],
    "클라우드": [...]
}
```

- `get_keywords()`가 선택 분야와 사용자 키워드를 합친다.
- `filter_articles()`가 제목과 내용을 소문자로 바꿔 키워드를 검색한다.
- 영문 대소문자를 구분하지 않는다.
- 여러 키워드에 맞는 기사도 결과에는 한 번만 넣는다.
- `count_articles_by_keyword()`가 키워드마다 일치 기사 수를 계산한다.

### app.py

Streamlit 화면에서 다음 기능을 제공한다.

1. RSS 기사 수집
2. KISA 보호나라 또는 The Hacker News 출처 선택
3. CSV에 저장된 기사 불러오기
4. 관심 분야 선택
5. 사용자 키워드 추가 및 삭제
6. 전체 기사 수와 검색 결과 수 표시
7. 기사 제목, 발행일, 출처, 내용, 원문 링크 표시
8. 키워드별 기사 수와 막대그래프 표시

그래프는 맑은 고딕을 사용하며, 세로축을 0부터 정수 단위로 표시한다. 일치하는 기사가 없으면 빈 그래프 대신 안내 문구를 보여 준다.

검색 조건을 하나도 선택하지 않으면 저장된 전체 기사를 보여 준다.

## 6. 실행 방법

프로젝트 폴더에서 필요한 라이브러리를 설치한다.

```bash
pip install -r requirements.txt
```

Streamlit 앱을 실행한다.

```bash
streamlit run app.py
```

브라우저에서 RSS 출처를 선택한 뒤 `RSS 기사 수집`을 누르면 선택한 출처의 최신 기사가 `data/articles.csv`에 저장된다.

## 7. 테스트 실행

실제 인터넷에 접속하지 않는 단위 테스트와 모의 RSS 통합 테스트를 실행한다.

```bash
python -m unittest discover -s tests -v
```

테스트 범위는 다음과 같다.

- RSS 기사 필드 정리와 누락 항목 처리
- 기본 분야 및 사용자 키워드 검색
- 대소문자 무시와 중복 결과 방지
- CSV 기사 중복 저장 방지
- TXT 키워드 저장 및 불러오기
- 수집 결과가 분류 기능으로 이어지는지 확인

## 8. requirements.txt

```text
feedparser
streamlit
matplotlib
```

AI 요약을 제거했으므로 `openai`와 `python-dotenv`는 설치하지 않는다.

## 9. 구현 원칙

- 클래스, 데이터베이스, AI API를 사용하지 않는다.
- 리스트, 딕셔너리, `for`, `if`, 함수, `try/except`를 중심으로 작성한다.
- CSV는 `csv.reader()`와 `csv.writer()`를 사용한다.
- 사용자 입력 키워드는 공백을 제거하고 빈 값은 저장하지 않는다.
- 원문 링크를 기사 중복 판단 기준으로 사용한다.
- RSS와 파일 오류가 발생해도 앱 전체가 종료되지 않도록 안내한다.

## 10. 프로젝트에서 제외한 기능

AI 요약, API 키 설정, 회원가입, 데이터베이스, 실시간 알림, 머신러닝 분류, 서버 배포는 구현하지 않는다.
