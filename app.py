import streamlit as st
import feedparser
from datetime import datetime
import urllib.parse
import re  # 👈 형식을 유연하게 파싱하기 위해 정규식 라이브러리 추가
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

# Gemini AI 분석 함수 (에러 방지 로직 강화)
def analyze_news(title, raw_summary, api_key):
    if not api_key:
        return "⚠️ 사이드바에 Gemini API Key를 입력하시면 요약이 생성됩니다.", "⚠️ API Key를 입력하시면 시사점이 생성됩니다."
    
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        당신은 IT 및 빅데이터 분야 전문 수석 애널리스트입니다. 
        아래 뉴스 기사의 제목과 내용을 바탕으로 핵심을 파악하여 일반 대중과 실무자가 읽기 쉽게 분석해 주세요.

        기사 제목: {title}
        기사 요약 내용: {raw_summary}

        출력 형식은 반드시 아래 형식을 엄격히 지켜주세요. 대괄호 명칭 변경 금지:
        [요약]: (기사의 핵심 사건과 사실 관계를 2~3문장으로 명확하게 요약)
        [시사점]: (이 뉴스가 관련 시장, 기술 트렌드, 혹은 실무자에게 주는 의미나 시사점을 2~3문장으로 날카롭게 분석)
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
        )
        
        result = response.text
        
        # 💡 안전한 파싱 기법 도입: split 대신 정규식을 사용하여 대괄호나 마크다운 형태를 모두 잡아냅니다.
        summary_match = re.search(r'(?:\[요약\]:|요약:|\*\*요약\*\*:?)(.*?)(?=(?:\[시사점\]:|시사점:|\*\*시사점\*\*:?)|$)', result, re.DOTALL)
        insight_match = re.search(r'(?:\[시사점\]:|시사점:|\*\*시사점\*\*:?)(.*)', result, re.DOTALL)
        
        # 매칭 성공 시 공백을 제거하고 가져옴, 실패 시 전체 답변을 나누어 담음
        ai_summary = summary_match.group(1).strip() if summary_match else ""
        ai_insight = insight_match.group(1).strip() if insight_match else ""
        
        # 정규식 파싱마저 실패한 완전 비상 상황인 경우 예외를 띄우지 않고 AI 전체 답변을 가공해 노출
        if not ai_summary and not ai_insight:
            ai_summary = result[:len(result)//2]
            ai_insight = result[len(result)//2:]
            
        return ai_summary, ai_insight
        
    except Exception as e:
        # 실제 어떤 에러가 나는지 디버깅하기 쉽도록 시스템 에러 메시지(str(e)) 노출로 변경
        return f"요약 생성 실패 ({str(e)})", "시사점 분석 실패"

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

# 대시보드 화면 레이아웃 배치
col1, col2 = st.columns(2)

with col1:
    st.header("💡 인공지능(AI) 최신 뉴스")
    ai_news = get_news("인공지능 AI")
    
    for i, news in enumerate(ai_news):
        with st.spinner(f"AI가 {i+1}번 기사 문맥 분석 중..."):
            ai_summary, ai_insight = analyze_news(news['title'], news['raw_summary'], gemini_api_key)
        
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
