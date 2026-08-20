import httpx
from datetime import datetime, timedelta
from typing import List, Optional, Dict


class NewsCalendar:
    HIGH_IMPACT_EVENTS = [
        "Non-Farm Payrolls",
        "NFP",
        "FOMC",
        "Federal Funds Rate",
        "CPI",
        "Core CPI",
        "GDP",
        "Interest Rate Decision",
        "ECB",
        "BOE",
        "BOJ",
        "RBA",
        "Retail Sales",
        "Unemployment Rate",
        "PMI",
        "ISM Manufacturing",
        "Consumer Confidence",
        "Initial Jobless Claims",
        "PCE",
        "Core PCE",
    ]
    
    CURRENCY_KEYWORDS = {
        "USD": ["USD", "US Dollar", "Fed", "Federal Reserve"],
        "EUR": ["EUR", "Euro", "ECB", "European Central Bank"],
        "GBP": ["GBP", "British Pound", "BOE", "Bank of England"],
        "JPY": ["JPY", "Japanese Yen", "BOJ", "Bank of Japan"],
        "AUD": ["AUD", "Australian Dollar", "RBA", "Reserve Bank of Australia"],
        "CAD": ["CAD", "Canadian Dollar", "BOC", "Bank of Canada"],
        "CHF": ["CHF", "Swiss Franc", "SNB", "Swiss National Bank"],
        "NZD": ["NZD", "New Zealand Dollar"],
    }
    
    def __init__(self):
        self.cache = {}
        self.cache_time = None
        self.cache_duration = timedelta(hours=1)
    
    async def get_upcoming_events(self) -> List[Dict]:
        now = datetime.utcnow()
        
        if self.cache_time and now - self.cache_time < self.cache_duration:
            return self.cache.get("events", [])
        
        events = await self._fetch_forex_factory()
        
        if not events:
            events = self._get_mock_events()
        
        self.cache = {"events": events}
        self.cache_time = now
        
        return events
    
    async def _fetch_forex_factory(self) -> List[Dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    events = []
                    
                    for item in data:
                        event = {
                            "title": item.get("title", ""),
                            "country": item.get("country", ""),
                            "date": item.get("date", ""),
                            "time": item.get("time", ""),
                            "impact": item.get("impact", ""),
                            "forecast": item.get("forecast", ""),
                            "previous": item.get("previous", ""),
                            "actual": item.get("actual", ""),
                        }
                        
                        if event["impact"].lower() in ["high", "holiday"]:
                            events.append(event)
                    
                    return events
        except Exception as e:
            print(f"Forex Factory fetch error: {e}")
        
        return []
    
    def _get_mock_events(self) -> List[Dict]:
        now = datetime.utcnow()
        
        events = [
            {
                "title": "Non-Farm Payrolls",
                "country": "USD",
                "date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "time": "13:30",
                "impact": "high",
                "forecast": "180K",
                "previous": "150K",
                "actual": None,
            },
            {
                "title": "FOMC Statement",
                "country": "USD",
                "date": (now + timedelta(days=3)).strftime("%Y-%m-%d"),
                "time": "19:00",
                "impact": "high",
                "forecast": None,
                "previous": None,
                "actual": None,
            },
            {
                "title": "CPI m/m",
                "country": "USD",
                "date": (now + timedelta(days=5)).strftime("%Y-%m-%d"),
                "time": "13:30",
                "impact": "high",
                "forecast": "0.3%",
                "previous": "0.4%",
                "actual": None,
            },
            {
                "title": "ECB Interest Rate Decision",
                "country": "EUR",
                "date": (now + timedelta(days=2)).strftime("%Y-%m-%d"),
                "time": "12:15",
                "impact": "high",
                "forecast": "4.50%",
                "previous": "4.50%",
                "actual": None,
            },
            {
                "title": "BOE Interest Rate Decision",
                "country": "GBP",
                "date": (now + timedelta(days=4)).strftime("%Y-%m-%d"),
                "time": "12:00",
                "impact": "high",
                "forecast": "5.25%",
                "previous": "5.25%",
                "actual": None,
            },
        ]
        
        return events
    
    def is_high_impact_period(self) -> dict:
        now = datetime.utcnow()
        hour = now.hour
        minute = now.minute
        
        high_impact_windows = {
            "NFP_window": (13, 15, 13, 45),
            "FOMC_window": (18, 30, 20, 0),
            "ECB_window": (11, 30, 13, 0),
            "BOE_window": (11, 30, 13, 0),
        }
        
        warnings = []
        
        nfp_start_hour, nfp_start_min, nfp_end_hour, nfp_end_min = high_impact_windows["NFP_window"]
        if (
            (hour == nfp_start_hour and minute >= nfp_start_min)
            or (hour == nfp_end_hour and minute < nfp_end_min)
            or (nfp_start_hour < hour < nfp_end_hour)
        ):
            warnings.append("NFP Release Window - HIGH VOLATILITY EXPECTED")
        
        fomc_start_hour, fomc_start_min, fomc_end_hour, fomc_end_min = high_impact_windows["FOMC_window"]
        if (
            (hour == fomc_start_hour and minute >= fomc_start_min)
            or (hour == fomc_end_hour and minute < fomc_end_min)
            or (fomc_start_hour < hour < fomc_end_hour)
        ):
            warnings.append("FOMC Window - EXTREME VOLATILITY EXPECTED")
        
        return {
            "is_high_impact": len(warnings) > 0,
            "warnings": warnings,
            "timestamp": now.isoformat(),
        }
    
    def should_avoid_trading(self, symbol: str) -> dict:
        now = datetime.utcnow()
        
        avoid_periods = [
            {"start_hour": 13, "start_min": 15, "end_hour": 14, "end_min": 0, "reason": "Pre-NFP volatility"},
            {"start_hour": 13, "start_min": 25, "end_hour": 14, "end_min": 15, "reason": "NFP Release"},
            {"start_hour": 18, "start_min": 0, "end_hour": 20, "end_min": 0, "reason": "FOMC Window"},
        ]
        
        for period in avoid_periods:
            start = period["start_hour"] * 60 + period["start_min"]
            end = period["end_hour"] * 60 + period["end_min"]
            current = now.hour * 60 + now.minute
            
            if start <= current <= end:
                return {
                    "avoid": True,
                    "reason": period["reason"],
                    "until": f"{period['end_hour']:02d}:{period['end_min']:02d} UTC",
                }
        
        return {"avoid": False, "reason": None, "until": None}


news_calendar = NewsCalendar()
