import os
import asyncio
import signal
import logging
import sys
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from aiohttp import web

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token and webhook configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7971247491:AAF1Z9RleXBjp0NBDvF7g3Eh7qA3bq9Ac9I")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://your-app.onrender.com
PORT = int(os.getenv("PORT", 8443))  # Render provides PORT, fallback to 8443 for local testing

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

# Webhook Handler
async def webhook(request):
    app = request.app["telegram_app"]
    try:
        update = Update.de_json(await request.json(), app.bot)
        if update:
            await app.process_update(update)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return web.Response(status=500)

# Shutdown Handler
async def shutdown(application):
    logger.info("Shutting down bot...")
    try:
        await application.stop()
        await application.shutdown()
        logger.info("Bot shutdown complete.")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")

# Setup Webhook Server
async def setup_webhook(app, webhook_url, token):
    logger.info(f"Setting up webhook: {webhook_url}/{token}")
    await app.bot.set_webhook(url=f"{webhook_url}/{token}")

# Main Function
async def main():
    # Build application
    telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    telegram_app.add_handler(CommandHandler("price", price))
    telegram_app.add_handler(CommandHandler("volume", volume))
    telegram_app.add_handler(CommandHandler("marketcap", marketcap))
    telegram_app.add_handler(CommandHandler("stats", stats))
    telegram_app.add_handler(CommandHandler("help", help_cmd))

    # Initialize Telegram application
    try:
        logger.info("Initializing Telegram application...")
        await telegram_app.initialize()
    except Exception as e:
        logger.error(f"Initialize error: {str(e)}")
        raise

    # Create aiohttp web app
    web_app = web.Application()
    web_app["telegram_app"] = telegram_app
    web_app.router.add_post(f"/{BOT_TOKEN}", webhook)

    # Setup webhook
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL environment variable not set.")
        sys.exit(1)
    await setup_webhook(telegram_app, WEBHOOK_URL, BOT_TOKEN)

    # Handle shutdown signals
    def handle_shutdown(loop):
        logger.info("Received shutdown signal.")
        tasks = [task for task in asyncio.all_tasks(loop) if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        asyncio.create_task(shutdown(telegram_app))
        loop.stop()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        sys.exit(0)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_shutdown, loop)
        except NotImplementedError:
            logger.warning(f"Signal handler for {sig} not supported.")

    # Start web server
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    logger.info(f"Starting web server on port {PORT}...")
    await site.start()

    try:
        # Keep the bot running
        await telegram_app.run_async()
    except asyncio.CancelledError:
        logger.info("Application cancelled.")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
    finally:
        await shutdown(telegram_app)
        await runner.cleanup()

if __name__ == "__main__":
    try:
        logger.info("Starting bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}")
        sys.exit(1)
