import os
import requests
import asyncio
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Set your group/channel/chat ID here

PAIR_URL = "https://api.dexscreener.com/latest/dex/pairs/bsc/0x68214c06d83a78274bb30598bf4aead0f8995657"

async def fetch_price():
    try:
        response = requests.get(PAIR_URL)
        data = response.json()["pair"]

        price = float(data["priceUsd"])
        volume = float(data["volume"]["h24"])
        market_cap = float(data["fdv"])  # FDV = fully diluted value (used as market cap)

        message = (
            f"💰 *CRUMB Price Update*\n"
            f"• Price: `${price:.6f}`\n"
            f"• 24h Volume: `${volume:,.0f}`\n"
            f"• Market Cap: `${market_cap:,.0f}`\n\n"
            f"🔗 [View on Dexscreener]({PAIR_URL})"
        )

        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

    except Exception as e:
        print("Error fetching or sending price update:", e)

async def main():
    while True:
        await fetch_price()
        await asyncio.sleep(3600)  # wait 1 hour

if __name__ == "__main__":
    asyncio.run(main())

