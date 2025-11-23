import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    # Default to Binance if not specified, but can be changed
    EXCHANGE_ID = os.getenv("EXCHANGE_ID", "binance")
    
    # Trading defaults
    DEFAULT_TIMEFRAME = "1h"
    DEFAULT_LIMIT = 100  # Number of candles to fetch
    
    # ATR Settings
    ATR_PERIOD = 14
    ATR_MULTIPLIER_SL = 1.5
    
    # Scanner Settings
    SYMBOLS_TO_SCAN = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    SCAN_INTERVAL = 3600 # 1 hour in seconds
    ADMIN_ID = int(os.getenv("362508830", "0")) # Replace with your User ID or set in .env
    
    # Risk Management
    RISK_REWARD_RATIOS = [1.0, 2.0, 3.0] # TP1, TP2, TP3 multipliers
