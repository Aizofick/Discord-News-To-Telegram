import asyncio
import disnake
from disnake.ext import commands
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BufferedInputFile, InputMediaPhoto, InputMediaDocument
import aiohttp

DISCORD_TOKEN = 'MTQwMjY5Njk0NTk3NzM5MzM4Nw.GMsgNT.SMJOu0YAuweFZGA7Z7oJm-tXgBYX57E3V-Swh8'
TELEGRAM_TOKEN = '8002779012:AAE4l_ysL9n9hu5MceXvIgztkh2YXyL10c0'

TELEGRAM_CHAT_ID = -1002388165108
TELEGRAM_THREAD_ID = 61933

DISCORD_CHANNEL_IDS = {
    1402689963920851017,
    1402970013094248531,
    1402969653399261259,
    1402968654345408565,
}

intents = disnake.Intents.default()
intents.message_content = True
discord_bot = commands.Bot(command_prefix="!", intents=intents)

bot = Bot(token=TELEGRAM_TOKEN, timeout=60, session=AiohttpSession())

sent_messages_ids = set()

@discord_bot.event
async def on_ready():
    print(f'Discord бот запущен как {discord_bot.user}')

@discord_bot.event
async def on_message(message: disnake.Message):
    if message.author == discord_bot.user:
        return

    if message.channel.id in DISCORD_CHANNEL_IDS:
        if message.id in sent_messages_ids:
            return

        username = message.author.name
        content = message.content or ""
        text_to_send = f"📢Пост от {username}:\n{content}"

        photos = []
        documents = []

        async with aiohttp.ClientSession() as session:
            for attachment in message.attachments:
                file_name = attachment.filename
                try:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            file_bytes = await resp.read()
                            input_file = BufferedInputFile(file_bytes, filename=file_name)

                            if attachment.content_type and attachment.content_type.startswith("image"):
                                photos.append(InputMediaPhoto(media=input_file))
                            else:
                                documents.append(InputMediaDocument(media=input_file))
                        else:
                            print(f"Не удалось скачать файл {file_name} с Discord, статус {resp.status}")
                except Exception as e:
                    print(f"Ошибка при скачивании файла {file_name}: {e}")

        try:
            if photos:
                photos[0] = InputMediaPhoto(
                    media=photos[0].media,
                    caption=text_to_send,
                    parse_mode=ParseMode.HTML
                )
                await bot.send_media_group(
                    chat_id=TELEGRAM_CHAT_ID,
                    media=photos,
                    message_thread_id=TELEGRAM_THREAD_ID
                )
                if documents:
                    await bot.send_media_group(
                        chat_id=TELEGRAM_CHAT_ID,
                        media=documents,
                        message_thread_id=TELEGRAM_THREAD_ID
                    )
            else:
                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=text_to_send,
                    message_thread_id=TELEGRAM_THREAD_ID,
                    parse_mode=ParseMode.HTML
                )
                if documents:
                    await bot.send_media_group(
                        chat_id=TELEGRAM_CHAT_ID,
                        media=documents,
                        message_thread_id=TELEGRAM_THREAD_ID
                    )

            sent_messages_ids.add(message.id)
        except Exception as e:
            print(f"Ошибка при отправке сообщения в Telegram: {e}")

    await discord_bot.process_commands(message)

async def main():
    print("Запускаем Discord и Telegram ботов")
    await discord_bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа остановлена вручную")
