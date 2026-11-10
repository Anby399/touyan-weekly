"""应用配置；只读取配置，不连接外部服务或创建目录。"""

from functools import lru_cache
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        hide_input_in_errors=True,
    )

    app_name: str = "touyan"
    app_env: Literal["development", "production"] = "development"
    app_host: str = "127.0.0.1"
    app_port: int = Field(default=8000, ge=1, le=65535)
    app_timezone: str = "Asia/Shanghai"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    openai_api_key: SecretStr = SecretStr("")
    openai_base_url: str = "https://api.openai.com/v1"
    llm_model: str = ""
    llm_temperature: float = Field(default=0.2, ge=0, le=2)
    llm_timeout_seconds: int = Field(default=120, gt=0)
    llm_max_retries: int = Field(default=2, ge=0)
    embedding_api_key: SecretStr = SecretStr("")
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = ""
    embedding_dimensions: int = Field(default=1536, gt=0)
    embedding_batch_size: int = Field(default=32, gt=0)

    tavily_api_key: SecretStr = SecretStr("")
    tavily_search_depth: Literal["basic", "advanced"] = "basic"
    tavily_max_results: int = Field(default=10, ge=1, le=20)
    http_timeout_seconds: int = Field(default=30, gt=0)

    mysql_host: str = "127.0.0.1"
    mysql_port: int = Field(default=3306, ge=1, le=65535)
    mysql_database: str = "touyan"
    mysql_user: str = "touyan"
    mysql_password: SecretStr = SecretStr("")
    mysql_charset: str = "utf8mb4"
    mysql_connect_timeout_seconds: int = Field(default=10, gt=0)
    milvus_uri: str = "http://127.0.0.1:19530"
    milvus_token: SecretStr = SecretStr("")
    milvus_database: str = "default"
    milvus_collection: str = "report_chunks"
    milvus_timeout_seconds: int = Field(default=30, gt=0)

    chunk_size: int = Field(default=1200, gt=0)
    chunk_overlap: int = Field(default=200, ge=0)
    retrieval_candidate_k: int = Field(default=30, gt=0)
    retrieval_top_k: int = Field(default=8, gt=0)

    worker_poll_seconds: float = Field(default=2, gt=0)
    worker_concurrency: int = Field(default=1, gt=0)
    worker_heartbeat_seconds: int = Field(default=15, gt=0)
    worker_lease_seconds: int = Field(default=120, gt=0)
    job_max_attempts: int = Field(default=3, gt=0)
    stage_timeout_seconds: int = Field(default=900, gt=0)
    agent_recursion_limit: int = Field(default=40, gt=0)
    fact_check_max_revisions: int = Field(default=2, ge=0)

    mcp_transport: Literal["streamable-http"] = "streamable-http"
    mcp_research_path: str = "/mcp/research"
    mcp_report_path: str = "/mcp/reports"
    mcp_research_url: str = "http://127.0.0.1:8000/mcp/research"
    mcp_access_token: SecretStr = SecretStr("")
    mcp_timeout_seconds: int = Field(default=120, gt=0)
    sse_heartbeat_seconds: int = Field(default=15, gt=0)

    data_dir: Path = PROJECT_ROOT / "data"
    max_upload_mb: int = Field(default=50, gt=0)
    pdf_ocr_enabled: bool = False
    pdf_ocr_language: str = "chi_sim+eng"
    libreoffice_binary: str = "soffice"
    export_timeout_seconds: int = Field(default=120, gt=0)

    @field_validator("data_dir", mode="before")
    @classmethod
    def resolve_data_dir(cls, value: str | Path) -> Path:
        path = Path(value).expanduser()
        return (path if path.is_absolute() else PROJECT_ROOT / path).resolve()

    @field_validator("app_timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("APP_TIMEZONE 必须是有效的 IANA 时区") from exc
        return value

    @model_validator(mode="after")
    def validate_related_settings(self) -> "Settings":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP 必须小于 CHUNK_SIZE")
        if self.retrieval_top_k > self.retrieval_candidate_k:
            raise ValueError("RETRIEVAL_TOP_K 不能大于 RETRIEVAL_CANDIDATE_K")
        if self.worker_heartbeat_seconds >= self.worker_lease_seconds:
            raise ValueError("WORKER_HEARTBEAT_SECONDS 必须小于 WORKER_LEASE_SECONDS")
        if self.mcp_research_path == self.mcp_report_path:
            raise ValueError("两个 MCP 服务不能使用相同路径")
        for path in (self.mcp_research_path, self.mcp_report_path):
            if not path.startswith("/"):
                raise ValueError("MCP 挂载路径必须以 / 开头")
        return self

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def exports_dir(self) -> Path:
        return self.data_dir / "exports"


@lru_cache
def get_settings() -> Settings:
    """按需加载配置；环境变量优先于项目根目录 .env。"""
    return Settings()
