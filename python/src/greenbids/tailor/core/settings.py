import datetime
import urllib.parse

import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="GREENBIDS_TAILOR_")

    index_url: str = "http://localhost"
    """URL of the Greenbids models repository"""
    api_user: str = "nobody"
    """Username used for authentication against Greenbids infrastructure"""
    api_key: str = ""
    """Password used for authentication against Greenbids infrastructure"""
    gb_model_refresh_seconds: int = pydantic.Field(
        default=3600, alias="GREENBIDS_TAILOR_MODEL_REFRESH_SECONDS"
    )
    """Period between two model refresh check"""

    @property
    def authenticated_index_url(self) -> urllib.parse.SplitResult:
        index_url = urllib.parse.urlsplit(self.index_url)
        netloc = index_url.netloc.split("@")[-1]
        return index_url._replace(netloc=f"{self.api_user}:{self.api_key}@{netloc}")

    @property
    def gb_model_refresh_period(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=float(self.gb_model_refresh_seconds))


settings = Settings()
