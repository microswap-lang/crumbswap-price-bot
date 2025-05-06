import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7971247491:AAF1Z9RleXBjp0NBDvF7g3Eh7qA3bq9Ac9I"

PAIR_URL = "https://api.dexscreener.com/latest/dex/pairs/bsc/0x68214c06d83a78274bb30598bf4aead0f8995657"

def get_data():
    res = requests.get(PAIR_URL)
    return res.json()["pair"]

# Formatters
def format_price(data):
    return f"💰 *Price:* `${float(data['priceUsd']):.6f}`"

def format_volume(data):
    return f"📊 *24h Volume:* `${float(data['volume']['h24']):,.0f}`"

def format_marketcap(data):
    return f"🏦 *Market Cap:* `${float(data['fdv']):,.0f}`"

def format_change(data):
    change = float(data["priceChange"]["h24"])
    emoji = "🔺" if change >= 0 else "🔻"
    return f"{emoji} *24h Change:* `{change:+.2f}%`"

# Bot command handlers
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "*CrumbSwap Bot Commands*\n\n"
        "💰 `/price` - Current CRUMB token price + 24h change\n"
        "📊 `/volume` - 24h trading volume\n"
        "🏦 `/marketcap` - Market cap\n"
        "📈 `/stats` - Full CRUMB stats\n"
        "ℹ️ `/help` - Show this list"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await asyncio.to_thread(get_data)
        msg = (
            f"*CRUMB Stats*\n\n"
            f"{format_price(data)}\n"
            f"{format_change(data)}\n"
            f"{format_volume(data)}\n"
            f"{format_marketcap(data)}\n\n"
            f"🔗 [View on Dexscreener]({PAIR_URL})"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except:
        await update.message.reply_text("⚠️ Could not fetch stats.")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await asyncio.to_thread(get_data)
        await update.message.reply_text(format_price(data), parse_mode="Markdown")
    except:
        await update.message.reply_text("⚠️ Could not fetch price.")

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await asyncio.to_thread(get_data)
        await update.message.reply_text(format_volume(data), parse_mode="Markdown")
    except:
        await update.message.reply_text("⚠️ Could not fetch volume.")

async def marketcap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await asyncio.to_thread(get_data)
        await update.message.reply_text(format_marketcap(data), parse_mode="Markdown")
    except:
        await update.message.reply_text("⚠️ Could not fetch market cap.")

# Main application
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("volume", volume))
    app.add_handler(CommandHandler("marketcap", marketcap))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

