# Trading Signals System

Real-time forex and stock trading signals with technical analysis, news alerts, and notifications.

## Features

- **Multi-Indicator Analysis**: RSI, MACD, Bollinger Bands, EMA crossovers, Stochastic, Volume analysis
- **Signal Generation**: STRONG_BUY, BUY, STRONG_SELL, SELL, NEUTRAL signals
- **Risk Management**: Automatic stop loss and take profit levels with risk/reward ratios
- **News Integration**: Economic calendar with NFP, FOMC, and high-impact event warnings
- **Notifications**: Telegram bot and email alerts for signals
- **Dashboard**: Real-time web interface to view all signals

## Project Structure

```
trading-signals/
├── backend/                 # FastAPI Python backend
│   ├── main.py             # API endpoints
│   ├── config.py           # Configuration
│   ├── services/
│   │   ├── market_data.py  # Yahoo Finance data fetching
│   │   ├── indicators.py   # Technical indicators
│   │   ├── signals.py      # Signal generation logic
│   │   ├── news.py         # News calendar
│   │   ├── telegram.py     # Telegram notifications
│   │   └── email.py        # Email notifications
│   ├── requirements.txt
│   ├── Dockerfile
│   └── render.yaml         # Render deployment config
└── frontend/               # Next.js dashboard
    ├── src/
    │   ├── app/            # Next.js app directory
    │   ├── components/     # React components
    │   ├── lib/            # API utilities
    │   └── types/          # TypeScript types
    ├── package.json
    └── vercel.json         # Vercel deployment config
```

## Deployment Guide

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `trading-signals`
3. Upload all files from this project
4. Make sure to include `.env.example` files

### Step 2: Deploy Backend to Render

1. Go to https://render.com and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: trading-signals-api
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID
   - `SMTP_USER`: Your email
   - `SMTP_PASS`: Your app password
   - `ALERT_EMAIL`: Where to send alerts
6. Click "Create Web Service"
7. Copy the deployed URL (e.g., `https://trading-signals-api.onrender.com`)

### Step 3: Deploy Frontend to Vercel

1. Go to https://vercel.com and sign up/login
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL from Step 2
6. Click "Deploy"
7. Copy the deployed URL

### Step 4: Setup Telegram Bot

1. Message @BotFather on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Message your new bot and get your chat ID from https://api.telegram.org/bot<TOKEN>/getUpdates

### Step 5: Setup Email Notifications (Gmail)

1. Enable 2FA on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password
4. Use this password for `SMTP_PASS`

### Step 6: Setup WhatsApp Notifications

#### Option A: WhatsApp Cloud API (Meta) - Free

1. Go to https://developers.facebook.com
2. Create a Meta Developer account
3. Create a new app → Select "Business" type → Add "WhatsApp" product
4. Get your **Phone Number ID** and generate a **Permanent Access Token**
5. Add your phone number and verify it
6. Add to Render env vars:
   - `WHATSAPP_CLOUD_API_TOKEN`: Your permanent token
   - `WHATSAPP_CLOUD_API_PHONE_ID`: Your phone number ID
   - `WHATSAPP_RECIPIENT`: Your phone number (format: 27821234567)

#### Option B: Twilio WhatsApp - Easiest ($0.005/msg)

1. Go to https://www.twilio.com and sign up
2. Get your Account SID and Auth Token from the dashboard
3. Enable WhatsApp sandbox: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
4. Send the join message from your phone to the sandbox number
5. Add to Render env vars:
   - `TWILIO_ACCOUNT_SID`: Your Account SID
   - `TWILIO_AUTH_TOKEN`: Your Auth Token
   - `WHATSAPP_RECIPIENT`: whatsapp:+27821234567

**Note**: System tries Cloud API first, falls back to Twilio automatically.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/signals` | GET | Get all trading signals |
| `/api/signals/{symbol}` | GET | Get signal for specific symbol |
| `/api/news` | GET | Get economic calendar |
| `/api/market-status` | GET | Get market open/close status |
| `/api/scan` | POST | Trigger manual scan |
| `/api/notifications/send` | POST | Send notification |

## Supported Symbols

**Forex**: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCHF, USDCAD, NZDUSD

**Stocks**: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META

**Crypto**: BTC-USD, ETH-USD

## Important Disclaimers

⚠️ **This is NOT financial advice.**

- All trading involves substantial risk of loss
- Past performance does not guarantee future results
- No system guarantees profits
- You are responsible for your own trading decisions
- Never trade with money you cannot afford to lose
- Always practice on a demo account first

## License

MIT
