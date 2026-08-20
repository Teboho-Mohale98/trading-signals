from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import asyncio

from config import settings
from services.market_data import market_data
from services.indicators import technical_indicators
from services.signals import signal_generator, SignalType
from services.telegram import telegram_notifier
from services.email import email_notifier
from services.news import news_calendar

app = FastAPI(
    title="Trading Signals API",
    description="Real-time forex and stock trading signals with technical analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "Trading Signals API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "signals": "/api/signals",
            "signal_detail": "/api/signals/{symbol}",
            "news": "/api/news",
            "market_status": "/api/market-status",
            "symbols": "/api/symbols",
        },
    }


@app.get("/api/signals")
async def get_all_signals(
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols"),
    min_strength: Optional[str] = Query("WEAK", description="Minimum signal strength"),
):
    try:
        symbol_list = symbols.split(",") if symbols else settings.SYMBOLS
        
        all_signals = []
        
        for symbol in symbol_list:
            try:
                df = market_data.get_symbol_data(symbol)
                if df is None or len(df) < 50:
                    print(f"Skipping {symbol}: insufficient data ({len(df) if df is not None else 0} candles)")
                    continue
                
                df = technical_indicators.calculate_all(df)
                signals = signal_generator.generate_signals(symbol, df)
                
                for signal in signals:
                    signal_dict = signal.to_dict()
                    signal_dict["news"] = await news_calendar.get_upcoming_events()
                    signal_dict["market_status"] = market_data.get_market_status()
                    all_signals.append(signal_dict)
                    
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        strong_signals = [
            s for s in all_signals
            if s["signal_type"] != "NEUTRAL"
        ]
        
        strong_signals.sort(
            key=lambda x: (
                0 if "STRONG" in x["signal_type"] else 1,
                x["risk_reward"]
            ),
            reverse=True,
        )
        
        return {
            "total_signals": len(all_signals),
            "actionable_signals": len(strong_signals),
            "signals": strong_signals,
            "all_signals": all_signals,
            "generated_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals/{symbol}")
async def get_symbol_signal(symbol: str):
    try:
        df = market_data.get_symbol_data(symbol)
        if df is None:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        if len(df) < 50:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for {symbol} ({len(df)} candles, need 50+)",
            )
        
        df = technical_indicators.calculate_all(df)
        signals = signal_generator.generate_signals(symbol, df)
        
        if not signals:
            raise HTTPException(status_code=404, detail="No signals generated")
        
        signal_dict = signals[0].to_dict()
        
        latest = df.iloc[-1]
        signal_dict["indicators"] = {
            "rsi": round(float(latest["rsi"]), 2),
            "macd": round(float(latest["macd"]), 5),
            "macd_signal": round(float(latest["macd_signal"]), 5),
            "bb_pct": round(float(latest["bb_pct"]), 2),
            "atr": round(float(latest["atr"]), 5),
            "volume_ratio": round(float(latest["volume_ratio"]), 2),
        }
        
        signal_dict["price_data"] = {
            "open": round(float(latest["Open"]), 5),
            "high": round(float(latest["High"]), 5),
            "low": round(float(latest["Low"]), 5),
            "close": round(float(latest["Close"]), 5),
            "support_1": round(float(latest["support_1"]), 5),
            "resistance_1": round(float(latest["resistance_1"]), 5),
        }
        
        signal_dict["news"] = await news_calendar.get_upcoming_events()
        signal_dict["market_status"] = market_data.get_market_status()
        
        return signal_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news")
async def get_news():
    try:
        events = await news_calendar.get_upcoming_events()
        current_news = news_calendar.is_high_impact_period()
        
        return {
            "upcoming_events": events,
            "current_status": current_news,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-status")
async def get_market_status():
    status = market_data.get_market_status()
    news_status = news_calendar.is_high_impact_period()
    
    return {
        "market": status,
        "news": news_status,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/symbols")
async def get_symbols():
    return {
        "default_symbols": settings.SYMBOLS,
        "description": {
            "EURUSD=X": "EUR/USD Forex",
            "GBPUSD=X": "GBP/USD Forex",
            "USDJPY=X": "USD/JPY Forex",
            "AUDUSD=X": "AUD/USD Forex",
            "USDCHF=X": "USD/CHF Forex",
            "USDCAD=X": "USD/CAD Forex",
            "NZDUSD=X": "NZD/USD Forex",
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft",
            "GOOGL": "Alphabet",
            "AMZN": "Amazon",
            "TSLA": "Tesla",
            "NVDA": "NVIDIA",
            "META": "Meta Platforms",
            "BTC-USD": "Bitcoin",
            "ETH-USD": "Ethereum",
        },
    }


@app.post("/api/notifications/send")
async def send_signal_notification(signal: dict):
    results = {"telegram": False, "email": False}
    
    if signal.get("signal_type") != "NEUTRAL":
        results["telegram"] = await telegram_notifier.send_signal(signal)
        results["email"] = await email_notifier.send_signal(signal)
    
    return {
        "notification_sent": any(results.values()),
        "channels": results,
    }


@app.post("/api/scan")
async def trigger_scan(symbols: Optional[str] = Query(None)):
    symbol_list = symbols.split(",") if symbols else settings.SYMBOLS
    
    results = []
    
    for symbol in symbol_list:
        try:
            news_check = news_calendar.should_avoid_trading(symbol)
            if news_check["avoid"]:
                results.append({
                    "symbol": symbol,
                    "skipped": True,
                    "reason": news_check["reason"],
                })
                continue
            
            df = market_data.get_symbol_data(symbol)
            if df is None or len(df) < 50:
                results.append({
                    "symbol": symbol,
                    "skipped": True,
                    "reason": "Insufficient data",
                })
                continue
            
            df = technical_indicators.calculate_all(df)
            signals = signal_generator.generate_signals(symbol, df)
            
            if signals and signals[0].signal_type != SignalType.NEUTRAL:
                signal_dict = signals[0].to_dict()
                
                await telegram_notifier.send_signal(signal_dict)
                await email_notifier.send_signal(signal_dict)
                
                results.append({
                    "symbol": symbol,
                    "signal": signal_dict,
                    "notified": True,
                })
            else:
                results.append({
                    "symbol": symbol,
                    "signal": "NEUTRAL",
                    "notified": False,
                })
                
        except Exception as e:
            results.append({
                "symbol": symbol,
                "error": str(e),
            })
    
    return {
        "scan_results": results,
        "scanned_at": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
