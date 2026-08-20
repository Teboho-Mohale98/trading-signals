import pandas as pd
import numpy as np
import ta


class TechnicalIndicators:
    
    def calculate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._add_ema(df)
        df = self._add_rsi(df)
        df = self._add_macd(df)
        df = self._add_bollinger(df)
        df = self._add_atr(df)
        df = self._add_stochastic(df)
        df = self._add_volume_indicators(df)
        df = self._add_support_resistance(df)
        return df

    def _add_ema(self, df: pd.DataFrame) -> pd.DataFrame:
        df["ema_9"] = ta.trend.ema_indicator(df["Close"], window=9)
        df["ema_21"] = ta.trend.ema_indicator(df["Close"], window=21)
        df["ema_50"] = ta.trend.ema_indicator(df["Close"], window=50)
        df["ema_200"] = ta.trend.ema_indicator(df["Close"], window=200)
        return df

    def _add_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        df["rsi"] = ta.momentum.rsi(df["Close"], window=14)
        df["rsi_6"] = ta.momentum.rsi(df["Close"], window=6)
        return df

    def _add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        macd = ta.trend.MACD(df["Close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["macd_histogram"] = macd.macd_diff()
        return df

    def _add_bollinger(self, df: pd.DataFrame) -> pd.DataFrame:
        bb = ta.volatility.BollingerBands(df["Close"], window=20, window_dev=2)
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_middle"] = bb.bollinger_mavg()
        df["bb_lower"] = bb.bollinger_lband()
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
        df["bb_pct"] = bb.bollinger_pband()
        return df

    def _add_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        df["atr"] = ta.volatility.average_true_range(
            df["High"], df["Low"], df["Close"], window=14
        )
        df["atr_pct"] = df["atr"] / df["Close"] * 100
        return df

    def _add_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        stoch = ta.momentum.StochasticOscillator(
            df["High"], df["Low"], df["Close"]
        )
        df["stoch_k"] = stoch.stoch()
        df["stoch_d"] = stoch.stoch_signal()
        return df

    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df["obv"] = ta.volume.on_balance_volume(df["Close"], df["Volume"])
        df["vwap"] = (
            (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum()
        )
        df["volume_sma"] = df["Volume"].rolling(window=20).mean()
        df["volume_ratio"] = df["Volume"] / df["volume_sma"]
        return df

    def _add_support_resistance(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        df["pivot"] = (df["High"] + df["Low"] + df["Close"]) / 3
        df["support_1"] = 2 * df["pivot"] - df["High"]
        df["resistance_1"] = 2 * df["pivot"] - df["Low"]
        df["support_2"] = df["pivot"] - (df["High"] - df["Low"])
        df["resistance_2"] = df["pivot"] + (df["High"] - df["Low"])
        return df


technical_indicators = TechnicalIndicators()
