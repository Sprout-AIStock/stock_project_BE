from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv # 👈 1. 라이브러리 import
import os

# 👇 2. .env 파일을 명시적으로 로드하는 코드 추가
#    config.py 파일의 위치를 기준으로 상위 폴더(../)의 .env 파일을 찾습니다.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

class Settings(BaseSettings):
    # 이제 model_config는 필요 없지만, 호환성을 위해 남겨둡니다.
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding='utf-8', extra='ignore')

    DEEPSEARCH_API_KEY: str
    NCP_API_KEY: str
    NCP_APIGW_URL: str
    OPENAI_API_KEY: str
    FRED_API_KEY: str
    DATABASE_URL: str

settings = Settings()