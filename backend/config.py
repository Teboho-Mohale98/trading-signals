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
    
    WHATSAPP_CLOUD_API_TOKEN: str = ""
    WHATSAPP_CLOUD_API_PHONE_ID: str = ""
    WHATSAPP_CLOUD_API_VERSION: str = "v18.0"
    WHATSAPP_RECIPIENT: str = ""
    
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"
    
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
