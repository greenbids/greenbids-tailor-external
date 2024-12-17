import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="GREENBIDS_TAILOR_")

    prediction_cache_size: int = pydantic.Field(default=1000, gt=0)
    prediction_cache_ttl_seconds: float = pydantic.Field(default=60.0, gt=0)


SETTINGS = Settings()
