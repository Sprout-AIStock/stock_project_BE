# app/core/insight_generator.py
import os
import uuid
import openai
from app.config import settings

# --- API 클라이언트 설정 ---
# 1. HyperCLOVA X 클라이언트
clova_client = openai.OpenAI(
    api_key=settings.NCP_API_KEY,
    base_url=settings.NCP_APIGW_URL
)

# 2. OpenAI GPT 클라이언트
gpt_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


# --- 1단계: HyperCLOVA X로 빠른 인사이트 생성 ---
def get_clova_insight(stock_name: str) -> str:
    """HyperCLOVA X를 이용해 신속한 1차 결론(매수/매도/중립)을 도출합니다."""
    prompt = f"""
    당신은 퀀트 분석가입니다. 아래 경제 지표가 '{stock_name}' 종목에 미칠 영향을 분석하여, 최종 투자 의견을 "매수", "매도", "중립" 중 하나로만 결론내려주세요.
    [경제 지표]
    - 미국 기준 금리: 5.50%
    - 원/달러 환율: 1,380원
    """
    try:
        response = clova_client.chat.completions.create(
            model="HCX-003",  # 실제 사용하는 모델 ID로 변경
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"CLOVA Insight Error: {e}")
        return "분석 오류"

# --- 2단계: GPT로 심층 보고서 생성 ---
def get_gpt_report(stock_name: str, clova_conclusion: str) -> str:
    """GPT를 이용해 과거 사례와 비교 분석하는 심층 보고서를 작성합니다."""
    prompt = f"""
    당신은 30년 경력의 베테랑 애널리스트입니다. '{stock_name}' 종목에 대한 1차 분석 결과는 '{clova_conclusion}'입니다.

    [작성 지침]
    1. 이 결론을 뒷받침하는 현재 거시 경제 지표(금리, 환율 등)를 분석합니다.
    2. 과거에 유사한 경제 상황(예: 2022년 금리인상기)이 있었는지 찾아보고, 당시 '{stock_name}'의 주가 흐름과 현재 상황의 다른 점을 비교 분석해주세요.
    3. 모든 내용을 종합하여, 전문적이지만 이해하기 쉬운 최종 투자 보고서를 500자 내외로 작성해주세요.
    """
    try:
        response = gpt_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"GPT Report Error: {e}")
        return "보고서 생성 중 오류가 발생했습니다."

# --- 보고서 파일 저장 ---
def save_report_to_file(report_text: str) -> str:
    """생성된 보고서 텍스트를 고유한 ID를 가진 파일로 저장합니다."""
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    report_id = str(uuid.uuid4())
    file_path = os.path.join(reports_dir, f"{report_id}.txt")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    return report_id

# --- 3단계: 문서 기반 챗봇 응답 생성 ---
def query_document_chatbot(report_id: str, user_question: str) -> str:
    """저장된 보고서 파일을 기반으로 사용자의 질문에 답변합니다."""
    file_path = f"reports/{report_id}.txt"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            document_content = f.read()
    except FileNotFoundError:
        return "죄송합니다. 해당 보고서를 찾을 수 없습니다."

    prompt = f"""
    당신은 아래 [문서]의 내용을 완벽하게 이해한 AI 비서입니다. 사용자의 [질문]에 대해 [문서]의 내용만을 근거로 친절하게 답변해주세요.
    
    [문서]
    {document_content}
    
    [질문]
    {user_question}
    """
    try:
        response = clova_client.chat.completions.create(
            model="HCX-003", # 실제 사용하는 모델 ID로 변경
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Chatbot Error: {e}")
        return "답변 생성 중 오류가 발생했습니다."