"""
Main application module for Telegram Location Bot.
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.config import Config
from src.bot_handlers import BotHandlers

# Setup logging
logger = logging.getLogger(__name__)


class TelegramLocationBot:
    """Main Telegram Location Bot class."""
    
    def __init__(self) -> None:
        """Initialize the bot."""
        self.config = Config()
        self.handlers = BotHandlers()
        
        # Create application
        self.application = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
        
        # Setup handlers
        self._setup_handlers()
        
    def _setup_handlers(self) -> None:
        """Setup bot handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handlers.start_command))
        self.application.add_handler(CommandHandler("help", self.handlers.help_command))
        
        # Location handler (main functionality)
        self.application.add_handler(MessageHandler(filters.LOCATION, self.handlers.handle_location))
        
        # Handle unsupported messages
        self.application.add_handler(MessageHandler(~filters.LOCATION & ~filters.COMMAND, 
                                                  self.handlers.unsupported_message))
        
        # Error handler
        self.application.add_error_handler(self.handlers.error_handler)
        
    def run(self) -> None:
        """Run the bot."""
        logger.info("Starting Telegram Location Bot...")
        
        if self.config.WEBHOOK_URL:
            # Production mode with webhook
            logger.info(f"Running in webhook mode on {self.config.WEBHOOK_URL}")
            self.application.run_webhook(
                listen="0.0.0.0",
                port=self.config.PORT,
                webhook_url=self.config.WEBHOOK_URL
            )
        else:
            # Development mode with polling
            logger.info("Running in polling mode...")
            # НЕ использовать asyncio.run() - python-telegram-bot управляет event loop самостоятельно
            self.application.run_polling()


def main() -> None:
    """Main entry point."""
    try:
        bot = TelegramLocationBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main() 