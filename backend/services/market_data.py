import yfinance as yf
import pandas as pd
import traceback
from datetime import datetime, timedelta
from typing import Optional


class MarketData:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)

    def get_symbol_data(
        self, symbol: str, period: str = "3mo", interval: str = "1h"
    ) -> Optional[pd.DataFrame]:
        cache_key = f"{symbol}_{period}_{interval}"
        
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data

        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df is None or df.empty:
                print(f"No data returned for {symbol}")
                df = ticker.history(period="3mo", interval="1d")
            
            if df is None or df.empty:
                print(f"Still no data for {symbol} after fallback")
                return None
            
            df = df.reset_index()
            
            for col in ["Datetime", "Date", "date", "datetime"]:
                if col in df.columns:
                    df = df.rename(columns={col: "timestamp"})
                    break
            
            required_cols = ["Open", "High", "Low", "Close", "Volume"]
            for col in required_cols:
                if col not in df.columns:
                    print(f"Missing column {col} for {symbol}")
                    return None
            
            df = df.dropna(subset=["Open", "High", "Low", "Close"])
            
            print(f"Fetched {len(df)} candles for {symbol}")
            
            self.cache[cache_key] = (datetime.now(), df)
            return df
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            traceback.print_exc()
            return None

    def get_current_price(self, symbol: str) -> Optional[float]:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            return info.get("lastPrice") or info.get("last_price")
        except Exception:
            return None

    def get_market_status(self) -> dict:
        now = datetime.utcnow()
        hour = now.hour
        weekday = now.weekday()
        
        forex_open = weekday < 5 and (22 <= hour or hour < 22)
        stock_open = weekday < 5 and 13 <= hour < 21
        
        return {
            "forex": "Open" if forex_open else "Closed",
            "stocks": "Open" if stock_open else "Closed",
            "timestamp": now.isoformat()
        }


market_data = MarketData()
