import ccxt.async_support as ccxt
import pandas as pd
import asyncio
from config import Config

class MarketDataService:
    def __init__(self):
        self.exchange_id = Config.EXCHANGE_ID
        self.exchange_class = getattr(ccxt, self.exchange_id)
        self.exchange = self.exchange_class()

    async def close(self):
        await self.exchange.close()

    async def fetch_ohlcv(self, symbol: str, timeframe: str = None, limit: int = None):
        """
        Fetches OHLCV data for a given symbol.
        """
        if timeframe is None:
            timeframe = Config.DEFAULT_TIMEFRAME
        if limit is None:
            limit = Config.DEFAULT_LIMIT

        try:
            # ccxt returns: [timestamp, open, high, low, close, volume]
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv:
                return None

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
