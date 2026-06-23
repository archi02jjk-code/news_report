import streamlit as st
import feedparser
from datetime import datetime
import urllib.parse  # 👈 한글 키워드 변환을 위해 추가된 라이브러리

# 웹페이지 설정
st.set_page_config(page_title="AI & 데이터 뉴스 봇", page_icon="🤖", layout="wide")

st.title("🤖 매일 아침 AI & 데이터 분석 뉴스 요약 보고서")
st.caption("Google News RSS를 활용하여 실시간으로 뉴스를 수집하고 보고서를 생성합니다.")

# 뉴스 수집 함수
def get_news(keyword):
    # 👈 한글 검색어를 URL용 안전한 문자열로 인코딩 (예: "인공지능 AI" -> "%EC%9D%B8%EA%B3%B5...")
    encoded_keyword = urllib.parse.quote(keyword)
    
    # 구글 뉴스 검색 RSS URL (encoded_keyword 적용)
    url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    
    news_list = []
    # 최신 뉴스 5개만 가져오기
    for entry in feed.entries[:5]:
        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })
    return news_list

# 화면 레이아웃 분할 (좌측: AI / 우측: 데이터 분석)
col1, col2 = st.columns(2)

with col1:
    st.header("💡 인공지능(AI) 최신 뉴스")
    ai_news = get_news("인공지능 AI")
    for i, news in enumerate(ai_news):
        st.subheader(f"{i+1}. {news['title']}")
        st.write(f"📅 발행일: {news['published']}")
        st.markdown(f"[🔗 뉴스 기사 보러가기]({news['link']})")
        st.write("---")

with col2:
    st.header("📊 데이터 분석 최신 뉴스")
    data_news = get_news("데이터 분석")
    for i, news in enumerate(data_news):
        st.subheader(f"{i+1}. {news['title']}")
        st.write(f"📅 발행일: {news['published']}")
        st.markdown(f"[🔗 뉴스 기사 보러가기]({news['link']})")
        st.write("---")

# 사이드바에 업데이트 시간 표시
st.sidebar.header("⏰ 시스템 정보")
st.sidebar.write(f"마지막 동기화: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.info("이 대시보드는 실시간 피드를 사용하므로, 매일 아침 6시에 접속하시면 최신 보고서를 확인하실 수 있습니다.")
