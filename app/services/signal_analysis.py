import pandas as pd
import numpy as np
from config import Config

try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False

class SignalAnalysisService:
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = None) -> pd.Series:
        if period is None:
            period = Config.ATR_PERIOD
            
        if HAS_PANDAS_TA:
            return df.ta.atr(length=period)
        else:
            # Manual ATR Calculation
            high = df['high']
            low = df['low']
            close = df['close']
            
            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean() # Simple Moving Average of TR
            # For Wilder's smoothing (RMA), which is standard for ATR:
            # atr = tr.ewm(alpha=1/period, adjust=False).mean() 
            # Using simple rolling mean for simplicity if pandas_ta fails, 
import pandas as pd
import numpy as np
from config import Config

try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False

class SignalAnalysisService:
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = None) -> pd.Series:
        if period is None:
            period = Config.ATR_PERIOD
            
        if HAS_PANDAS_TA:
            return df.ta.atr(length=period)
        else:
            # Manual ATR Calculation
            high = df['high']
            low = df['low']
            close = df['close']
            
            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean() # Simple Moving Average of TR
            # For Wilder's smoothing (RMA), which is standard for ATR:
            # atr = tr.ewm(alpha=1/period, adjust=False).mean() 
            # Using simple rolling mean for simplicity if pandas_ta fails, 
            # but let's use ewm to be closer to standard ATR
            atr = tr.ewm(alpha=1/period, adjust=False).mean()
            
            return atr

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        if HAS_PANDAS_TA:
            return df.ta.rsi(length=period)
        else:
            # Manual RSI Calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            # Use exponential moving average for better accuracy (Wilder's Smoothing)
            # gain = delta.where(delta > 0, 0).ewm(alpha=1/period, adjust=False).mean()
            # loss = -delta.where(delta < 0, 0).ewm(alpha=1/period, adjust=False).mean()
            # Using Simple Moving Average for robustness if dependencies are tricky, 
            # but let's try EWM as it's standard.
            gain = delta.where(delta > 0, 0).ewm(alpha=1/period, adjust=False).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

    @staticmethod
    def generate_signal(symbol: str, df: pd.DataFrame):
        """
        Generates a trading signal based on the latest data.
        """
        if df is None or df.empty:
            return None

        # Calculate Indicators
        df['ATR'] = SignalAnalysisService.calculate_atr(df)
        df['RSI'] = SignalAnalysisService.calculate_rsi(df)
        
        # Get latest candle
        latest = df.iloc[-1]
        current_price = latest['close']
        atr_value = latest['ATR']
        rsi_value = latest['RSI']
        
        if pd.isna(atr_value) or pd.isna(rsi_value):
            return {"error": "Not enough data for indicators"}

        # Logic for Long/Short
        direction = None
        
        # RSI Logic
        if rsi_value < 30:
            direction = "LONG"
        elif rsi_value > 70:
            direction = "SHORT"
            
        # If no condition met, return None (no signal)
        if not direction:
            return None
        
        sl_dist = atr_value * Config.ATR_MULTIPLIER_SL
        
        entry_price = current_price
        
        if direction == "LONG":
            stop_loss = entry_price - sl_dist
            tp_factors = [1, 2, 3]
        else: # SHORT
            stop_loss = entry_price + sl_dist
            tp_factors = [-1, -2, -3]
        
        tp_levels = []
        for ratio in Config.RISK_REWARD_RATIOS:
            # Adjust ratio sign for Short
            r = ratio if direction == "LONG" else -ratio
            tp_price = entry_price + (atr_value * r)
            tp_levels.append(tp_price)

        return {
            "symbol": symbol,
            "direction": direction,
            "entry": entry_price,
            "sl": stop_loss,
            "tps": tp_levels,
            "atr": atr_value,
            "rsi": rsi_value,
            "timestamp": latest['timestamp']
        }
