import asyncio
import pandas as pd
import numpy as np
from app.services.market_data import MarketDataService
from app.services.signal_analysis import SignalAnalysisService
from config import Config

async def run_backtest(symbol="BTC/USDT", days=30):
    print(f"[START] Starting Backtest for {symbol} over last {days} days...")
    
    market_service = MarketDataService()
    
    # Fetch enough data (assuming 1h timeframe, 24 candles per day)
    limit = days * 24
    # ccxt limit might be capped (e.g. 1000), so we might need pagination in a real robust backtester.
    # For now, let's try to fetch the max allowed or a reasonable amount.
    # Binance usually allows 1000 candles. 30 days * 24h = 720 candles. So 1000 is enough.
    
    print("[INFO] Fetching historical data...")
    df = await market_service.fetch_ohlcv(symbol, limit=1000)
    await market_service.close()
    
    if df is None or df.empty:
        print("[ERROR] Failed to fetch data.")
        return

    print(f"[INFO] Analyzing {len(df)} candles...")
    
    # Initial Balance
    initial_balance = 1000
    balance = initial_balance
    trades = []
    wins = 0
    losses = 0
    
    # Iterate through data
    # We need a window for ATR/RSI, so start after period
    start_idx = 50 
    
    for i in range(start_idx, len(df) - 1):
        # Slice data up to current point to simulate "live"
        current_df = df.iloc[:i+1].copy()
        
        # Generate Signal
        signal = SignalAnalysisService.generate_signal(symbol, current_df)
        
        if signal and "error" not in signal:
            # We have a signal!
            # Let's simulate the trade outcome
            entry_price = signal['entry']
            sl_price = signal['sl']
            tp1_price = signal['tps'][0] # Aiming for TP1 for simplicity in this basic backtest
            direction = signal['direction']
            
            # Look ahead at future candles to see what happened
            outcome = None
            pnl = 0
            
            # Check next candles until SL or TP is hit
            for j in range(i + 1, len(df)):
                future_candle = df.iloc[j]
                high = future_candle['high']
                low = future_candle['low']
                
                if direction == "LONG":
                    # Check SL first (conservative)
                    if low <= sl_price:
                        outcome = "LOSS"
                        pnl = -10 # Assume $10 risk (1%)
                        break
                    if high >= tp1_price:
                        outcome = "WIN"
                        pnl = 10 * Config.RISK_REWARD_RATIOS[0] # Reward based on R:R
                        break
                elif direction == "SHORT":
                    if high >= sl_price:
                        outcome = "LOSS"
                        pnl = -10
                        break
                    if low <= tp1_price:
                        outcome = "WIN"
                        pnl = 10 * Config.RISK_REWARD_RATIOS[0]
                        break
            
            if outcome:
                balance += pnl
                trades.append({
                    "date": signal['timestamp'],
                    "type": direction,
                    "entry": entry_price,
                    "outcome": outcome,
                    "pnl": pnl
                })
                if outcome == "WIN": wins += 1
                else: losses += 1
                
                # Skip ahead to where trade closed to avoid overlapping trades (simple logic)
                # In reality you can have multiple trades, but let's keep it simple
                # We won't actually skip 'i' in the main loop easily without a while loop, 
                # but since we only take one trade at a time logic, let's just ignore signals if we were "in a trade".
                # For this simple script, we'll just log every signal as if we took it, 
                # which might be unrealistic if signals are frequent.
                # A better way:
                # We can't easily skip 'i' here. Let's just print the trade.
                pass

    # Report
    print("\n" + "="*30)
    print("BACKTEST RESULTS")
    print("="*30)
    print(f"Symbol: {symbol}")
    print(f"Period: Last {len(df)} hours")
    print(f"Initial Balance: ${initial_balance}")
    print(f"Final Balance:   ${balance:.2f}")
    print(f"Total Trades:    {len(trades)}")
    print(f"Wins:            {wins}")
    print(f"Losses:          {losses}")
    if len(trades) > 0:
        print(f"Win Rate:        {(wins/len(trades))*100:.2f}%")
    print("="*30)
    
    # Show last 5 trades
    if trades:
        print("\nLast 5 Trades:")
        for t in trades[-5:]:
            print(f"{t['date']} | {t['type']} | {t['outcome']} | ${t['pnl']:.2f}")

if __name__ == "__main__":
    asyncio.run(run_backtest())
