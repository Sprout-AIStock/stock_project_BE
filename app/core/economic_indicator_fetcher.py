from fredapi import Fred
from app.config import settings

fred = Fred(api_key=settings.FRED_API_KEY)

def get_us_economic_indicators():
    """FRED API를 이용해 미국의 최신 주요 경제 지표를 가져옵니다."""
    try:
        # 미국 기준 금리 (Effective Federal Funds Rate), 가장 최신 값
        interest_rate_series = fred.get_series('DFF')
        latest_interest_rate = interest_rate_series.iloc[-1]

        # 미국 실질 GDP 성장률 (전분기 대비), 가장 최신 값
        gdp_growth_series = fred.get_series('A191RL1Q225SBEA')
        latest_gdp_growth = gdp_growth_series.iloc[-1]
        
        return {
            "current_us_interest_rate": f"{latest_interest_rate:.2f}%",
            "current_us_gdp_growth": f"{latest_gdp_growth:.2f}%"
        }
    except Exception as e:
        print(f"Error fetching from FRED API: {e}")
        return None