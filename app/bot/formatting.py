def format_signal_message(signal_data: dict) -> str:
    if not signal_data or "error" in signal_data:
        return "⚠️ **Error generating signal.**"

    symbol = signal_data['symbol']
    direction = signal_data['direction']
    entry = signal_data['entry']
    sl = signal_data['sl']
    tps = signal_data['tps']
    atr = signal_data['atr']
    rsi = signal_data.get('rsi', 0)
    
    # Formatting numbers
    def fmt(val):
        return f"{val:.4f}" if val < 10 else f"{val:.2f}"

    msg = (
        f"📊 **Trading Signal: {symbol}**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"**Direction:** {direction}\n"
        f"**Entry:** `{fmt(entry)}`\n"
        f"**ATR:** `{fmt(atr)}` | **RSI:** `{fmt(rsi)}`\n\n"
        
        f"🛑 **Stop-Loss:** `{fmt(sl)}`\n\n"
        
        f"🎯 **Take-Profit 1:** `{fmt(tps[0])}`\n"
        f"🎯 **Take-Profit 2:** `{fmt(tps[1])}`\n"
        f"🎯 **Take-Profit 3:** `{fmt(tps[2])}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ _Trade at your own risk._"
    )
    return msg
