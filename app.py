import streamlit as st
import feedparser
from datetime import datetime
import urllib.parse
from google import genai  # 👈 구글 공식 Gemini 라이브러리

# 웹페이지 기본 설정
st.set_page_config(page_title="AI & 데이터 뉴스 분석 봇", page_icon="🤖", layout="wide")

st.title("🤖 매일 아침 AI & 데이터 분석 뉴스 요약 보고서")
st.caption("Google News RSS와 Google Gemini API를 활용하여 무료로 실시간 뉴스를 분석합니다.")

# 사이드바 설정 (API 키 입력창 및 안내)
st.sidebar.header("🔑 Google API 설정")
gemini_api_key = st.sidebar.text_input("Gemini API Key를 입력하세요", type="password")
st.sidebar.markdown(
    "[Google AI Studio](https://aistudio.google.com/)에서 무료로 키를 발급받아 붙여넣으시면 시스템이 작동합니다."
)

st.sidebar.write("---")
st.sidebar.header("⏰ 시스템 정보")
st.sidebar.write(f"마지막 동기화: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.info("분당 약 15회 요청까지 완전 무료로 사용할 수 있는 Free Tier 기반 대시보드입니다.")

# Gemini AI 분석 함수
def analyze_news(title, raw_summary, api_key):
    # API 키가 입력되지 않았을 때 안내문 출력
    if not api_key:
        return "⚠️ 사이드바에 Gemini API Key를 입력하시면 요약이 생성됩니다.", "⚠️ API Key를 입력하시면 시사점이 생성됩니다."
    
    try:
        # 최신 구글 API 클라이언트 초기화
        client = genai.Client(api_key=api_key)
        
        # AI에게 전달할 프롬프트 구성
        prompt = f"""
        당신은 IT 및 빅데이터 분야 전문 수석 애널리스트입니다. 
        아래 뉴스 기사의 제목과 내용을 바탕으로 핵심을 파악하여 일반 대중과 실무자가 읽기 쉽게 분석해 주세요.

        기사 제목: {title}
        기사 요약 내용: {raw_summary}

        출력 형식은 반드시 아래 형식을 엄격히 지켜주세요. 대괄호 명칭 변경 금지:
        [요약]: (기사의 핵심 사건과 사실 관계를 2~3문장으로 명확하게 요약)
        [시사점]: (이 뉴스가 관련 시장, 기술 트렌드, 혹은 실무자에게 주는 의미나 시사점을 2~3문장으로 날카롭게 분석)
        """
        
        # 완전 무료 제공되는 가성비 최고 속도 모델(gemini-2.5-flash) 호출
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        result = response.text
        
        # AI가 준 답변에서 [요약]과 [시사점] 파트를 잘라내어 추출
        ai_summary = result.split("[요약]:")[1].split("[시사점]:")[0].strip()
        ai_insight = result.split("[시사점]:")[1].strip()
        
        return ai_summary, ai_insight
    except Exception as e:
        # 파싱 오류나 API 제한 도달 시 예외 처리
        return f"요약 생성 실패 (오류 혹은 키 확인 필요)", "시사점 분석 실패"

# 구글 RSS 뉴스 수집 함수
def get_news(keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    
    news_list = []
    # API 호출 한도 및 화면 밸런스를 위해 섹션당 최신 뉴스 3개씩만 수집
    for entry in feed.entries[:3]:
        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "raw_summary": entry.get("summary", "")
        })
    return news_list

# 대시보드 화면 2열 레이아웃 배치
col1, col2 = st.columns(2)

with col1:
    st.header("💡 인공지능(AI) 최신 뉴스")
    ai_news = get_news("인공지능 AI")
    
    for i, news in enumerate(ai_news):
        # AI 연동 연산이 수행되는 동안 로딩 스피너 작동
        with st.spinner(f"AI가 {i+1}번 기사 문맥 분석 중..."):
            ai_summary, ai_insight = analyze_news(news['title'], news['raw_summary'], gemini_api_key)
        
        # 사용자가 요청한 [1, 2, 3, 4] 정렬 포맷 출력
        st.markdown(f"### 기사 {i+1}")
        st.markdown(f"**1. 제목:** {news['title']}")
        st.markdown(f"**2. 요약:** {ai_summary}")
        st.markdown(f"**3. 시사점:** {ai_insight}")
        st.markdown(f"**4. 링크:** [🔗 뉴스 기사 보러가기]({news['link']})")
        st.write("---")

with col2:
    st.header("📊 데이터 분석 최신 뉴스")
    data_news = get_news("데이터 분석")
    
    for i, news in enumerate(data_news):
        with st.spinner(f"AI가 {i+1}번 기사 문맥 분석 중..."):
            ai_summary, ai_insight = analyze_news(news['title'], news['raw_summary'], gemini_api_key)
            
        st.markdown(f"### 기사 {i+1}")
        st.markdown(f"**1. 제목:** {news['title']}")
        st.markdown(f"**2. 요약:** {ai_summary}")
        st.markdown(f"**3. 시사점:** {ai_insight}")
        st.markdown(f"**4. 링크:** [🔗 뉴스 기사 보러가기]({news['link']})")
        st.write("---")
