import httpx
from typing import Optional
from config import settings


class WhatsAppNotifier:
    def __init__(self):
        self.cloud_api_token = settings.WHATSAPP_CLOUD_API_TOKEN
        self.cloud_api_phone_id = settings.WHATSAPP_CLOUD_API_PHONE_ID
        self.cloud_api_version = settings.WHATSAPP_CLOUD_API_VERSION
        self.twilio_sid = settings.TWILIO_ACCOUNT_SID
        self.twilio_auth_token = settings.TWILIO_AUTH_TOKEN
        self.twilio_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
        self.recipient = settings.WHATSAPP_RECIPIENT

    async def send_signal(self, signal_dict: dict) -> bool:
        message = self._format_signal(signal_dict)
        
        if self.cloud_api_token and self.cloud_api_phone_id:
            sent = await self._send_via_cloud_api(message)
            if sent:
                return True
        
        if self.twilio_sid and self.twilio_auth_token:
            sent = await self._send_via_twilio(message)
            if sent:
                return True
        
        print("WhatsApp not configured - no valid credentials")
        return False

    async def send_alert(self, message: str) -> bool:
        if self.cloud_api_token and self.cloud_api_phone_id:
            return await self._send_via_cloud_api(message)
        
        if self.twilio_sid and self.twilio_auth_token:
            return await self._send_via_twilio(message)
        
        return False

    async def _send_via_cloud_api(self, message: str) -> bool:
        if not self.cloud_api_token or not self.cloud_api_phone_id or not self.recipient:
            return False
        
        url = f"https://graph.facebook.com/{self.cloud_api_version}/{self.cloud_api_phone_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.cloud_api_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": self.recipient,
            "type": "text",
            "text": {"body": message},
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    print("WhatsApp Cloud API: Message sent")
                    return True
                else:
                    print(f"WhatsApp Cloud API error: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            print(f"WhatsApp Cloud API error: {e}")
            return False

    async def _send_via_twilio(self, message: str) -> bool:
        if not self.twilio_sid or not self.twilio_auth_token or not self.recipient:
            return False
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        
        from_number = f"whatsapp:{self.twilio_whatsapp_number}"
        to_number = f"whatsapp:{self.recipient}"
        
        data = {
            "From": from_number,
            "To": to_number,
            "Body": message,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=(self.twilio_sid, self.twilio_auth_token),
                )
                if response.status_code == 201:
                    print("Twilio WhatsApp: Message sent")
                    return True
                else:
                    print(f"Twilio WhatsApp error: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            print(f"Twilio WhatsApp error: {e}")
            return False

    def _format_signal(self, signal: dict) -> str:
        signal_type = signal["signal_type"]
        
        if "BUY" in signal_type:
            emoji = "🟢"
        elif "SELL" in signal_type:
            emoji = "🔴"
        else:
            emoji = "⚪"
        
        reasons = "\n".join([f"  • {r}" for r in signal["reasons"][:5]])
        
        message = f"""
{emoji} *{signal_type} Signal* - {signal['symbol']}

*Strength:* {signal['strength']}
*Entry:* {signal['price']}
*Stop Loss:* {signal['stop_loss']}
*Take Profit:* {signal['take_profit']}
*Risk:Reward:* 1:{signal['risk_reward']}

*Analysis:*
{reasons}

*Timeframe:* {signal['timeframe']}
*Time:* {signal['timestamp'][:19]}

_This is not financial advice. Trade at your own risk._
"""
        return message.strip()


whatsapp_notifier = WhatsAppNotifier()
