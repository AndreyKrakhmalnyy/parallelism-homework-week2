from typing import Optional
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BOOKING_TTL_MINUTES = 15

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
    
class PaymentAPIConfig(BaseModel):
    port: int
    base_url: str
    timeout: float
    retry_count: int

class ProtectionAPIConfig(BaseModel):
    port: int
    base_url: str
    timeout: float
    retry_count: int

class ConnectorsConfig(BaseModel):
    payment: PaymentAPIConfig
    protection: ProtectionAPIConfig

class RedisConfig(BaseModel):
    port: int
    host: str
    password: Optional[SecretStr] = None
    database: int = 0

    @property
    def url(self):
        if self.password is None:
            return f"redis://{self.host}:{self.port}/{self.database}"
        
        password = self.password.get_secret_value()
        return f"redis://{password}@{self.host}:{self.port}/{self.database}"


class Settings(BaseSettings):
    app: AppConfig
    postgres: PostgresConfig
    connectors: ConnectorsConfig
    redis: RedisConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

settings = Settings()