import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from config import settings


class EmailNotifier:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_pass = settings.SMTP_PASS
        self.alert_email = settings.ALERT_EMAIL
    
    async def send_signal(self, signal_dict: dict) -> bool:
        if not self.smtp_user or not self.alert_email:
            print("Email not configured")
            return False
        
        subject = f"Trading Signal: {signal_dict['signal_type']} - {signal_dict['symbol']}"
        html_content = self._format_signal_html(signal_dict)
        text_content = self._format_signal_text(signal_dict)
        
        return self._send_email(subject, html_content, text_content)
    
    async def send_alert(self, subject: str, message: str) -> bool:
        if not self.smtp_user or not self.alert_email:
            return False
        
        return self._send_email(subject, message, message)
    
    def _send_email(self, subject: str, html_content: str, text_content: str) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = self.alert_email
            
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def _format_signal_html(self, signal: dict) -> str:
        signal_type = signal["signal_type"]
        
        if "BUY" in signal_type:
            color = "#22c55e"
            bg_color = "#f0fdf4"
        elif "SELL" in signal_type:
            color = "#ef4444"
            bg_color = "#fef2f2"
        else:
            color = "#6b7280"
            bg_color = "#f9fafb"
        
        reasons_html = "".join([f"<li>{r}</li>" for r in signal["reasons"]])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: {bg_color}; border-left: 4px solid {color}; padding: 20px; border-radius: 4px; }}
        .signal-type {{ color: {color}; font-size: 24px; font-weight: bold; margin: 0; }}
        .details {{ background: #f8fafc; padding: 20px; border-radius: 4px; margin-top: 20px; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }}
        .label {{ font-weight: bold; color: #64748b; }}
        .value {{ color: #1e293b; }}
        .reasons {{ margin-top: 20px; }}
        .reasons h3 {{ color: #475569; font-size: 16px; }}
        .reasons ul {{ padding-left: 20px; }}
        .reasons li {{ margin: 5px 0; }}
        .footer {{ margin-top: 20px; padding: 15px; background: #fef3c7; border-radius: 4px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <p class="signal-type">{signal_type} Signal</p>
            <p style="margin: 5px 0 0 0; color: #475569;">{signal['symbol']}</p>
        </div>
        
        <div class="details">
            <div class="detail-row">
                <span class="label">Strength</span>
                <span class="value">{signal['strength']}</span>
            </div>
            <div class="detail-row">
                <span class="label">Entry Price</span>
                <span class="value">{signal['price']}</span>
            </div>
            <div class="detail-row">
                <span class="label">Stop Loss</span>
                <span class="value" style="color: #ef4444;">{signal['stop_loss']}</span>
            </div>
            <div class="detail-row">
                <span class="label">Take Profit</span>
                <span class="value" style="color: #22c55e;">{signal['take_profit']}</span>
            </div>
            <div class="detail-row">
                <span class="label">Risk:Reward</span>
                <span class="value">1:{signal['risk_reward']}</span>
            </div>
            <div class="detail-row">
                <span class="label">Timeframe</span>
                <span class="value">{signal['timeframe']}</span>
            </div>
        </div>
        
        <div class="reasons">
            <h3>Analysis Reasons</h3>
            <ul>{reasons_html}</ul>
        </div>
        
        <div class="footer">
            <strong>⚠️ Disclaimer:</strong> This is not financial advice. Trading involves substantial risk of loss. 
            Always do your own research and never trade with money you cannot afford to lose.
        </div>
        
        <p style="color: #94a3b8; font-size: 11px; margin-top: 20px; text-align: center;">
            Generated: {signal['timestamp'][:19]}
        </p>
    </div>
</body>
</html>
"""
        return html
    
    def _format_signal_text(self, signal: dict) -> str:
        reasons = "\n".join([f"  • {r}" for r in signal["reasons"]])
        
        text = f"""
{signal['signal_type']} Signal - {signal['symbol']}

Strength: {signal['strength']}
Entry Price: {signal['price']}
Stop Loss: {signal['stop_loss']}
Take Profit: {signal['take_profit']}
Risk:Reward: 1:{signal['risk_reward']}
Timeframe: {signal['timeframe']}

Analysis Reasons:
{reasons}

Generated: {signal['timestamp'][:19]}

⚠️ Disclaimer: This is not financial advice. Trading involves substantial risk of loss.
"""
        return text


email_notifier = EmailNotifier()
