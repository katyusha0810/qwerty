import pandas as pd
from app.services.signal_analysis import SignalAnalysisService
from app.bot.formatting import format_signal_message

def test_signal_generation():
    # Create mock data
    data = {
        'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='H'),
        'open': [100] * 100,
        'high': [105] * 100,
        'low': [95] * 100,
        'close': [100] * 100,
        'volume': [1000] * 100
    }
    df = pd.DataFrame(data)
    
    # Add some volatility to make ATR non-zero
    import numpy as np
    np.random.seed(42)
    df['close'] = df['close'] + np.random.normal(0, 2, 100)
    df['high'] = df['close'] + 2
    df['low'] = df['close'] - 2
    
    print("Testing Signal Generation...")
    # Force RSI to be low (Oversold) to trigger LONG
    # We need a downtrend for RSI to be low
    df['close'] = np.linspace(100, 80, 100) 
    # Add noise
    df['close'] = df['close'] + np.random.normal(0, 0.5, 100)
    
    signal = SignalAnalysisService.generate_signal("BTC/USDT", df)
    
    if signal and "error" not in signal:
        print("\n[SUCCESS] Signal Generated Successfully:")
        print(f"Direction: {signal['direction']}")
        print(f"Entry: {signal['entry']}")
        print(f"SL: {signal['sl']}")
        print(f"TPs: {signal['tps']}")
        print(f"ATR: {signal['atr']}")
        print(f"RSI: {signal['rsi']}")
        
        print("\nTesting Formatting:")
        msg = format_signal_message(signal)
        try:
            print(msg)
        except UnicodeEncodeError:
            print("[Formatted message contains emojis, cannot print to console directly]")
    else:
        print("[FAILED] Failed to generate signal (Condition might not be met)")
        if signal:
            print(signal)

if __name__ == "__main__":
    test_signal_generation()
