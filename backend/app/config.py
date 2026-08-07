"""
Centralized application settings, loaded from environment variables (.env).
Keeping all provider/integration config here is what lets the LLM Gateway and
Integration Service stay decoupled from any single vendor (see Master Spec §8, §11).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "change-me"

    database_url: str = "sqlite:///./nava.db"

    # LLM Gateway
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    # Integrations
    salesforce_client_id: str = ""
    salesforce_client_secret: str = ""
    salesforce_username: str = ""
    salesforce_password: str = ""
    salesforce_domain: str = "login"

    heyreach_api_key: str = ""
    heyreach_base_url: str = "https://api.heyreach.io/api/public"


settings = Settings()
