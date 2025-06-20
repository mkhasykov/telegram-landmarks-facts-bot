"""
Configuration module for Telegram Location Bot.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Optional: Webhook configuration
    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")
    PORT: int = int(os.getenv("PORT", "8080"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
            
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
            
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    @classmethod
    def setup_logging(cls) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                # Add file handler if needed
                # logging.FileHandler('bot.log')
            ]
        )


# Configuration validation
try:
    Config.validate()
    Config.setup_logging()
except ValueError as e:
    print(f"Configuration error: {e}")
    print("\nPlease ensure the following environment variables are set:")
    print("- TELEGRAM_BOT_TOKEN=your_telegram_bot_token")
    print("- OPENAI_API_KEY=your_openai_api_key")
    print("\nOptional environment variables:")
    print("- OPENAI_MODEL=gpt-4.1-mini (default)")
    print("- DEBUG=false")
    print("- LOG_LEVEL=INFO")
    print("- WEBHOOK_URL=your_webhook_url (for production)")
    exit(1) 