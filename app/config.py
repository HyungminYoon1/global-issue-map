from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "global_issue_map"
    openai_api_key: str = ""
    newsdata_api_key: str = ""
    gnews_api_key: str = ""
    currents_api_key: str = ""


settings = Settings()
