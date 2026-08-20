import yfinance as yf
import pandas as pd
import requests
import io
import traceback
from datetime import datetime, timedelta
from typing import Optional


class MarketData:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def get_symbol_data(
        self, symbol: str, period: str = "3mo", interval: str = "1h"
    ) -> Optional[pd.DataFrame]:
        cache_key = f"{symbol}_{period}_{interval}"
        
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data

        df = self._fetch_with_yfinance(symbol, period, interval)
        
        if df is None or df.empty:
            df = self._fetch_with_direct_url(symbol, period, interval)
        
        if df is not None and not df.empty:
            self.cache[cache_key] = (datetime.now(), df)
            return df
        
        return None

    def _fetch_with_yfinance(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        try:
            yf.set_config(proxy=None)
            ticker = yf.Ticker(symbol, session=self.session)
            df = ticker.history(period=period, interval=interval)
            
            if df is not None and not df.empty:
                df = df.reset_index()
                for col in ["Datetime", "Date", "date", "datetime"]:
                    if col in df.columns:
                        df = df.rename(columns={col: "timestamp"})
                        break
                
                required_cols = ["Open", "High", "Low", "Close", "Volume"]
                for col in required_cols:
                    if col not in df.columns:
                        return None
                
                df = df.dropna(subset=["Open", "High", "Low", "Close"])
                print(f"yfinance: Fetched {len(df)} candles for {symbol}")
                return df
        except Exception as e:
            print(f"yfinance error for {symbol}: {e}")
        
        return None

    def _fetch_with_direct_url(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        try:
            period_map = {"1d": "1d", "5d": "5d", "1mo": "1mo", "3mo": "3mo", "6mo": "6mo", "1y": "1y", "2y": "2y", "5y": "5y", "10y": "10y", "max": "max"}
            interval_map = {"1m": "1m", "2m": "2m", "5m": "5m", "15m": "15m", "30m": "30m", "60m": "60m", "90m": "90m", "1h": "1h", "1d": "1d", "5d": "5d", "1wk": "1wk", "1mo": "1mo", "3mo": "3mo"}
            
            p = period_map.get(period, "3mo")
            i = interval_map.get(interval, "1h")
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1=0&period2=9999999999&interval={i}&range={p}"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"Direct URL failed for {symbol}: HTTP {response.status_code}")
                return None
            
            data = response.json()
            result = data.get("chart", {}).get("result", [])
            
            if not result:
                print(f"No chart data for {symbol}")
                return None
            
            chart = result[0]
            timestamps = chart.get("timestamp", [])
            indicators = chart.get("indicators", {}).get("quote", [{}])[0]
            
            if not timestamps or not indicators:
                return None
            
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(timestamps, unit="s"),
                "Open": indicators.get("open", []),
                "High": indicators.get("high", []),
                "Low": indicators.get("low", []),
                "Close": indicators.get("close", []),
                "Volume": indicators.get("volume", []),
            })
            
            df = df.dropna(subset=["Open", "High", "Low", "Close"])
            df = df[df["Close"] > 0]
            
            print(f"Direct URL: Fetched {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            print(f"Direct URL error for {symbol}: {e}")
            traceback.print_exc()
            return None

    def get_current_price(self, symbol: str) -> Optional[float]:
        try:
            ticker = yf.Ticker(symbol, session=self.session)
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
