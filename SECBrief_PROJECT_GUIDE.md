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
│  └─ memos.csv               # 기사별 학습 메모 저장 파일
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
- `summary`, `description`, `content` 순서로 RSS 본문을 확인한다.
- RSS 본문이 없으면 `requests`와 `BeautifulSoup`으로 원문을 읽는다.
- KISA 공지는 개요·설명·영향 제품·해결 방안을 추출하고, 일반 뉴스는 본문 앞부분을 추출한다.
- 메뉴·광고·문의 문구와 HTML 태그를 제거한다.
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
- 기존 기사에 내용이 없으면 새로 수집한 본문으로 해당 행만 갱신한다.
- `save_keywords()`는 사용자 키워드를 TXT 파일에 한 줄씩 쓴다.
- `load_keywords()`는 TXT 파일을 한 줄씩 읽는다.
- `save_memos()`와 `load_memos()`는 기사 링크별 학습 메모를 `data/memos.csv`에 저장하고 읽는다.
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
9. 선택 기사별 학습 메모 작성 및 `data/memos.csv` 저장

기사 수집 버튼을 누르면 내용이 없는 기존 기사도 원문에서 본문을 다시 확인한다.

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
requests
beautifulsoup4
```

AI 요약을 제거했으므로 `openai`와 `python-dotenv`는 설치하지 않는다.

## 9. 구현 원칙

- 클래스, 데이터베이스, AI API를 사용하지 않는다.
- 리스트, 딕셔너리, `for`, `if`, 함수, `try/except`를 중심으로 작성한다.
- CSV는 `csv.reader()`와 `csv.writer()`를 사용한다.
- AI API 없이 RSS와 원문 HTML에서 기사 본문을 수집한다.
- 사용자 입력 키워드는 공백을 제거하고 빈 값은 저장하지 않는다.
- 원문 링크를 기사 중복 판단 기준으로 사용한다.
- RSS와 파일 오류가 발생해도 앱 전체가 종료되지 않도록 안내한다.

## 10. 프로젝트에서 제외한 기능

AI 요약, API 키 설정, 회원가입, 데이터베이스, 실시간 알림, 머신러닝 분류, 서버 배포는 구현하지 않는다.



https://github.com/middleterm/SecBrief 사용한 변수명 md 파일로 정리해. 호출이나 그런거 라우트? 뭐라해 그런것도 정리

정리 완료했어.

SECBRIEF_VARIABLE_AND_CALL_FLOW.md

포함 내용:

파일별 모든 주요 변수명과 역할
매개변수·지역변수·전역변수 구분
st.session_state 변수 설명
함수별 입력값과 반환값
모듈 사이의 함수 호출 관계
기사 수집·필터링·메모 저장 전체 실행 순서
changed_count, selected_link, searchable_text 등 헷갈리는 변수 상세 설명
발표 때 사용할 핵심 설명
참고로 이 프로젝트에는 API 라우트가 없어서, 정확한 표현인 함수 호출 관계와 데이터 흐름으로 정리했어. 테스트 파일 내부의 테스트용 변수까지는 포함하지 않고 실제 프로그램을 구성하는 네 개의 핵심 파일을 기준으로 작성했어.





SecBrief 변수명 및 함수 호출 흐름 정리
기준: main 브랜치의 app.py, crawler.py, recommender.py, storage.py
이 프로젝트에는 FastAPI의 @app.get() 같은 **API 라우트(route)**가 없다. 여기서는 라우트 대신 함수 호출 관계와 데이터 흐름을 정리한다.

1. 전체 구조
파일	역할	다른 파일과의 관계
app.py	Streamlit 화면과 전체 실행 순서 관리	나머지 세 모듈의 함수들을 호출함
crawler.py	RSS 및 원문에서 기사 수집	수집한 기사 딕셔너리 리스트를 app.py에 반환함
storage.py	기사·키워드·메모 파일 입출력	데이터를 CSV/TXT에 저장하고 다시 불러옴
recommender.py	관심 분야 필터링과 통계 계산	기사와 키워드를 받아 필터 결과와 개수를 반환함
사용자 조작
   ↓
app.py
   ├─ crawler.py      기사 수집·본문 추출
   ├─ storage.py      파일 저장·불러오기
   └─ recommender.py  기사 필터링·통계 계산
2. 공통 기사 데이터 구조
기사 하나는 딕셔너리, 여러 기사는 딕셔너리를 담은 리스트로 관리한다.

article = {
    "title": "기사 제목",
    "link": "원문 주소",
    "date": "발행일",
    "content": "기사 내용",
    "source": "RSS 출처",
}

articles = [article1, article2, article3]
키 이름	뜻	주로 사용되는 곳
title	기사 제목	화면 표시, 키워드 검색
link	기사 원문 주소이자 기사의 고유 식별값	중복 판단, 기사 선택, 메모 연결
date	기사 발행일 또는 수정일	화면 표시
content	RSS 또는 원문에서 가져온 기사 내용	화면 표시, 키워드 검색
source	KISA 보호나라 등 기사 출처	출처 표시, 수집 방식 구분
3. crawler.py 변수명
전역변수
변수명	자료형	의미
RSS_SOURCES	딕셔너리	수집 가능한 RSS의 이름과 URL을 저장함
함수별 변수
clean_content(text)
변수명	역할
text	정리할 원본 문자열. HTML 엔티티·태그·연속 공백을 제거한 뒤 반환함
get_rss_content(entry)
변수명	역할
entry	RSS 기사 하나의 데이터
content_fields	내용을 찾을 필드 순서: summary, description, content
field	현재 확인 중인 필드 이름
value	해당 필드에 들어 있는 값
item	value가 리스트일 때 그 안의 항목 하나
content	clean_content()로 정리한 기사 내용
remove_unnecessary_tags(soup)
변수명	역할
soup	BeautifulSoup으로 분석한 HTML 문서
remove_names	제거할 HTML 태그 이름 목록
tag	현재 확인하거나 제거하는 HTML 태그
remove_words	클래스명·ID에 포함되면 제거할 단어 목록
class_value	태그의 class 값
id_value	태그의 id 값
attributes	클래스와 ID를 합쳐 소문자로 만든 검색용 문자열
should_remove	해당 태그를 제거해야 하는지 나타내는 불리언 값
word	현재 검사하는 제거 대상 단어
is_noise_text(text)
변수명	역할
text	메뉴·광고·문의 문구인지 확인할 문자열
noise_words	기사 본문에서 제외할 표현 목록
noise_word	현재 검사 중인 제외 표현
get_main_area(soup)
변수명	역할
soup	분석할 HTML 문서
content_area	.content_html 클래스로 찾은 본문 영역
article_area	<article> 태그로 찾은 본문 영역
main_area	<main> 태그로 찾은 본문 영역
get_page_lines(soup)
변수명	역할
soup	분석할 HTML 문서
lines	정리된 본문 줄을 모으는 리스트
page_text	본문 영역 전체를 줄바꿈 기준으로 꺼낸 문자열
line	현재 정리하고 검사하는 한 줄
is_section_line(line)
변수명	역할
line	KISA 공지의 구역 제목인지 검사할 줄
section_words	개요·설명·해결 방안 등 구역 제목 목록
section_word	현재 비교 중인 구역 제목
normalized_line	양끝 기호와 공백을 제거한 줄
extract_kisa_content(soup)
변수명	역할
content_area	KISA 페이지의 .content_html 영역
result	최종 본문 조각을 순서대로 담는 리스트
item	본문 안의 현재 문단 또는 표
text	문단에서 추출하고 정리한 글
table_rows	표의 행들을 문자열로 저장하는 리스트
row	현재 표 행(<tr>)
cells	현재 행의 셀 값들을 저장하는 리스트
cell	현재 표 셀(<th> 또는 <td>)
cell_text	셀에서 추출한 문자열
table_row	`
lines	페이지 전체에서 정리한 텍스트 줄 목록
sections	찾을 구역 이름과 가능한 표현을 묶은 목록
section_name	결과에 표시할 구역 이름
section_labels	해당 구역을 찾을 때 사용할 표현 목록
start_index	현재 구역이 시작되는 lines의 위치
index	lines를 순회할 때의 위치 번호
label	현재 확인하는 구역 표현
section_lines	현재 구역에 속한 본문 줄 목록
first_line	구역 제목이 발견된 첫 줄
first_text	첫 줄에서 구역 제목을 제거하고 남은 본문
next_index	다음 줄부터 구역 본문을 읽기 위한 위치 번호
extract_general_content(soup)
변수명	역할
lines	페이지에서 정리한 텍스트 줄 목록
paragraphs	길이가 충분한 문단을 담는 리스트
paragraph	현재 확인 중인 <p> 태그
text	문단 또는 본문 영역에서 추출한 문자열
block	문단이 없을 때 확인하는 <article> 또는 <main> 영역
all_text	모든 문단을 하나로 합친 문자열
sentences	문장부호 기준으로 나눈 문장 목록
selected_sentences	화면에 사용할 최대 5개의 문장
sentence	현재 길이 등을 확인하는 문장
fetch_web_content(url, source="")
변수명	역할
url	가져올 기사 원문 주소
source	기사 출처. KISA 전용 추출 방식을 선택할 때 사용
response	requests.get()으로 받은 HTTP 응답
soup	응답 HTML을 분석한 BeautifulSoup 객체
content	사이트별 방식으로 추출한 기사 내용
cleaned_lines	마지막으로 공백을 정리한 본문 줄 목록
line	현재 정리 중인 본문 한 줄
error	원문 수집 과정에서 발생한 예외 객체
refresh_article_contents(articles)
변수명	역할
articles	저장되어 있던 기사 리스트
updated_count	본문을 새로 채운 기사 수
article	현재 확인하는 기사 딕셔너리
old_content	기사에 기존부터 저장되어 있던 내용
link	현재 기사의 원문 주소
new_content	원문에서 다시 가져온 새 기사 내용
fetch_articles(rss_url, limit=10, source="알 수 없는 출처")
변수명	역할
rss_url	읽을 RSS 주소
limit	최대 수집 기사 수
source	기사에 기록할 RSS 출처 이름
articles	수집한 기사 딕셔너리를 담는 리스트
feed	feedparser.parse()가 반환한 RSS 분석 결과
entries	RSS에 들어 있는 기사 항목 목록
entry	현재 처리 중인 RSS 기사 항목
title	정리한 기사 제목
link	정리한 원문 주소
date	발행일 또는 수정일
content	RSS 또는 원문에서 가져온 기사 내용
article	다섯 필드로 완성한 기사 딕셔너리
error	RSS 수집 과정에서 발생한 예외 객체
4. storage.py 변수명
전역변수
변수명	의미
BASE_FOLDER	storage.py가 있는 프로젝트 폴더
DATA_FOLDER	데이터를 저장할 data 폴더 경로
ARTICLES_FILE	data/articles.csv 경로
KEYWORDS_FILE	data/keywords.txt 경로
MEMOS_FILE	data/memos.csv 경로
ARTICLE_FIELDS	기사 CSV의 열 이름과 순서
함수별 변수
load_articles()
변수명	역할
articles	파일에서 읽은 기사 딕셔너리 리스트
file	열려 있는 기사 CSV 파일 객체
reader	CSV를 행 단위 리스트로 읽는 객체
row	현재 읽은 CSV 한 행
article	row를 변환해 만든 기사 딕셔너리
error	파일 또는 CSV 읽기 예외
save_articles(articles)
변수명	역할
articles	새로 저장하거나 갱신할 기사 리스트
old_articles	CSV에 이미 저장된 기사 리스트
saved_links	기존 기사들의 링크 목록. 중복 판단에 사용
article	현재 비교하거나 저장하는 기사
changed_count	새로 추가하거나 본문을 갱신한 기사 수. 단순히 입력받은 기사 수가 아님
title	공백을 제거한 새 기사 제목
link	공백을 제거한 새 기사 링크
existing_index	같은 링크를 가진 기존 기사의 위치
old_article	같은 링크로 이미 저장되어 있던 기사
new_content	새로 수집한 기사 본문
old_content	기존 CSV에 저장된 기사 본문
file	쓰기 모드로 연 기사 CSV 파일 객체
writer	CSV에 행을 쓰는 객체
error	파일 저장 예외
changed_count가 필요한 이유는 수집한 기사 중 실제 파일에 변화가 생긴 수만 사용자에게 알려 주기 위해서다. 예를 들어 10개를 수집했어도 8개가 중복이면 changed_count는 2가 될 수 있다.

load_keywords() / save_keywords(keywords)
변수명	역할
keywords	읽었거나 저장할 사용자 키워드 리스트
clean_keywords	공백과 대소문자 중복을 제거한 최종 키워드 리스트
file	키워드 TXT 파일 객체
line	파일에서 읽은 한 줄
keyword	현재 확인하는 키워드
duplicate	같은 키워드가 이미 있는지 표시
item	기존 정리 목록과 비교하는 키워드
error	파일 입출력 예외
load_memos() / save_memos(memos)
변수명	역할
memos	{기사 링크: 메모 내용} 형태의 딕셔너리
file	메모 CSV 파일 객체
reader	메모 CSV를 읽는 객체
writer	메모 CSV를 쓰는 객체
row	[link, memo] 형태의 CSV 한 행
link	현재 저장하는 기사의 링크
error	파일 또는 CSV 입출력 예외
5. recommender.py 변수명
전역변수
변수명	자료형	의미
CATEGORY_KEYWORDS	딕셔너리	관심 분야별 기본 검색 키워드 목록
함수별 변수
get_keywords(selected_categories, user_keywords=None)
변수명	역할
selected_categories	사용자가 선택한 관심 분야 리스트
user_keywords	사용자가 직접 저장한 키워드 리스트
keywords	기본 키워드와 사용자 키워드를 합친 최종 리스트
category	현재 확인 중인 관심 분야
category_keywords	현재 분야에 등록된 기본 키워드 목록
keyword	현재 추가하려는 키워드
duplicate	같은 키워드가 이미 있는지 표시
item	기존 키워드와 중복 비교할 값
filter_articles(articles, selected_categories, user_keywords=None)
변수명	역할
articles	필터링할 전체 기사 리스트
selected_categories	선택된 관심 분야 리스트
user_keywords	사용자 키워드 리스트
keywords	검색에 사용할 모든 키워드
filtered_articles	키워드와 일치한 기사 리스트
article	현재 검사 중인 기사
title	현재 기사의 제목
content	현재 기사의 본문
searchable_text	제목과 본문을 합쳐 소문자로 만든 검색용 문자열
matched	기사에 키워드가 하나라도 포함됐는지 표시
keyword	현재 검색하는 키워드
count_articles_by_keyword(articles, keywords)
변수명	역할
articles	통계를 낼 기사 리스트
keywords	개수를 계산할 키워드 목록
counts	{키워드: 일치 기사 수} 형태의 결과 딕셔너리
keyword	현재 개수를 세는 키워드
count	현재 키워드와 일치한 기사 수
lower_keyword	대소문자 구분 없이 비교하기 위해 소문자로 바꾼 키워드
article	현재 검사 중인 기사
title, content	현재 기사의 제목과 본문
searchable_text	제목과 본문을 합쳐 소문자로 만든 검색용 문자열
6. app.py 주요 변수명
st.session_state에 보관하는 값
Streamlit은 사용자가 버튼을 누를 때마다 app.py 전체를 다시 실행한다. 따라서 다시 실행되어도 유지해야 하는 값은 st.session_state에 저장한다.

상태 이름	의미
st.session_state.articles	현재 불러온 전체 기사 리스트
st.session_state.keywords	저장된 사용자 키워드 리스트
st.session_state.memos	기사 링크별 메모 딕셔너리
st.session_state.selected_link	현재 화면에 선택된 기사의 링크
st.session_state[memo_key]	선택 기사 메모 입력창의 현재 내용
기사 태그 함수
get_article_tags(article, user_keywords)
변수명	역할
article	태그를 찾을 기사 딕셔너리
user_keywords	사용자가 직접 저장한 키워드 목록
title, content	기사의 제목과 내용
searchable_text	제목과 본문을 합쳐 소문자로 만든 검색용 문자열
categories	기사와 일치한 관심 분야 목록
keywords	기사에서 발견한 기본·사용자 키워드 목록
user_keyword_matched	사용자 키워드가 하나라도 일치했는지 표시
category	현재 검사하는 분야
category_matched	현재 분야의 키워드가 하나라도 일치했는지 표시
keyword	현재 검사하는 키워드
duplicate	같은 태그가 이미 추가됐는지 표시
saved_keyword	이미 추가된 태그와 비교할 값
화면과 실행 흐름에서 사용하는 변수
변수명	의미
source_names	화면의 출처 선택 상자에 표시할 이름 목록
source_key	RSS_SOURCES를 순회하는 키
selected_source_name	사용자가 선택한 RSS 출처 이름
selected_source_url	선택한 출처에 대응하는 RSS URL
header_title, header_button	제목 영역과 수집 버튼 영역의 Streamlit 열
collect_clicked	기사 수집 버튼을 눌렀는지 표시
collected_articles	이번에 RSS에서 수집한 기사 목록
changed_count	CSV에 새로 추가하거나 갱신한 기사 수
stored_articles	CSV에서 다시 읽은 전체 기사 목록
refreshed_count	원문에서 본문을 새로 채운 기존 기사 수
category_options	관심 분야 라디오 버튼의 선택지 목록
selected_category	사용자가 현재 선택한 분야 하나
selected_categories	추천 함수에 전달하기 위한 선택 분야 리스트
articles	세션에 저장된 전체 기사 목록을 가리키는 변수
user_keywords	세션에 저장된 키워드 목록을 가리키는 변수
filtered_articles	선택 분야·키워드와 일치한 기사 목록
filtered_links	필터 결과 기사들의 링크 목록
selected_index	선택 기사가 필터 결과에서 몇 번째인지 나타내는 인덱스
selected_article	현재 화면 중앙에 표시할 기사 딕셔너리
index	기사 목록을 반복할 때의 위치 번호
article_label	사이드바 버튼에 표시할 번호와 기사 제목
button_key	Streamlit이 기사 버튼들을 구분하기 위한 고유 키
clicked	현재 기사 선택 버튼을 눌렀는지 표시
new_keyword	사용자가 입력창에 새로 입력한 키워드
duplicated	새 키워드가 기존 목록과 중복되는지 표시
keywords	새 키워드를 추가하기 위해 복사한 키워드 리스트
saved_keywords	정리 후 파일에 저장된 최종 키워드 리스트
keyword_to_delete	사용자가 삭제 대상으로 선택한 키워드
remaining_keywords	삭제 대상만 제외하고 다시 만든 키워드 리스트
article_categories	선택 기사와 일치한 관심 분야 목록
article_keywords	선택 기사에서 발견한 키워드 태그 목록
date_column, source_column, category_column	기사 정보를 나누어 표시하는 세 열
tag_text	화면에 Markdown 태그 형태로 표시할 문자열
previous_column, count_column, next_column	이전·현재 번호·다음 버튼 영역
bottom_mode	하단에서 기사 통계와 학습 메모 중 선택한 화면
statistics_column, collection_column	그래프 영역과 수집 현황 영역
all_keywords	통계에 사용할 기본·사용자 키워드 전체 목록
keyword_counts	{키워드: 기사 수} 통계 딕셔너리
has_matched_keyword	일치 기사 수가 1개 이상인 키워드가 있는지 표시
max_count	그래프 세로축 범위를 정하기 위한 가장 큰 기사 수
figure, axis	Matplotlib 그래프 전체와 좌표축 객체
memo_key	기사 링크를 붙여 만든 메모 입력창의 고유 키
memo_column, save_column	메모 입력 영역과 저장 버튼 영역
7. 함수 호출 관계
호출하는 곳	호출되는 함수·기능	목적
app.py 시작	load_articles()	기존 기사 불러오기
app.py 시작	load_keywords()	사용자 키워드 불러오기
app.py 시작	load_memos()	기사별 메모 불러오기
app.py 기사 수집 버튼	fetch_articles()	선택한 RSS에서 기사 수집
fetch_articles()	clean_content()	제목과 본문 문자열 정리
fetch_articles()	get_rss_content()	RSS 내부의 기사 내용 탐색
get_rss_content()	clean_content()	RSS 내용 정리
fetch_articles()	fetch_web_content()	RSS에 내용이 없을 때 원문 수집
fetch_web_content()	extract_kisa_content()	KISA 공지 본문 추출
fetch_web_content()	extract_general_content()	일반 뉴스 본문 추출
본문 추출 함수	remove_unnecessary_tags(), get_page_lines(), is_noise_text()	메뉴·광고 등 불필요한 내용 제거
app.py 기사 수집 버튼	save_articles()	수집 기사를 중복 없이 저장
save_articles()	load_articles()	기존 기사와 비교
save_articles()	ensure_data_folder()	저장 전 data 폴더 보장
app.py 기사 수집 버튼	refresh_article_contents()	내용 없는 기존 기사 재수집
refresh_article_contents()	fetch_web_content()	기사 원문에서 본문 가져오기
app.py 필터 영역	filter_articles()	분야·키워드에 맞는 기사만 선택
filter_articles()	get_keywords()	검색할 키워드 목록 만들기
app.py 기사 카드	get_article_tags()	선택 기사에 분야·키워드 태그 부여
app.py 통계 영역	get_keywords()	통계 대상 키워드 목록 만들기
app.py 통계 영역	count_articles_by_keyword()	키워드별 기사 수 계산
app.py 키워드 추가·삭제	save_keywords()	키워드 TXT 저장
save_keywords()	ensure_data_folder()	저장 전 data 폴더 보장
app.py 메모 저장 버튼	save_memos()	링크별 메모 CSV 저장
save_memos()	ensure_data_folder()	저장 전 data 폴더 보장
8. 기능별 실행 순서
8-1. 앱을 처음 실행할 때
app.py 실행
  ├─ load_articles() → st.session_state.articles
  ├─ load_keywords() → st.session_state.keywords
  ├─ load_memos()    → st.session_state.memos
  └─ selected_link 초기화
8-2. 기사 수집 버튼을 눌렀을 때
선택한 출처 이름과 RSS URL 확인
  ↓
fetch_articles()
  ├─ feedparser.parse()로 RSS 읽기
  ├─ get_rss_content()로 RSS 본문 확인
  └─ 내용이 없으면 fetch_web_content()로 원문 확인
  ↓
save_articles()
  ├─ 링크로 중복 검사
  ├─ 새 기사는 추가
  └─ 기존 본문이 비어 있으면 본문만 갱신
  ↓
refresh_article_contents()
  └─ 여전히 내용이 없는 기존 기사 재수집
  ↓
load_articles()
  └─ 최신 CSV 내용을 session_state에 다시 저장
8-3. 관심 분야나 키워드로 기사를 찾을 때
선택 분야 + 사용자 키워드
  ↓
get_keywords() → 중복 없는 검색 키워드 목록
  ↓
filter_articles()
  ├─ 기사 제목 + 본문을 searchable_text로 결합
  ├─ 모두 소문자로 바꿔 대소문자 차이 제거
  └─ 키워드가 하나라도 있으면 결과에 추가
  ↓
filtered_articles를 사이드바와 기사 카드에 표시
8-4. 메모를 저장할 때
선택 기사의 link로 memo_key 생성
  ↓
사용자가 st.text_area에 메모 입력
  ↓
st.session_state.memos[기사 link] = 메모 내용
  ↓
save_memos()
  ↓
data/memos.csv에 link, memo 형태로 저장
9. 함수별 입력값과 반환값 요약
함수	입력	반환
clean_content()	문자열	정리된 문자열
get_rss_content()	RSS 기사 항목	RSS에서 찾은 내용 또는 빈 문자열
remove_unnecessary_tags()	BeautifulSoup 객체	없음. 전달받은 객체를 직접 수정
is_noise_text()	문자열	제외 문구 여부 True/False
get_main_area()	BeautifulSoup 객체	본문으로 판단한 HTML 영역
get_page_lines()	BeautifulSoup 객체	정리된 본문 줄 리스트
is_section_line()	한 줄 문자열	구역 제목 여부 True/False
extract_kisa_content()	BeautifulSoup 객체	KISA 본문 문자열
extract_general_content()	BeautifulSoup 객체	일반 기사 본문 문자열
fetch_web_content()	URL, 출처	원문 본문 또는 빈 문자열
refresh_article_contents()	기사 리스트	본문을 갱신한 기사 수
fetch_articles()	RSS URL, 제한 수, 출처	기사 딕셔너리 리스트
ensure_data_folder()	없음	없음. 필요하면 폴더 생성
load_articles()	없음	기사 딕셔너리 리스트
save_articles()	기사 리스트	추가·갱신된 기사 수
load_keywords()	없음	키워드 리스트
save_keywords()	키워드 리스트	정리된 키워드 리스트, 실패 시 None
load_memos()	없음	{링크: 메모} 딕셔너리
save_memos()	메모 딕셔너리	성공 여부 True/False
get_keywords()	선택 분야, 사용자 키워드	중복 없는 키워드 리스트
filter_articles()	기사, 선택 분야, 사용자 키워드	필터링된 기사 리스트
count_articles_by_keyword()	기사, 키워드	{키워드: 기사 수} 딕셔너리
get_article_tags()	기사, 사용자 키워드	(분야 리스트, 키워드 리스트) 튜플
10. 발표 때 사용할 핵심 설명
app.py가 전체 흐름을 관리하고, 수집은 crawler.py, 저장은 storage.py, 분류와 통계는 recommender.py에 맡긴 구조다.
기사 하나는 딕셔너리로, 여러 기사는 리스트로 관리한다.
기사 링크인 link를 중복 판별 기준이자 기사와 메모를 연결하는 고유값처럼 사용한다.
searchable_text는 제목과 본문을 합친 검색용 문자열이다. 소문자로 바꿔 영문 대소문자 차이를 없앤다.
changed_count는 수집 개수가 아니라 CSV에 실제로 추가되거나 갱신된 기사 개수다.
Streamlit은 버튼을 누를 때 코드가 다시 실행되므로 기사·키워드·메모·선택 기사는 st.session_state에 보관한다.
이 프로젝트에는 API 라우트가 없으며, app.py에서 각 모듈의 함수를 호출하는 구조다.
