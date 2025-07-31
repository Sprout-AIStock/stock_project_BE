from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding='utf-8')

    # .env 파일에 정의된 모든 변수 목록
    DEEPSEARCH_API_KEY: str
    NCP_API_KEY: str
    NCP_APIGW_URL: str
    OPENAI_API_KEY: str
    FRED_API_KEY: str
    DATABASE_URL: str

settings = Settings()