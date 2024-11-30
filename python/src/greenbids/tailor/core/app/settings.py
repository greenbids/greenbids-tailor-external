import functools
import pydantic
import pydantic_settings


class SupportSettings(pydantic_settings.BaseSettings):
    log_level: str = "ERROR"
    count: int = 30


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="GREENBIDS_TAILOR_")

    index_url: str = ""
    api_user: str = "nobody"
    api_key: str = ""
    gb_model_name: str = pydantic.Field(default="None", alias="model_name")
    gb_model_refresh_seconds: float = pydantic.Field(
        default=-1, alias="model_refresh_seconds"
    )
    download_disabled: bool = False
    profile: str = ""
    support: SupportSettings = pydantic.Field(default_factory=SupportSettings)


@functools.lru_cache(1)
def get_settings() -> Settings:
    return Settings()
