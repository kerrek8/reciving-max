import asyncio
import logging

from app.bot import bot
from app.config import CHAT_ID
from app.utils import parse_message
from app.storage import threads, save_threads

queue: asyncio.Queue = asyncio.Queue()

def resolve_entity(sender: dict):
    chat_id = str(sender.get("chatId"))
    sender_name = sender.get("senderName", "Unknown")
    chat_name = sender.get("chatName", "Unknown")

    # если это группа
    if chat_name and chat_name != sender_name:
        return chat_id, chat_name  # используем группу

    return chat_id, sender_name  # личка

async def get_or_create_thread(chat_id: str, sender_name: str):
    if chat_id in threads:
        return threads[chat_id]

    topic = await bot.create_forum_topic(
        chat_id=CHAT_ID,
        name=f"{sender_name} | {chat_id}"
    )

    thread_id = topic.message_thread_id

    threads[chat_id] = thread_id
    save_threads(threads)

    return thread_id


async def send_with_retry(func, retries=3):
    for attempt in range(retries):
        try:
            await func()
            return True
        except Exception as e:
            logging.error(f"Send failed (attempt {attempt+1}): {e}")
            await asyncio.sleep(5)
    return False


async def worker():
    while True:
        payload = await queue.get()

        try:
            msg = parse_message(payload)

            sender = payload.get("senderData", {})

            chat_id, display_name = resolve_entity(sender)

            thread_id = await get_or_create_thread(chat_id, display_name)

            # TEXT
            if msg["type"] == "text":
                await send_with_retry(lambda: bot.send_message(
                    chat_id=CHAT_ID,
                    message_thread_id=thread_id,
                    text=msg["text"],
                    parse_mode="HTML"
                ))

            # PHOTO
            elif msg["type"] == "photo":
                await send_with_retry(lambda: bot.send_photo(
                    chat_id=CHAT_ID,
                    message_thread_id=thread_id,
                    photo=msg["url"],
                    caption=msg["text"],
                    parse_mode="HTML"
                ))

            # VIDEO
            elif msg["type"] == "video":
                await send_with_retry(lambda: bot.send_video(
                    chat_id=CHAT_ID,
                    message_thread_id=thread_id,
                    video=msg["url"],
                    caption=msg["text"],
                    parse_mode="HTML"
                ))

            else:
                await send_with_retry(lambda: bot.send_message(
                    chat_id=CHAT_ID,
                    message_thread_id=thread_id,
                    text=msg["text"]
                ))

        except Exception as e:
            logging.exception(f"Worker error: {e}")

        finally:
            queue.task_done()