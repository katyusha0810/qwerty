import asyncio
import logging
from aiogram import Bot
from config import Config
from app.services.market_data import MarketDataService
from app.services.signal_analysis import SignalAnalysisService
from app.bot.formatting import format_signal_message

class ScannerService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.market_service = MarketDataService()
        self.is_running = False

    async def start_scanning(self):
        self.is_running = True
        logging.info("🚀 Scanner started...")
        
        while self.is_running:
            try:
                for symbol in Config.SYMBOLS_TO_SCAN:
                    logging.info(f"🔍 Scanning {symbol}...")
                    df = await self.market_service.fetch_ohlcv(symbol)
                    
                    if df is not None:
                        signal = SignalAnalysisService.generate_signal(symbol, df)
                        
                        if signal and "error" not in signal:
                            logging.info(f"✅ Signal found for {symbol}!")
                            msg = format_signal_message(signal)
                            
                            if Config.ADMIN_ID != 0:
                                try:
                                    await self.bot.send_message(Config.ADMIN_ID, msg, parse_mode="Markdown")
                                except Exception as e:
                                    logging.error(f"Failed to send message to admin: {e}")
                            else:
                                logging.warning("⚠️ Signal found but ADMIN_ID is not set in config.")
                        else:
                            logging.info(f"No signal for {symbol}.")
                    
                    # Small delay between symbols to avoid rate limits
                    await asyncio.sleep(2)
                
                logging.info(f"💤 Sleeping for {Config.SCAN_INTERVAL} seconds...")
                await asyncio.sleep(Config.SCAN_INTERVAL)
                
            except Exception as e:
                logging.error(f"Error in scanner loop: {e}")
                await asyncio.sleep(60) # Wait a bit before retrying on error

    async def stop(self):
        self.is_running = False
        await self.market_service.close()
