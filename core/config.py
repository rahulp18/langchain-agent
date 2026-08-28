from pydantic_settings import BaseSettings,SettingsConfigDict
from pathlib import Path
from pydantic import SecretStr,PostgresDsn
from functools import lru_cache


@lru_cache(maxsize=1)
def get_settings()->Settings:
  return Settings()

DEFAULT_POSTGRES_PORT=5432

PROJECT_ROOT=Path(__file__).resolve().parent.parent

def _with_schema(dsn:PostgresDsn,scheme:str)->str:
  hosts=[
           {**host, "port": host.get("port") or DEFAULT_POSTGRES_PORT}
        for host in dsn.hosts()
  ]
  return str(
    PostgresDsn.build(
      scheme=scheme,
      hosts=hosts,
      path=(dsn.path or "").lstrip("/"),
      query=dsn.query
    )
  )

class Settings(BaseSettings):
  model_config=SettingsConfigDict(
    env_file=PROJECT_ROOT / ".env",
    env_file_encoding="utf-8",
    extra='ignore',
    frozen=True
  )

  groq_api_key:SecretStr
  weather_api_key:SecretStr
  database_url:PostgresDsn
  db_echo:bool=False
  llm_model:str="openai/gpt-oss-120b"

  @property
  def sqlalchemy_dsn(self)->str:
    return _with_schema(self.database_url,"postgresql+psycopg")
  @property
  def psycopg_dsn(self)->str:
    return _with_schema(self.database_url,"postgresql")


if __name__=="__main__":
  print(Settings())