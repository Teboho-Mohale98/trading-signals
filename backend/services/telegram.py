import httpx
from typing import Optional
from config import settings


class TelegramNotifier:
    def __init__(self):
        self.base_url = "https://api.telegram.org"
    
    async def send_signal(self, signal_dict: dict) -> bool:
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            print("Telegram not configured")
            return False
        
        message = self._format_signal(signal_dict)
        
        url = f"{self.base_url}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                return response.status_code == 200
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def _format_signal(self, signal: dict) -> str:
        signal_type = signal["signal_type"]
        emoji = "🟢" if "BUY" in signal_type else "🔴" if "SELL" in signal_type else "⚪"
        strength = signal["strength"]
        
        reasons_text = "\n".join([f"• {r}" for r in signal["reasons"]])
        
        message = f"""
{emoji} <b>{signal_type} Signal - {signal['symbol']}</b>

<b>Strength:</b> {strength}
<b>Price:</b> {signal['price']}
<b>Stop Loss:</b> {signal['stop_loss']}
<b>Take Profit:</b> {signal['take_profit']}
<b>Risk:Reward:</b> 1:{signal['risk_reward']}

<b>Analysis:</b>
{reasons_text}

<i>Timeframe: {signal['timeframe']}
Generated: {signal['timestamp'][:19]}</i>

⚠️ <i>Not financial advice. Trade at your own risk.</i>
"""
        return message.strip()
    
    async def send_alert(self, message: str) -> bool:
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            return False
        
        url = f"{self.base_url}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                return response.status_code == 200
        except Exception:
            return False


telegram_notifier = TelegramNotifier()
