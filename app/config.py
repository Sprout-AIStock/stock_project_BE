# API 키, 설정값 등 민감하거나 변경될 수 있는 정보를 관리합니다.
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding='utf-8')

    DEEPSEARCH_API_KEY: str
    NCP_API_KEY: str
    NCP_APIGW_URL: str
    OPENAI_API_KEY: str

settings = Settings()