"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Service Health Monitor"
    debug: bool = False

    # Health check settings
    check_interval_seconds: int = 60
    request_timeout_seconds: int = 10

    # Services to monitor (format: "name=url,name2=url2")
    services_config: str = "github=https://api.github.com,google=https://www.google.com"

    @property
    def services(self) -> dict[str, str]:
        """Parse services config string into dictionary."""
        result: dict[str, str] = {}
        if not self.services_config:
            return result
        for item in self.services_config.split(","):
            if "=" in item:
                name, url = item.split("=", 1)
                result[name.strip()] = url.strip()
        return result

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
