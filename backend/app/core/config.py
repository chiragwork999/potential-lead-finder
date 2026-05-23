from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = "Potential Lead Finder API"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/potential_leads"
    redis_url: str = "redis://localhost:6379/0"
    enable_scheduler: bool = False

    grok_api_key: str = ""
    grok_base_url: str = "https://api.x.ai/v1"
    grok_model: str = "grok-3-mini"


settings = Settings()
