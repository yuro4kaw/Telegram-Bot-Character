import logging
import os
from dotenv import load_dotenv
from PyCharacterAI import get_client
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

# Load environment variables
load_dotenv()

CHARACTER_AI_TOKEN = os.getenv("CHARACTER_AI_TOKEN")
CHARACTER_AI_WEB_NEXT_AUTH = os.getenv("CHARACTER_AI_WEB_NEXT_AUTH")
CHARACTER_ID = os.getenv("CHARACTER_ID")
VOICE_ID = os.getenv("VOICE_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_COMMAND = os.getenv("BOT_COMMAND")


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

@dp.message(Command(commands=BOT_COMMAND))
async def cmd_vova(m: Message):
    char_client = await get_client(token=CHARACTER_AI_TOKEN)

    msg_parts = m.text.split()

    if len(msg_parts) < 2:
        await m.answer(
            "Будь ласка, напишіть своє повідомлення після команди. Наприклад:\n\n"
            f"<code>/{BOT_COMMAND} Як твої справи</code>"
        )
        return

    await bot.send_chat_action(chat_id=m.chat.id, action=ChatAction.RECORD_VOICE)

    message_text = " ".join(msg_parts[1:])
    message_text = f"Добрий день, я {m.from_user.full_name} {message_text}"
    chat, greeting_message = await char_client.chat.create_chat(CHARACTER_ID)

    answer = await char_client.chat.send_message(CHARACTER_ID, chat.chat_id, message_text)
    # answer_text = answer.get_primary_candidate().text

    await bot.send_chat_action(chat_id=m.chat.id, action=ChatAction.RECORD_VOICE)

    speech = await char_client.utils.generate_speech(
        chat.chat_id,
        answer.turn_id,
        answer.primary_candidate_id,
        VOICE_ID
    )

    await m.answer_voice(
        BufferedInputFile(speech, filename="Відповідь.mp3"),
        reply_to_message_id=m.message_id
    )

def main():
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)

if __name__ == "__main__":
    main()
