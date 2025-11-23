import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession

from config import Config
from app.services.market_data import MarketDataService
from app.services.signal_analysis import SignalAnalysisService
from app.bot.formatting import format_signal_message
from app.services.scanner import ScannerService

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    # Check for PythonAnywhere proxy
    session = None
    proxy_url = os.getenv("http_proxy")
    if proxy_url:
        logging.info(f"🚀 Running on PythonAnywhere (Proxy detected: {proxy_url})")
        session = AiohttpSession(proxy=proxy_url)

    # Initialize Bot with proxy session if needed
    bot = Bot(token=Config.BOT_TOKEN, session=session)
    dp = Dispatcher()

    # --- Command Handlers ---
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer(
            f"👋 Hello! I am your Trading Bot.\n"
            f"Your ID is: `{message.from_user.id}` (Put this in config.py)\n\n"
            f"Commands:\n"
            f"/signal <symbol> - Get manual signal (e.g. /signal BTC/USDT)"
        )

    @dp.message(Command("signal"))
    async def cmd_signal(message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.answer("⚠️ Usage: /signal <symbol>\nExample: `/signal BTC/USDT`")
            return
        
        symbol = args[1].upper()
        await message.answer(f"🔍 Analyzing {symbol}...")
        
        try:
            market_service = MarketDataService()
            df = await market_service.fetch_ohlcv(symbol)
            await market_service.close()
            
            if df is None:
                await message.answer(f"❌ Error fetching data for {symbol}")
                return
                
            signal = SignalAnalysisService.generate_signal(symbol, df)
            response = format_signal_message(signal)
            await message.answer(response, parse_mode="Markdown")
            
        except Exception as e:
            logging.error(f"Error processing signal: {e}")
            await message.answer("❌ An error occurred while analyzing.")

    # --- Start Scanner ---
    # Pass the bot instance to the scanner so it can send messages
    scanner = ScannerService(bot)
    asyncio.create_task(scanner.start())

    # Start Polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not Config.BOT_TOKEN:
        print("Error: BOT_TOKEN is not set in config.py or environment variables.")
    else:
        asyncio.run(main())
