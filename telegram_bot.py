from typing import Final
from utils import load_env_variable, inference, get_logger
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from flask import Flask, request
import logging

logger = get_logger(__name__)

# Load environment variables
TOKEN: Final = load_env_variable("TELEGRAM_TOKEN")
BOT_USERNAME: Final = load_env_variable("TELEGRAM_USERNAME")
PORT = int(load_env_variable("PORT", 8443))

# Telegram Bot Application
application = Application.builder().token(TOKEN).build()


# Define commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi, I'm Nail Shop Service assistant! How can I help you?")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! I'm here to help you shine. Need to book an appointment, check our services, "
        "or get quick answers about your nail care? I've got you covered.\n"
        "Your beauty, our passion! ✨"
    )


def hande_response(prompt):
    try:
        logger.info(f"Generating response for prompt: {prompt}")
        response = inference(prompt=prompt)
        logger.info(f"Response generated!")
        return response
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return f"An error occurred: {e}"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    user_message = update.message.text

    logger.info(f"User ({update.message.chat.id}) in {message_type}: {user_message}.")

    if message_type == "group" and BOT_USERNAME in user_message:
        prompt: str = user_message.replace(f"{BOT_USERNAME} ", "").strip()
        response: str = hande_response(prompt)
    elif message_type != "group":
        response = hande_response(user_message)
    else:
        return

    logger.info(f"Response: {response}")
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}")


# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT, handle_message))
application.add_error_handler(error)

# Flask app for webhook
app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook requests from Telegram."""
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.update_queue.put(update)
    return "OK", 200


if __name__ == "__main__":
    logger.info("Starting bot...")

    # Set webhook URL
    WEBHOOK_URL = f"https://nailshoptelegram.onrender.com/webhook"
    application.bot.set_webhook(WEBHOOK_URL)

    # Run Flask app
    app.run(host="0.0.0.0", port=PORT)
