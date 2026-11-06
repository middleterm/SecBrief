import streamlit as st

from crawler import RSS_SOURCES, fetch_articles
from recommender import CATEGORY_KEYWORDS, filter_articles
from summarizer import summarize_article


st.set_page_config(
    page_title="SecBrief",
    page_icon="🛡️",
)

st.title("SecBrief — 개인 맞춤형 AI 사이버보안 신문")
st.caption("KISA 보안 RSS에서 관심 분야의 최신 기사를 확인하세요.")

selected_categories = st.multiselect(
    "관심 분야",
    options=list(CATEGORY_KEYWORDS),
    default=list(CATEGORY_KEYWORDS),
)

if "articles" not in st.session_state:
    st.session_state.articles = None

if st.button("기사 불러오기", type="primary"):
    st.session_state.articles = fetch_articles(RSS_SOURCES["1"]["url"], limit=10)

articles = st.session_state.articles
if articles is None:
    st.info("관심 분야를 선택한 뒤 ‘기사 불러오기’를 눌러주세요.")
    st.stop()

if not articles:
    st.error("기사를 불러오지 못했습니다. RSS 주소 또는 인터넷 연결을 확인해주세요.")
    st.stop()

if len(articles) < 10:
    st.warning(f"현재 {len(articles)}개의 기사만 확인됩니다.")

filtered_articles = filter_articles(articles, selected_categories)
if not filtered_articles:
    st.info("선택한 분야의 기사가 없습니다.")
    st.stop()

for article in filtered_articles:
    st.subheader(article["title"])
    st.caption(f"발행일: {article['date']}")

    with st.spinner("AI가 3줄 요약을 만드는 중입니다..."):
        summary = summarize_article(article)

    if summary.startswith(("API 키가 없어", "요약을 생성하지", "요약 형식이")):
        st.warning(summary)
    else:
        st.markdown(summary)

    st.markdown(f"[원문 보기]({article['link']})")
    st.divider()
