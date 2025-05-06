import os
import asyncio
import signal
import logging
import sys
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token (from environment or hardcoded fallback)
BOT_TOKEN = os.getenv("BOT_TOKEN", "7971247491:AAF1Z9RleXBjp0NBDvF7g3Eh7qA3bq9Ac9I")

# Dexscreener API URL
PAIR_URL = "https://api.dexscreener.com/latest/dex/pairs/bsc/0x68214c06d83a78274bb30598bf4aead0f8995657"

# Fetch data from Dexscreener
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

# Command Handlers
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "*CrumbSwap Bot Commands*\n\n"
        "💰 `/price` - Current CRUMB token price\n"
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
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not fetch stats: {str(e)}")
        logger.error(f"Stats error: {str(e)}")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await asyncio.to_thread(get_data)
        await update.message.reply_text(format_price(data), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not fetch price: {str(e)}")
        logger.error(f"Price error: {str(e)}")

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await asyncio.to_thread(get_data)
        await update.message.reply_text(format_volume(data), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not fetch volume: {str(e)}")
        logger.error(f"Volume error: {str(e)}")

async def marketcap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await asyncio.to_thread(get_data)
        await update.message.reply_text(format_marketcap(data), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not fetch market cap: {str(e)}")
        logger.error(f"Marketcap error: {str(e)}")

# Shutdown Handler
async def shutdown(application):
    logger.info("Shutting down bot...")
    try:
        await application.stop()
        await application.shutdown()
        logger.info("Bot shutdown complete.")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")

# Main Function
async def main():
    # Build application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("volume", volume))
    app.add_handler(CommandHandler("marketcap", marketcap))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_cmd))

    # Initialize application
    try:
        logger.info("Initializing application...")
        await app.initialize()
    except Exception as e:
        logger.error(f"Initialize error: {str(e)}")
        raise

    # Handle shutdown signals
    def handle_shutdown(loop):
        logger.info
