import pandas as pd
from datetime import datetime
from typing import List, Optional
from enum import Enum


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"
    NEUTRAL = "NEUTRAL"


class SignalStrength(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"


class Signal:
    def __init__(
        self,
        symbol: str,
        signal_type: SignalType,
        strength: SignalStrength,
        price: float,
        reasons: List[str],
        stop_loss: float,
        take_profit: float,
        risk_reward: float,
        timestamp: str,
        timeframe: str,
    ):
        self.symbol = symbol
        self.signal_type = signal_type
        self.strength = strength
        self.price = price
        self.reasons = reasons
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.risk_reward = risk_reward
        self.timestamp = timestamp
        self.timeframe = timeframe

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "signal_type": self.signal_type.value,
            "strength": self.strength.value,
            "price": round(self.price, 5),
            "reasons": self.reasons,
            "stop_loss": round(self.stop_loss, 5),
            "take_profit": round(self.take_profit, 5),
            "risk_reward": round(self.risk_reward, 2),
            "timestamp": self.timestamp,
            "timeframe": self.timeframe,
        }


class SignalGenerator:
    
    def generate_signals(self, symbol: str, df: pd.DataFrame) -> List[Signal]:
        signals = []
        
        if len(df) < 200:
            return signals
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        buy_score, sell_score, buy_reasons, sell_reasons = 0, 0, [], []
        
        buy_score, sell_score, buy_reasons, sell_reasons = self._check_ema_crossover(
            latest, prev, buy_score, sell_score, buy_reasons, sell_reasons
        )
        
        buy_score, sell_score, buy_reasons, sell_reasons = self._check_rsi(
            latest, buy_score, sell_score, buy_reasons, sell_reasons
        )
        
        buy_score, sell_score, buy_reasons, sell_reasons = self._check_macd(
            latest, prev, buy_score, sell_score, buy_reasons, sell_reasons
        )
        
        buy_score, sell_score, buy_reasons, sell_reasons = self._check_bollinger(
            latest, buy_score, sell_score, buy_reasons, sell_reasons
        )
        
        buy_score, sell_score, buy_reasons, sell_reasons = self._check_stochastic(
            latest, buy_score, sell_score, buy_reasons, sell_reasons
        )
        
        buy_score, sell_score, buy_reasons, sell_reasons = self._check_volume(
            latest, buy_score, sell_score, buy_reasons, sell_reasons
        )
        
        buy_score, sell_score, buy_reasons, sell_reasons = self._check_trend_alignment(
            latest, buy_score, sell_score, buy_reasons, sell_reasons
        )
        
        buy_score, sell_score, buy_reasons, sell_reasons = self._check_price_action(
            latest, prev, buy_score, sell_score, buy_reasons, sell_reasons
        )
        
        total_score = buy_score + sell_score
        
        if buy_score >= 5 and buy_score > sell_score * 1.5:
            signal = self._create_signal(
                symbol, latest, SignalType.STRONG_BUY, buy_reasons, df
            )
            signals.append(signal)
        elif buy_score >= 3 and buy_score > sell_score:
            signal = self._create_signal(
                symbol, latest, SignalType.BUY, buy_reasons, df
            )
            signals.append(signal)
        elif sell_score >= 5 and sell_score > buy_score * 1.5:
            signal = self._create_signal(
                symbol, latest, SignalType.STRONG_SELL, sell_reasons, df
            )
            signals.append(signal)
        elif sell_score >= 3 and sell_score > buy_score:
            signal = self._create_signal(
                symbol, latest, SignalType.SELL, sell_reasons, df
            )
            signals.append(signal)
        else:
            signal = self._create_signal(
                symbol, latest, SignalType.NEUTRAL,
                ["No clear direction - waiting for confirmation"], df
            )
            signals.append(signal)
        
        return signals

    def _check_ema_crossover(self, latest, prev, buy_score, sell_score, buy_reasons, sell_reasons):
        if latest["ema_9"] > latest["ema_21"] and prev["ema_9"] <= prev["ema_21"]:
            buy_score += 2
            buy_reasons.append("EMA 9 crossed above EMA 21")
        elif latest["ema_9"] < latest["ema_21"] and prev["ema_9"] >= prev["ema_21"]:
            sell_score += 2
            sell_reasons.append("EMA 9 crossed below EMA 21")
        
        if latest["Close"] > latest["ema_50"] and latest["Close"] > latest["ema_200"]:
            buy_score += 1
            buy_reasons.append("Price above EMA 50 & 200")
        elif latest["Close"] < latest["ema_50"] and latest["Close"] < latest["ema_200"]:
            sell_score += 1
            sell_reasons.append("Price below EMA 50 & 200")
        
        if latest["ema_9"] > latest["ema_21"] > latest["ema_50"]:
            buy_score += 1
            buy_reasons.append("EMA alignment bullish")
        elif latest["ema_9"] < latest["ema_21"] < latest["ema_50"]:
            sell_score += 1
            sell_reasons.append("EMA alignment bearish")
        
        return buy_score, sell_score, buy_reasons, sell_reasons

    def _check_rsi(self, latest, buy_score, sell_score, buy_reasons, sell_reasons):
        rsi = latest["rsi"]
        
        if rsi < 30:
            buy_score += 2
            buy_reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 70:
            sell_score += 2
            sell_reasons.append(f"RSI overbought ({rsi:.1f})")
        elif 30 <= rsi <= 40:
            buy_score += 1
            buy_reasons.append(f"RSI approaching oversold ({rsi:.1f})")
        elif 60 <= rsi <= 70:
            sell_score += 1
            sell_reasons.append(f"RSI approaching overbought ({rsi:.1f})")
        
        return buy_score, sell_score, buy_reasons, sell_reasons

    def _check_macd(self, latest, prev, buy_score, sell_score, buy_reasons, sell_reasons):
        if latest["macd"] > latest["macd_signal"] and prev["macd"] <= prev["macd_signal"]:
            buy_score += 2
            buy_reasons.append("MACD bullish crossover")
        elif latest["macd"] < latest["macd_signal"] and prev["macd"] >= prev["macd_signal"]:
            sell_score += 2
            sell_reasons.append("MACD bearish crossover")
        
        if latest["macd_histogram"] > 0 and latest["macd_histogram"] > prev["macd_histogram"]:
            buy_score += 1
            buy_reasons.append("MACD histogram increasing")
        elif latest["macd_histogram"] < 0 and latest["macd_histogram"] < prev["macd_histogram"]:
            sell_score += 1
            sell_reasons.append("MACD histogram decreasing")
        
        return buy_score, sell_score, buy_reasons, sell_reasons

    def _check_bollinger(self, latest, buy_score, sell_score, buy_reasons, sell_reasons):
        bb_pct = latest["bb_pct"]
        
        if bb_pct < 0:
            buy_score += 2
            buy_reasons.append("Price below lower Bollinger Band")
        elif bb_pct > 1:
            sell_score += 2
            sell_reasons.append("Price above upper Bollinger Band")
        
        if latest["bb_width"] < 0.02:
            buy_reasons.append("Bollinger squeeze - volatility expansion expected")
            sell_reasons.append("Bollinger squeeze - volatility expansion expected")
        
        return buy_score, sell_score, buy_reasons, sell_reasons

    def _check_stochastic(self, latest, buy_score, sell_score, buy_reasons, sell_reasons):
        k = latest["stoch_k"]
        d = latest["stoch_d"]
        
        if k < 20 and k > d:
            buy_score += 1
            buy_reasons.append(f"Stochastic oversold bullish ({k:.1f})")
        elif k > 80 and k < d:
            sell_score += 1
            sell_reasons.append(f"Stochastic overbought bearish ({k:.1f})")
        
        return buy_score, sell_score, buy_reasons, sell_reasons

    def _check_volume(self, latest, buy_score, sell_score, buy_reasons, sell_reasons):
        vol_ratio = latest["volume_ratio"]
        
        if vol_ratio > 1.5:
            buy_reasons.append(f"High volume ({vol_ratio:.1f}x avg)")
            sell_reasons.append(f"High volume ({vol_ratio:.1f}x avg)")
        
        if latest["Close"] > latest["vwap"] and vol_ratio > 1.2:
            buy_score += 1
            buy_reasons.append("Price above VWAP with volume")
        elif latest["Close"] < latest["vwap"] and vol_ratio > 1.2:
            sell_score += 1
            sell_reasons.append("Price below VWAP with volume")
        
        return buy_score, sell_score, buy_reasons, sell_reasons

    def _check_trend_alignment(self, latest, buy_score, sell_score, buy_reasons, sell_reasons):
        ema_aligned_bull = (
            latest["ema_9"] > latest["ema_21"] > latest["ema_50"] > latest["ema_200"]
        )
        ema_aligned_bear = (
            latest["ema_9"] < latest["ema_21"] < latest["ema_50"] < latest["ema_200"]
        )
        
        rsi_ok_bull = 40 < latest["rsi"] < 70
        rsi_ok_bear = 30 < latest["rsi"] < 60
        
        macd_ok_bull = latest["macd"] > latest["macd_signal"]
        macd_ok_bear = latest["macd"] < latest["macd_signal"]
        
        if ema_aligned_bull and rsi_ok_bull and macd_ok_bull:
            buy_score += 2
            buy_reasons.append("Full trend alignment bullish")
        elif ema_aligned_bear and rsi_ok_bear and macd_ok_bear:
            sell_score += 2
            sell_reasons.append("Full trend alignment bearish")
        
        return buy_score, sell_score, buy_reasons, sell_reasons

    def _check_price_action(self, latest, prev, buy_score, sell_score, buy_reasons, sell_reasons):
        body = latest["Close"] - latest["Open"]
        upper_wick = latest["High"] - max(latest["Close"], latest["Open"])
        lower_wick = min(latest["Close"], latest["Open"]) - latest["Low"]
        total_range = latest["High"] - latest["Low"]
        
        if total_range > 0:
            body_ratio = abs(body) / total_range
            
            if body > 0 and lower_wick > abs(body) * 2:
                buy_score += 1
                buy_reasons.append("Hammer/pin bar pattern")
            elif body < 0 and upper_wick > abs(body) * 2:
                sell_score += 1
                sell_reasons.append("Shooting star pattern")
        
        if latest["Close"] > latest["resistance_1"] and prev["Close"] <= prev["resistance_1"]:
            buy_score += 1
            buy_reasons.append("Breakout above resistance")
        elif latest["Close"] < latest["support_1"] and prev["Close"] >= prev["support_1"]:
            sell_score += 1
            sell_reasons.append("Breakdown below support")
        
        return buy_score, sell_score, buy_reasons, sell_reasons

    def _create_signal(self, symbol, latest, signal_type, reasons, df):
        atr = latest["atr"]
        price = latest["Close"]
        
        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
            stop_loss = price - (atr * 1.5)
            take_profit = price + (atr * 2.5)
        else:
            stop_loss = price + (atr * 1.5)
            take_profit = price - (atr * 2.5)
        
        risk = abs(price - stop_loss)
        reward = abs(take_profit - price)
        risk_reward = reward / risk if risk > 0 else 0
        
        if signal_type in [SignalType.STRONG_BUY, SignalType.STRONG_SELL]:
            strength = SignalStrength.STRONG
        elif len(reasons) >= 3:
            strength = SignalStrength.MODERATE
        else:
            strength = SignalStrength.WEAK
        
        timeframe = "1H"
        
        return Signal(
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            price=price,
            reasons=reasons[:6],
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward=risk_reward,
            timestamp=datetime.utcnow().isoformat(),
            timeframe=timeframe,
        )


signal_generator = SignalGenerator()
