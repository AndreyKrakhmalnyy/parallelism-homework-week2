from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    host: str
    port: int

class PostgresConfig(BaseModel):
    host: str
    port: int
    user: str
    password: SecretStr
    db: str
    echo: bool = True
    pool_size: int
    max_overflow: int
    pool_pre_ping: bool

    @property
    def url(self) -> str:
        return (
            f"postgresql+psycopg://{self.user}:"
            f"{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.db}"
        )
    
class Settings(BaseSettings):
    app: AppConfig
    postgres: PostgresConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="forbid"
    )

settings = Settings()