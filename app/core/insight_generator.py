import os
import uuid
import openai
from app.config import settings
from app.services.scheduler import indicator_cache

# --- API 클라이언트 설정 ---
clova_client = openai.OpenAI(
    api_key=settings.NCP_API_KEY,
    base_url=settings.NCP_APIGW_URL
)
gpt_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

# --- 1단계: HyperCLOVA X로 빠른 인사이트 생성 ---
def get_clova_insight(stock_name: str) -> tuple[str, str]:
    """
    매일 업데이트되는 실시간 경제지표를 바탕으로
    HyperCLOVA X로부터 신속한 1차 결론 및 근거를 도출합니다.
    """
    economic_data = indicator_cache

    prompt = f"""
    당신은 아래의 [분석 프레임워크]에 따라 시장을 해석하는 숙련된 매크로 전략가입니다.

    [분석 프레임워크]
    1. 기본 전제: 현재 미국 행정부(트럼프)는 중국 견제를 위해 글로벌 관세 정책을 활용하며, 우방국과는 협상을 통해 관세를 조율한다.
    2. 금리-무역 관계: 기준 금리가 인하되면 미국이 경제적 부담을 덜게 되어, 우방국과의 관세 협상을 철회하고 다시 압박할 가능성이 높아진다.
    3. 시장 트리거:
       - 소규모 금리 인하(0.25%p): 단기적인 호재로 작용할 수 있다.
       - 대규모 금리 인하('빅컷'): 시장은 경기 침체의 신호로 해석하고, 무역 갈등 재점화 리스크까지 겹쳐 하락의 핵심 트리거가 될 확률이 매우 높다.
    4. 현재 시장 상태: 높은 금리에도 불구하고 성장률이 높아 미국 증시와 암호화폐 시장은 강세를 보이지만, 금리 인하 시그널이 나타나면 즉시 경계해야 하는 구간이다.

    [최신 경제 동향]
    - 미국 기준 금리: {economic_data.get('current_us_interest_rate', 'N/A')}
    - 미국 GDP 성장률: {economic_data.get('current_us_gdp_growth', 'N/A')}
    - 최신 무역 정책 동향: {economic_data.get('latest_trade_policy', 'N/A')}
    - 분석 대상 종목: {stock_name}

    [임무]
    위 [분석 프레임워크]와 [최신 경제 동향]을 바탕으로 '{stock_name}' 종목에 대한 투자 의견과 핵심 근거를 아래 형식에 맞춰 한 줄로만 출력해줘.

    형식: 결론: [매수/매도/중립], 근거: [핵심 근거 한 문장]
    """
    try:
        response = clova_client.chat.completions.create(
            model="HCX-003",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.3
        )
        result_text = response.choices[0].message.content.strip()
        
        parts = result_text.split(', 근거:')
        conclusion = parts[0].replace('결론:', '').strip()
        reason = parts[1].strip() if len(parts) > 1 else "근거를 찾을 수 없습니다."
        
        return conclusion, reason

    except Exception as e:
        print(f"CLOVA Insight Error: {e}")
        return "분석 오류", "오류로 인해 근거를 생성할 수 없습니다."

# --- 2단계: GPT로 심층 보고서 생성 ---
def get_gpt_report(stock_name: str, clova_conclusion: str, clova_reason: str) -> str:
    """GPT를 이용해 과거 사례와 비교 분석하는 심층 보고서를 작성합니다."""
    prompt = f"""
    당신은 30년 경력의 베테랑 애널리스트입니다. '{stock_name}' 종목에 대한 1차 분석 결과는 다음과 같습니다.
    - 결론: '{clova_conclusion}'
    - 핵심 근거: '{clova_reason}'

    [작성 지침]
    1. 위 1차 분석 결과를 뒷받침하는 현재 거시 경제 지표(금리, 환율 등)를 상세히 분석합니다.
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
            model="HCX-003",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Chatbot Error: {e}")
        return "답변 생성 중 오류가 발생했습니다."