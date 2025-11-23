import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import Config
from app.services.market_data import MarketDataService
from app.services.signal_analysis import SignalAnalysisService
from app.bot.formatting import format_signal_message

from app.services.scanner import ScannerService

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Bot and Dispatcher
bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

market_service = MarketDataService()
scanner_service = ScannerService(bot)

@dp.startup()
async def on_startup(bot: Bot):
    # Start the scanner in the background
    asyncio.create_task(scanner_service.start_scanning())

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    await message.answer(f"👋 **Welcome to the Trading Bot!**\n\nYour User ID is: `{user_id}`\n(Copy this to ADMIN_ID in config.py to receive alerts)\n\nUse `/signal <symbol>` to get a trade setup manually.")

@dp.message(Command("signal"))
async def cmd_signal(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Usage: `/signal <symbol>` (e.g., `/signal BTC/USDT`)")
        return

    symbol = args[1].upper()
    await message.answer(f"🔍 Fetching data for **{symbol}**...")

    # Fetch Data
    df = await market_service.fetch_ohlcv(symbol)
    
    if df is None:
        await message.answer(f"❌ Could not fetch data for {symbol}. Check the symbol or exchange.")
        return

    # Analyze
    signal = SignalAnalysisService.generate_signal(symbol, df)
    
    # Format and Send
    response = format_signal_message(signal)
    await message.answer(response, parse_mode="Markdown")

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await market_service.close()

if __name__ == "__main__":
    if not Config.BOT_TOKEN:
        print("Error: BOT_TOKEN is not set in config.py or environment variables.")
    else:
        asyncio.run(main())
