import streamlit as st
import feedparser
from datetime import datetime
import urllib.parse
import re
from google import genai

# 웹페이지 기본 설정
st.set_page_config(page_title="AI & 데이터 뉴스 분석 봇", page_icon="🤖", layout="wide")

st.title("🤖 매일 아침 AI & 데이터 분석 뉴스 요약 보고서")
st.caption("Google News RSS와 Google Gemini API를 활용하여 무료로 실시간 뉴스를 분석합니다.")

# 사이드바 설정
st.sidebar.header("🔑 Google API 설정")
gemini_api_key = st.sidebar.text_input("Gemini API Key를 입력하세요", type="password")
st.sidebar.markdown(
    "[Google AI Studio](https://aistudio.google.com/)에서 무료로 키를 발급받아 붙여넣으시면 시스템이 작동합니다."
)

st.sidebar.write("---")
st.sidebar.header("⏰ 시스템 정보")
st.sidebar.write(f"마지막 동기화: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 단일 항목(요약 또는 시사점)을 개별 요청하는 안정화된 AI 함수
def ask_gemini(title, raw_summary, mission_prompt, api_key):
    if not api_key:
        return "⚠️ 사이드바에 API Key를 입력해주세요."
    
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        당신은 IT 및 빅데이터 분야 전문 수석 애널리스트입니다.
        아래 기사의 제목과 요약 내용을 바탕으로 지시사항을 수행해 주세요.

        기사 제목: {title}
        기사 내용: {raw_summary}

        지시사항: {mission_prompt}
        답변은 다른 군더더기 말(예: "네, 요약해드리겠습니다" 등) 없이 딱 지시사항에 대한 결과만 깔끔하게 출력하세요.
        """
        
        # 서버 부하를 줄이기 위해 텍스트 전용 최적화 모델 사용
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
        )
        return response.text.strip()
        
    except Exception as e:
        # 503 에러 발생 시 시스템 장애 메시지를 그대로 리턴하여 화면에 개별 표시되도록 함
        return f"실패 ({str(e)})"

# 구글 RSS 뉴스 수집 함수
def get_news(keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    
    news_list = []
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
        # ⚠️ PDF 요구사항: 기사 번호와 제목을 대제목 형태로 먼저 배치
        st.markdown(f"### {news['title']}")
        
        # 각 항목별 독립적 AI 호출로 503 에러 발생 시 해당 칸만 에러 메시지가 나오도록 격리
        with st.spinner(f"AI가 요약문 생성 중..."):
            summary_prompt = "이 기사의 핵심 사건과 사실 관계를 2~3문장으로 명확하게 요약해줘."
            ai_summary = ask_gemini(news['title'], news['raw_summary'], summary_prompt, gemini_api_key)
            
        with st.spinner(f"AI가 시사점 분석 중..."):
            insight_prompt = "이 뉴스가 관련 시장, 기술 트렌드, 혹은 실무자에게 주는 의미나 시사점을 2~3문장으로 날카롭게 분석해줘."
            ai_insight = ask_gemini(news['title'], news['raw_summary'], insight_prompt, gemini_api_key)
            
        # ⚠️ PDF 요구사항에 맞춤 포맷 출력 (1. 요약 / 2. 시사점 / 링크)
        if "실패" in ai_summary:
            st.markdown(f"**1. 요약:** 요약 생성 {ai_summary}")
        else:
            st.markdown(f"**1. 요약:** {ai_summary}")
            
        if "실패" in ai_insight:
            st.markdown(f"**2. 시사점:** 시사점 분석 실패")
        else:
            st.markdown(f"**2. 시사점:** {ai_insight}")
            
        st.markdown(f"[🔗 뉴스 기사 보러가기]({news['link']})")
        st.write("---")

with col2:
    st.header("📊 데이터 분석 최신 뉴스")
    data_news = get_news("데이터 분석")
    
    for i, news in enumerate(data_news):
        # ⚠️ PDF 요구사항: 기사 번호와 제목을 대제목 형태로 먼저 배치
        st.markdown(f"### {news['title']}")
        
        with st.spinner(f"AI가 요약문 생성 중..."):
            summary_prompt = "이 기사의 핵심 사건과 사실 관계를 2~3문장으로 명확하게 요약해줘."
            ai_summary = ask_gemini(news['title'], news['raw_summary'], summary_prompt, gemini_api_key)
            
        with st.spinner(f"AI가 시사점 분석 중..."):
            insight_prompt = "이 뉴스가 관련 시장, 기술 트렌드, 혹은 실무자에게 주는 의미나 시사점을 2~3문장으로 날카롭게 분석해줘."
            ai_insight = ask_gemini(news['title'], news['raw_summary'], insight_prompt, gemini_api_key)
            
        # ⚠️ PDF 요구사항에 맞춤 포맷 출력 (1. 요약 / 2. 시사점 / 링크)
        if "실패" in ai_summary:
            st.markdown(f"**1. 요약:** 요약 생성 {ai_summary}")
        else:
            st.markdown(f"**1. 요약:** {ai_summary}")
            
        if "실패" in ai_insight:
            st.markdown(f"**2. 시사점:** 시사점 분석 실패")
        else:
            st.markdown(f"**2. 시사점:** {ai_insight}")
            
        st.markdown(f"[🔗 뉴스 기사 보러가기]({news['link']})")
        st.write("---")
