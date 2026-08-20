from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    ALERT_EMAIL: str = ""
    
    SYMBOLS: List[str] = [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X",
        "USDCHF=X", "USDCAD=X", "NZDUSD=X",
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
        "NVDA", "META", "BTC-USD", "ETH-USD"
    ]
    
    TIMEFRAME: str = "1h"
    SCAN_INTERVAL_MINUTES: int = 15
    
    class Config:
        env_file = ".env"

settings = Settings()
