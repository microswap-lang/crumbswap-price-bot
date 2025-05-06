import os
import requests
import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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

# Commands
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

# Auto update
async def auto_post(bot: Bot):
    while True:
        try:
            data = await asyncio.to_thread(get_data)
            msg = (
                f"📈 *CRUMB Live Update*\n"
                f"{format_price(data)}\n"
                f"{format_volume(data)}\n"
                f"{format_marketcap(data)}\n\n"
                f"🔗 [View on Dexscreener]({PAIR_URL})"
            )
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
        except Exception as e:
            print("Auto post error:", e)
        await asyncio.sleep(3600)

# Main
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("volume", volume))
    app.add_handler(CommandHandler("marketcap", marketcap))

    bot = Bot(token=BOT_TOKEN)
    asyncio.create_task(auto_post(bot))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())


