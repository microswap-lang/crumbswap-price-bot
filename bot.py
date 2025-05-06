import os
import requests
import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Optional for manual replies

PAIR_URL = "https://api.dexscreener.com/latest/dex/pairs/bsc/0x68214c06d83a78274bb30598bf4aead0f8995657"

def format_price_message(data):
    price = float(data["priceUsd"])
    volume = float(data["volume"]["h24"])
    market_cap = float(data["fdv"])

    return (
        f"💰 *CRUMB Price Update*\n"
        f"• Price: `${price:.6f}`\n"
        f"• 24h Volume: `${volume:,.0f}`\n"
        f"• Market Cap: `${market_cap:,.0f}`\n\n"
        f"🔗 [View on Dexscreener]({PAIR_URL})"
    )

async def fetch_data():
    response = requests.get(PAIR_URL)
    return response.json()["pair"]

# Manual command handler
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await asyncio.to_thread(fetch_data)
        message = format_price_message(data)
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("⚠️ Error fetching price.")

# Auto hourly posting
async def auto_post(bot: Bot):
    while True:
        try:
            data = await asyncio.to_thread(fetch_data)
            message = format_price_message(data)
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        except Exception as e:
            print("Auto-post error:", e)
        await asyncio.sleep(3600)

# Main app
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("price", price_command))

    bot = Bot(token=BOT_TOKEN)
    asyncio.create_task(auto_post(bot))

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())


