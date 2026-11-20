import matplotlib.pyplot as plt
import streamlit as st

from crawler import RSS_SOURCES, fetch_articles
from recommender import (
    CATEGORY_KEYWORDS,
    count_articles_by_keyword,
    filter_articles,
    get_keywords,
)
from storage import load_articles, load_keywords, save_articles, save_keywords


# 한글 제목과 축 이름이 깨지지 않도록 맑은 고딕을 사용한다.
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(page_title="Security Brief", page_icon="🛡️")


def get_article_tags(article, user_keywords):
    """기사 본문에서 분야와 키워드 태그를 찾는다."""
    title = str(article.get("title") or "")
    content = str(article.get("content") or "")
    searchable_text = (title + " " + content).lower()
    categories = []
    keywords = []
    user_keyword_matched = False

    for category in CATEGORY_KEYWORDS:
        category_matched = False
        for keyword in CATEGORY_KEYWORDS[category]:
            if keyword.lower() in searchable_text:
                category_matched = True

                duplicate = False
                for saved_keyword in keywords:
                    if saved_keyword.lower() == keyword.lower():
                        duplicate = True
                        break
                if not duplicate:
                    keywords.append(keyword)

        if category_matched:
            categories.append(category)

    for keyword in user_keywords:
        keyword = str(keyword).strip()
        if keyword and keyword.lower() in searchable_text:
            user_keyword_matched = True
            duplicate = False
            for saved_keyword in keywords:
                if saved_keyword.lower() == keyword.lower():
                    duplicate = True
                    break
            if not duplicate:
                keywords.append(keyword)

    if not categories:
        if user_keyword_matched:
            categories.append("사용자 키워드")
        else:
            categories.append("전체")

    return categories, keywords


if "articles" not in st.session_state:
    st.session_state.articles = load_articles()

if "keywords" not in st.session_state:
    st.session_state.keywords = load_keywords()

if "selected_link" not in st.session_state:
    st.session_state.selected_link = ""


# 출처 선택은 사이드바 위쪽에 두고, 수집 버튼은 상단 헤더에 둔다.
st.sidebar.header("RSS 출처")
source_names = []
for source_key in RSS_SOURCES:
    source_names.append(RSS_SOURCES[source_key]["name"])

selected_source_name = st.sidebar.selectbox(
    "수집할 출처를 선택하세요.",
    source_names,
)
selected_source_url = ""
for source_key in RSS_SOURCES:
    if RSS_SOURCES[source_key]["name"] == selected_source_name:
        selected_source_url = RSS_SOURCES[source_key]["url"]
        break


header_title, header_button = st.columns([6, 1.5])
with header_title:
    st.title("Security Brief")
    st.caption("개인 맞춤형 사이버 보안 뉴스 브리핑")
with header_button:
    collect_clicked = st.button("기사 수집", type="primary")

if collect_clicked:
    collected_articles = fetch_articles(
        selected_source_url,
        limit=10,
        source=selected_source_name,
    )
    if collected_articles:
        added_count = save_articles(collected_articles)
        st.session_state.articles = load_articles()
        st.success(
            f"{selected_source_name}에서 {len(collected_articles)}개를 수집했고, "
            f"{added_count}개를 새로 저장했습니다."
        )
    else:
        st.error("기사를 수집하지 못했습니다. RSS 주소와 인터넷 연결을 확인하세요.")


# 가로형 라디오 버튼으로 관심 분야를 탭처럼 보여 준다.
st.subheader("관심 분야")
category_options = ["전체"]
for category in CATEGORY_KEYWORDS:
    category_options.append(category)

selected_category = st.radio(
    "관심 분야를 선택하세요.",
    category_options,
    horizontal=True,
    label_visibility="collapsed",
)

selected_categories = []
if selected_category != "전체":
    selected_categories.append(selected_category)

articles = st.session_state.articles
user_keywords = st.session_state.keywords
filtered_articles = filter_articles(
    articles,
    selected_categories,
    user_keywords,
)


# 필터 결과가 바뀌면 목록의 첫 기사를 자동으로 선택한다.
filtered_links = []
for article in filtered_articles:
    filtered_links.append(article["link"])

if not filtered_articles:
    st.session_state.selected_link = ""
elif st.session_state.selected_link not in filtered_links:
    st.session_state.selected_link = filtered_articles[0]["link"]

selected_index = -1
selected_article = None
for index, article in enumerate(filtered_articles):
    if article["link"] == st.session_state.selected_link:
        selected_index = index
        selected_article = article
        break


# 좌측 사이드바의 기사 목록은 고정 높이 컨테이너 안에서 스크롤된다.
st.sidebar.divider()
st.sidebar.subheader("기사 목록")
st.sidebar.caption(f"현재 목록 {len(filtered_articles)}개")

if filtered_articles:
    with st.sidebar.container(height=520):
        for index, article in enumerate(filtered_articles):
            article_label = f"{index + 1:02d}. {article['title']}"
            button_key = f"article_select_{index}"

            if index == selected_index:
                clicked = st.button(
                    article_label,
                    key=button_key,
                    type="primary",
                )
            else:
                clicked = st.button(article_label, key=button_key)

            st.caption(article["source"])
            if clicked:
                st.session_state.selected_link = article["link"]
                st.rerun()
else:
    st.sidebar.info("조건에 맞는 기사가 없습니다.")


# 사용자 키워드 기능은 기사 목록 아래에 배치한다.
st.sidebar.divider()
st.sidebar.subheader("사용자 키워드")
new_keyword = st.sidebar.text_input("추가할 키워드")

if st.sidebar.button("키워드 추가"):
    new_keyword = new_keyword.strip()
    duplicated = False

    for keyword in st.session_state.keywords:
        if keyword.lower() == new_keyword.lower():
            duplicated = True
            break

    if not new_keyword:
        st.sidebar.warning("키워드를 입력하세요.")
    elif duplicated:
        st.sidebar.warning("이미 저장된 키워드입니다.")
    else:
        keywords = list(st.session_state.keywords)
        keywords.append(new_keyword)
        saved_keywords = save_keywords(keywords)
        if saved_keywords is None:
            st.sidebar.error("키워드를 저장하지 못했습니다.")
        else:
            st.session_state.keywords = saved_keywords
            st.sidebar.success("키워드를 저장했습니다.")
            st.rerun()

if st.session_state.keywords:
    keyword_to_delete = st.sidebar.selectbox(
        "삭제할 키워드",
        st.session_state.keywords,
    )
    if st.sidebar.button("키워드 삭제"):
        remaining_keywords = []
        for keyword in st.session_state.keywords:
            if keyword != keyword_to_delete:
                remaining_keywords.append(keyword)

        saved_keywords = save_keywords(remaining_keywords)
        if saved_keywords is None:
            st.sidebar.error("키워드를 삭제하지 못했습니다.")
        else:
            st.session_state.keywords = saved_keywords
            st.sidebar.success("키워드를 삭제했습니다.")
            st.rerun()
else:
    st.sidebar.info("저장된 사용자 키워드가 없습니다.")

st.sidebar.metric("전체 수집 기사 수", len(articles))


# 중앙에는 현재 선택한 기사만 넓은 카드 형태로 표시한다.
st.divider()
if selected_article is None:
    st.info("사이드바에서 기사를 선택하세요.")
else:
    article_categories, article_keywords = get_article_tags(
        selected_article,
        user_keywords,
    )

    with st.container(border=True):
        st.subheader(selected_article["title"])
        date_column, source_column, category_column = st.columns(3)
        date_column.caption(f"발행일: {selected_article['date']}")
        source_column.caption(f"출처: {selected_article['source']}")
        category_column.caption(f"분야: {' / '.join(article_categories)}")

        tag_text = ""
        for keyword in article_keywords:
            tag_text += f"`{keyword}` "
        if not tag_text:
            tag_text = "없음"
        st.markdown(f"**키워드 태그:** {tag_text}")

        st.write(selected_article["content"])
        st.markdown(f"[원문 보기]({selected_article['link']})")

    previous_column, count_column, next_column = st.columns([1, 3, 1])
    with previous_column:
        if st.button("← 이전 기사", disabled=selected_index <= 0):
            st.session_state.selected_link = filtered_articles[selected_index - 1]["link"]
            st.rerun()

    with count_column:
        st.caption(f"{selected_index + 1} / {len(filtered_articles)}")

    with next_column:
        if st.button(
            "다음 기사 →",
            disabled=selected_index >= len(filtered_articles) - 1,
        ):
            st.session_state.selected_link = filtered_articles[selected_index + 1]["link"]
            st.rerun()


# 하단은 통계와 학습 메모를 전환해서 보여 준다.
st.divider()
st.subheader("기사 통계 및 학습 메모")
bottom_mode = st.radio(
    "하단 영역을 선택하세요.",
    ["기사 통계", "학습 메모"],
    horizontal=True,
    label_visibility="collapsed",
)

if bottom_mode == "기사 통계":
    statistics_column, collection_column = st.columns([2, 1])

    all_keywords = get_keywords(list(CATEGORY_KEYWORDS), user_keywords)
    keyword_counts = count_articles_by_keyword(articles, all_keywords)
    has_matched_keyword = False
    max_count = 0

    for keyword in keyword_counts:
        if keyword_counts[keyword] > 0:
            has_matched_keyword = True
        if keyword_counts[keyword] > max_count:
            max_count = keyword_counts[keyword]

    with statistics_column:
        st.markdown("#### 키워드별 기사 수")
        if has_matched_keyword:
            figure, axis = plt.subplots(figsize=(10, 4))
            axis.bar(list(keyword_counts.keys()), list(keyword_counts.values()))
            axis.set_ylabel("기사 수")
            axis.tick_params(axis="x", rotation=45)
            axis.set_ylim(0, max_count + 1)
            axis.set_yticks(range(0, max_count + 1))
            figure.tight_layout()
            st.pyplot(figure)
            plt.close(figure)
        else:
            st.info("키워드와 일치하는 기사가 없어 그래프를 표시하지 않습니다.")

    with collection_column:
        st.markdown("#### 수집 현황")
        st.metric("전체 기사", len(articles))
        st.metric("현재 분야 기사", len(filtered_articles))
        st.metric("현재 수집 출처", selected_source_name)
else:
    st.text_area(
        "학습 메모",
        key="learning_memo",
        height=360,
        placeholder="기사에서 새롭게 알게 된 내용을 자유롭게 기록하세요.",
    )
