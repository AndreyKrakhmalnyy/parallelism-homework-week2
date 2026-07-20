<<<<<<< Updated upstream
DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:7432/postgres"
REDIS_URL = "redis://localhost:7379/0"
PAYMENT_API_URL = "http://localhost:9001"
PROTECTION_API_URL = "http://localhost:9002"
=======
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


>>>>>>> Stashed changes
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
    url: str
    endpoint_url: str

class ProtectionAPIConfig(BaseModel):
    port: int
    url: str
    endpoint_url: str

class Settings(BaseSettings):
    app: AppConfig
    postgres: PostgresConfig
    payment_api: PaymentAPIConfig
    protection_api: ProtectionAPIConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

settings = Settings()