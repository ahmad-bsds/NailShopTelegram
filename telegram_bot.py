from typing import Final
from utils import load_env_variable, inference, get_logger
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logger = get_logger(__name__)

TOKEN: Final = load_env_variable("TELEGRAM_TOKEN")
BOT_USERNAME: Final = load_env_variable("TELEGRAM_USERNAME")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hi, I'm Nail Shop Service assistant! How can I help you?")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        """
        Welcome! I'm here to help you shine. Need to book an appointment, check our services,\
        or get quick answers about your nail care? I've got you covered.\
        From gel polish to acrylics, manicures to pedicures,\
        just ask and I'll make sure you get the perfect nail experience. Your beauty, our passion! ✨
        
        """
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
    """
    Check if someone calling bot in the group then give it response.
    :param update:
    :param context:
    :return: string text
    """
    message_type = update.message.chat.type
    user_message = update.message.text

    logger.info(f"User ({update.message.chat.id}) in {message_type}: {user_message}.")

    if message_type == "group":
        if BOT_USERNAME in user_message:
            prompt: str = user_message.replace(f"{BOT_USERNAME} ", "").strip()
            response: str = hande_response(prompt)
        else:
            return
    else:
        response = hande_response(user_message)

    logger.info(f"Response: {response}")

    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    logger.info("Starting bot...")
    application = Application.builder().token(TOKEN).build()

    # Commands
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help_command)

    # Messages
    message_handler = MessageHandler(filters.TEXT, handle_message)

    # Handlers
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(message_handler)

    # Log Errors
    application.add_error_handler(error)

    # Run
    logger.info("Pooling...")
    application.run_polling(poll_interval=5)
