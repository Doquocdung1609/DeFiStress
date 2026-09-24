from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_mode: str = "FIXTURE"
    log_level: str = "INFO"

    # Ethereum sources.
    eth_rpc_url: str = ""
    eth_archive_rpc_url: str = ""
    graph_api_key: str = ""
    aave_v3_subgraph_id: str = "JCNWRypm7FYwV8fx5HhzZPSFaMxgkPuw4TnR3Gpi81zk"

    graph_page_size: int = 100
    graph_max_pages: int = 10
    snapshot_confirmations: int = 12
    max_borrowers: int = 500

    # Terra historical-source configuration. These values only indicate that a
    # provider has been configured; imported datasets still carry their own
    # FIXTURE/PARTIAL/REAL_HISTORICAL evidence status.
    terra_archive_lcd_url: str = ""
    terra_history_data_url: str = ""
    curve_history_data_url: str = ""
    bridge_flow_data_url: str = ""

    database_url: str = "sqlite:///./defi_stress.db"
    redis_url: str = "redis://localhost:6379/0"
    async_backend: str = "local"
    coingecko_api_key: str = ""
    defillama_api_url: str = "https://coins.llama.fi"
    chain_id: int = 1
    discovery_lookback_blocks: int = 50_000
    borrower_max_users: int = 1_000
    rpc_batch_size: int = 50
    rpc_block_chunk_size: int = 2_000
    uniswap_tick_word_radius: int = 4


@lru_cache
def get_settings() -> Settings:
    return Settings()
