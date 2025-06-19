"""
Bot handlers for Telegram Location Bot.
"""

import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from src.location_service import LocationService

logger = logging.getLogger(__name__)


class BotHandlers:
    """Handles Telegram bot interactions."""
    
    def __init__(self) -> None:
        """Initialize bot handlers."""
        self.location_service = LocationService()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        welcome_message = (
            f"Привет, {user.first_name}! 👋\n\n"
            "Я бот, который рассказывает интересные факты о местах рядом с вашей геолокацией.\n\n"
            "📍 Просто отправьте мне свою локацию, и я найду что-то интересное поблизости!\n\n"
            "Используйте /help для получения дополнительной информации."
        )
        
        await update.message.reply_text(welcome_message)
        logger.info(f"User {user.id} ({user.username}) started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_message = (
            "🤖 *Телеграм-бот \"Факты о месте\"*\n\n"
            "Как пользоваться:\n"
            "📍 Отправьте мне свою геолокацию через кнопку \"Поделиться локацией\"\n"
            "🔍 Я найду интересную достопримечательность поблизости\n"
            "📖 Расскажу вам необычный факт об этом месте\n\n"
            "*Команды:*\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать эту справку\n\n"
            "*Примечание:* Бот работает только с геолокацией. "
            "Текстовые сообщения не поддерживаются."
        )
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
        logger.info(f"User {update.effective_user.id} requested help")
    
    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle location messages - main bot functionality."""
        user = update.effective_user
        location = update.message.location
        
        logger.info(
            f"Received location from user {user.id} ({user.username}): "
            f"lat={location.latitude}, lon={location.longitude}"
        )
        
        # Send initial response
        processing_message = await update.message.reply_text(
            "🔍 Ищу интересное место рядом с вами...\n"
            "⏳ Это может занять несколько секунд."
        )
        
        try:
            # Process location and get interesting fact
            result = await self.location_service.process_location(
                latitude=location.latitude,
                longitude=location.longitude,
                user_id=user.id
            )
            
            if result:
                # Format and send response
                response_message = self._format_location_response(result)
                await processing_message.edit_text(response_message, parse_mode='Markdown')
                
                logger.info(f"Successfully processed location for user {user.id}")
            else:
                # No interesting place found
                await processing_message.edit_text(
                    "😔 К сожалению, я не смог найти интересные достопримечательности "
                    "рядом с вашим местоположением.\n\n"
                    "Попробуйте отправить локацию из другого места!"
                )
                logger.warning(f"No interesting places found for user {user.id}")
                
        except Exception as e:
            logger.error(f"Error processing location for user {user.id}: {e}")
            await processing_message.edit_text(
                "❌ Произошла ошибка при обработке вашей локации.\n\n"
                "Пожалуйста, попробуйте еще раз через несколько минут."
            )
    
    async def unsupported_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unsupported message types."""
        await update.message.reply_text(
            "🤖 Я работаю только с геолокацией!\n\n"
            "📍 Пожалуйста, отправьте мне свою локацию через кнопку "
            "\"Поделиться локацией\" в меню вложений.\n\n"
            "Используйте /help для получения дополнительной информации."
        )
        
        logger.info(f"User {update.effective_user.id} sent unsupported message type")
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Send error message to user if possible
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла непредвиденная ошибка.\n"
                "Пожалуйста, попробуйте еще раз."
            )
    
    def _format_location_response(self, result: dict) -> str:
        """Format the location processing result for user."""
        place_name = result.get('place_name', 'Неизвестное место')
        distance = result.get('distance', 0)
        fact = result.get('interesting_fact', 'Информация недоступна')
        
        # Distance formatting
        if distance < 1:
            distance_str = f"{int(distance * 1000)} м"
        else:
            distance_str = f"{distance:.1f} км"
        
        response = (
            f"🏛️ *{place_name}*\n"
            f"📍 Расстояние: ~{distance_str}\n\n"
            f"💡 *Интересный факт:*\n"
            f"{fact}"
        )
        
        return response 