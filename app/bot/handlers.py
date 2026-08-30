import asyncio
import logging

from aiogram import F, Router
from aiogram.types import Message

from app.search.router import handle_message

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "/start")
async def start(message: Message) -> None:
    await message.answer(
        "היי! אני עוזר חיפוש מחירים בישראל.\n"
        "שלח לי מה אתה מחפש ואיפה, למשל:\n"
        "\"חלב 3% בתל אביב\" או \"iPhone 17 128GB בחיפה עד 4000 שקל\"."
    )


@router.message(F.text)
async def on_text(message: Message) -> None:
    await message.bot.send_chat_action(message.chat.id, "typing")
    try:
        reply = await asyncio.to_thread(handle_message, message.text)
    except Exception:
        logger.exception("Failed to handle message: %s", message.text)
        reply = "משהו השתבש בחיפוש. נסה שוב בעוד רגע."
    await message.answer(reply)
